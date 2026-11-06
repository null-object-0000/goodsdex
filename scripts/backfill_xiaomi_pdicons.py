"""Local image-only candidate and directory gap audit; never publishes.

Read the external APK table without modifying it. curl validates candidate PNGs;
Pillow decodes their actual dimensions. ProductCompact batches never exceed 20.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import urllib.request
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.xiaomi_covers import apply_pdicons, PDICON_BASE
from PIL import Image

API = 'https://home.mi.com/cgi-op/api/v1/productCompact'
ROOT = Path('docs/pdicon-covers-20261106')
MAP = Path('data/official/xiaomi-pdid-map.json')


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def compact(batch):
    assert len(batch) <= 20
    req = urllib.request.Request(API, data=json.dumps(batch).encode(),
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=35) as r:
            return dict(models=batch, http_status=r.status, response=json.load(r))
    except Exception as exc:
        return dict(models=batch, error=str(exc))


def check_image(url):
    with tempfile.TemporaryDirectory(prefix='pdicon-') as tmp:
        path = Path(tmp) / 'image'
        p = subprocess.run(['curl', '-L', '-sS', '--retry', '1', '--max-time', '25',
                            '-o', str(path), '-w', '%{http_code}\n%{content_type}', url],
                           capture_output=True, text=True)
        parts = p.stdout.splitlines()
        out = dict(image=url, http_status=int(parts[0]) if parts and parts[0].isdigit() else None,
                   content_type=parts[1] if len(parts) > 1 else None, width=None, height=None)
        if p.returncode:
            out['error'] = p.stderr.strip()
        try:
            with Image.open(path) as im:
                im.load()
                out.update(width=im.width, height=im.height,
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        except Exception as exc:
            out.setdefault('error', str(exc))
        out['usable'] = (out['http_status'] == 200
                         and (out['content_type'] or '').startswith('image/')
                         and (out['width'] or 0) >= 400 and (out['height'] or 0) >= 400)
        return out


def unsigned(url):
    return urlsplit(url or '')._replace(query='', fragment='').geturl()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--table', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--reuse', action='store_true')
    a = ap.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    raw = a.input.read_bytes()
    if a.input.suffix == '.gz':
        raw = gzip.decompress(raw)
    rows = json.loads(raw)
    table_bytes = a.table.read_bytes()
    table = json.loads(gzip.decompress(table_bytes))['result']['devices']['list']
    local = {r['model']: r for r in table}
    assert len(table) == len(local), 'Ambiguous duplicate model in local table'
    models = sorted({r['miio_model'] for r in rows if r.get('miio_model')})
    response_path = ROOT / 'product-compact-responses.json'
    responses = json.loads(response_path.read_text()) if response_path.exists() else []
    queried = {m for b in responses if b.get('http_status') == 200
               and b.get('response', {}).get('code') == 0 for m in b['models']}
    # Compare all published models as well as resolving missing identities.
    pending = sorted(set(models) - queried)
    if pending and not a.reuse:
        batches = [pending[i:i+20] for i in range(0, len(pending), 20)]
        with ThreadPoolExecutor(max_workers=6) as pool:
            responses.extend(pool.map(compact, batches))
        write(response_path, responses)
    online = {}
    for b in responses:
        if b.get('http_status') == 200 and b.get('response', {}).get('code') == 0:
            for r in b['response'].get('data', {}).get('list', []):
                if r.get('model') in b['models'] and type(r.get('pdId')) is int and r['pdId'] > 0:
                    online[r['model']] = r
    mappings = {}
    for model in models:
        if model in local:
            mappings[model] = dict(pd_id=local[model]['pd_id'], pd_id_source='local_table')
        elif model in online:
            mappings[model] = dict(pd_id=online[model]['pdId'], pd_id_source='product_compact')
    # Audit only this patch, without replaying unrelated frozen store covers.
    candidates = [r for r in rows if r.get('miio_model') in mappings
                  and not str(r.get('image_source', '')).startswith('mijia_baike')]
    sample = random.Random(20261106).sample(sorted(candidates, key=lambda r:r['id']), 30)
    urls = sorted({PDICON_BASE + str(mappings[r['miio_model']]['pd_id']) + '.png' for r in candidates})
    checks_path = ROOT / 'url-checks.json'
    checks = json.loads(checks_path.read_text()) if checks_path.exists() else {}
    unchecked = sorted(set(urls) - checks.keys())
    if unchecked and a.reuse:
        raise ValueError('Missing URL checks; run without --reuse')
    if unchecked:
        with ThreadPoolExecutor(max_workers=20) as pool:
            checks.update(zip(unchecked, pool.map(check_image, unchecked)))
        write(checks_path, checks)
    for entry in mappings.values():
        check = checks.get(PDICON_BASE + str(entry['pd_id']) + '.png')
        # Only a successfully validated candidate URL enables image replay.
        entry.update(usable=bool(check and check['usable']))
        if check:
            entry.update({k:check[k] for k in ('width', 'height', 'http_status')})
    write(MAP, mappings)
    after = apply_pdicons(rows, mappings)
    # Compare the pdicon patch to its input, independently of existing cover replay.
    assert apply_pdicons(after, mappings) == after
    for before, out in zip(rows, after):
        assert {k:v for k,v in before.items() if not k.startswith('image')} == {k:v for k,v in out.items() if not k.startswith('image')}
    changes = [dict(id=b['id'], model=b.get('miio_model'),
                    before={k:v for k,v in b.items() if k.startswith('image')},
                    after={k:v for k,v in o.items() if k.startswith('image')})
               for b,o in zip(rows,after) if b != o]
    (ROOT / 'cover-changes.json.gz').write_bytes(gzip.compress(json.dumps(changes,ensure_ascii=False).encode(),mtime=0))
    audit = []
    for r in after:
        model = r.get('miio_model')
        if not model:
            continue
        e = mappings.get(model, {})
        url = PDICON_BASE + str(e['pd_id']) + '.png' if e else None
        c = checks.get(url, {})
        audit.append(dict(id=r['id'], model=model, pd_id=e.get('pd_id'),
                          pd_id_source=e.get('pd_id_source'), image=url,
                          selected_image=r.get('image'), http_status=c.get('http_status'),
                          width=c.get('width'), height=c.get('height'),
                          selected_source=r.get('image_source'),
                          validation='passed' if c.get('usable') else ('failed_retained_original' if c else 'not_tested_baike_preferred')))
    write(Path('data/official/pdicon-audit.json'), audit)
    sampled = [dict(id=r['id'], model=r['miio_model'], **checks[PDICON_BASE+str(mappings[r['miio_model']]['pd_id'])+'.png']) for r in sample]
    write(ROOT/'sample-30.json', sampled)
    failures = [dict(id=r['id'], model=r['miio_model'], **checks[PDICON_BASE+str(mappings[r['miio_model']]['pd_id'])+'.png']) for r in candidates if not mappings[r['miio_model']]['usable']]
    write(ROOT/'failures.json', failures)
    mismatches = [dict(model=m, name=local[m]['name'], local_pd_id=local[m]['pd_id'],
                       product_compact_pd_id=online[m]['pdId'], local_icon=unsigned(local[m]['icon_real']),
                       product_compact_icon=unsigned(online[m].get('realIcon')))
                  for m in models if m in local and m in online
                  and unsigned(local[m]['icon_real']) != unsigned(online[m].get('realIcon'))]
    write(ROOT/'icon-comparison.json', dict(compared=len(set(local)&online.keys()),mismatches=mismatches))
    groups = defaultdict(list)
    for r in table:
        groups[r.get('cate_name') or '未分类'].append(r)
    stats = [dict(category=c, have=sum(r['model'] in models for r in rs), total=len(rs),
                  missing=sum(r['model'] not in models for r in rs)) for c,rs in sorted(groups.items())]
    write(ROOT/'gap-summary.json', stats)
    md = ['# 米家目录型号缺口', '', '以 APK 表的唯一 model 为分母，与发布集中所有非空 miio_model 精确匹配；不按品牌/status 过滤，不将缺口自动视为应补采商品。', '', '|cate_name|已有型号|表内型号|覆盖率|缺口|', '|---|---:|---:|---:|---:|']
    for s in stats:
        md.append(f"|{s['category']}|{s['have']}|{s['total']}|{s['have']/s['total']:.2%}|{s['missing']}|")
    md += ['', '## 家电专项', '', '按表内 model 的设备类型段精确归组；cate_name 为宽类，以下只是型号目录缺口，不代表参数覆盖率。空调包括 airc/aircondition（目录中也含控制器），扫地机沿用 vacuum 类型（目录中也含擦窗机）。电热水器仅取 waterheater 且官方 name 明含“电热水”的条目；不推断燃料种类。微波炉沿用 microwave 类型，不推断 oven 里的微蒸烤机；风扇不含 light 类型的风扇灯。完整缺口仍全部列于 cate_name 节。', '']
    kinds={'空调':{'airc','aircondition'},'扫地机':{'vacuum'},'冰箱':{'fridge'},'洗衣机':{'washer'},'微波炉':{'microwave'},'洗碗机':{'dishwasher'},'电热水器':{'waterheater'},'风扇':{'fan'}}
    def listing(rs):
        return ['|model|name|pd_id|','|---|---|---:|']+[f"|{r['model']}|{r['name'].replace('|','/')}|{r['pd_id']}|" for r in sorted(rs,key=lambda r:r['model']) if r['model'] not in models]
    for kind, tokens in kinds.items():
        rs=[r for r in table if len(r['model'].split('.'))==3 and r['model'].split('.')[1] in tokens
            and (kind != '电热水器' or '电热水' in r['name'])]
        have=sum(r['model'] in models for r in rs)
        md += [f'### {kind}：{have}/{len(rs)}，缺 {len(rs)-have}', ''] + listing(rs) + ['']
    md += ['## 按 cate_name 的完整缺口', '']
    for cat, rs in sorted(groups.items()):
        md += [f'### {cat}', ''] + listing(rs) + ['']
    (ROOT/'mihome-gap.md').write_text('\n'.join(md))
    report=dict(baseline_sha256=hashlib.sha256(raw).hexdigest(),table_sha256=hashlib.sha256(table_bytes).hexdigest(),
                rows=len(rows),with_model=len(audit),unique_models=len(models),table_rows=len(table),
                map_entries=len(mappings),map_sources=dict(Counter(e['pd_id_source'] for e in mappings.values())),
                image_changed_sources=dict(Counter(o.get('image_source','unspecified') for b,o in zip(rows,after) if b.get('image')!=o.get('image'))),
                pdicon_rows=sum(r.get('image_source')=='mijia_pdicon' for r in after),
                checked_urls=len(checks),failed_records=len(failures),sample_passed=sum(r['usable'] for r in sampled),
                gap_have=sum(s['have'] for s in stats),gap_total=len(table),
                gap_missing=sum(s['missing'] for s in stats),non_image_fields_unchanged=True,idempotent=True)
    write(ROOT/'report.json',report)
    a.output.write_text(json.dumps(after,ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

if __name__ == '__main__':
    main()
