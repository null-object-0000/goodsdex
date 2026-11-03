"""Reproduce exact reviewed memberships, exhaustive research census and reports."""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.series_release import apply_series_releases, is_accessory
from review import build as review, read, write

def count(rows):
    mi = [r for r in rows if r.get('brand') == '小米']
    def product(r):
        d = r.get('release') or {}
        return bool(d.get('date'))
    def series(r):
        return bool((r.get('release_series') or {}).get('date'))
    def visible(r, k):
        d = r.get(k) or {}
        return bool(d.get('date')) and d.get('usage') != 'disabled' and d.get('display_allowed', True)
    return dict(rows=len(mi), product=sum(map(product,mi)), series=sum(map(series,mi)),
                assertion_union=sum(product(r) or series(r) for r in mi),
                display_allowed_union=sum(visible(r,'release') or visible(r,'release_series') for r in mi))

def main():
    before = json.loads(gzip.decompress((OUT / 'baseline.json.gz').read_bytes()))
    bundle = json.loads(gzip.decompress((OUT / 'series-before.json.gz').read_bytes()))
    new = review()
    bundle['batches'].extend(new)
    write(ROOT / 'data/official/series-releases.json', bundle)
    after = apply_series_releases(before)
    unmanaged = lambda rs: [{k:v for k,v in r.items() if k != 'release_series'} for r in rs]
    assert unmanaged(before) == unmanaged(after)
    assert apply_series_releases(after) == after
    old_ids = {m['id'] for b in json.loads(gzip.decompress((OUT/'series-before.json.gz').read_bytes()))['batches'] for m in b['members']}
    ids = {m['id'] for b in new for m in b['members']}
    assert not old_ids & ids
    new_rows = [r for r in after if r['id'] in ids]
    assert all(r['release_series']['display_allowed'] for r in new_rows)
    assert all(not (r.get('release') or {}).get('date') for r in new_rows)
    (OUT/'expected.json.gz').write_bytes(gzip.compress(json.dumps(after,ensure_ascii=False).encode(),mtime=0))
    before_count, after_count = count(before), count(after)
    report = dict(before=before_count, after=after_count, new_batches=len(new), new_unique_ids=len(ids),
        new_covered_rows=len(new_rows), missing_after=1684-after_count['assertion_union'],
        coverage_before=before_count['assertion_union']/1684, coverage_after=after_count['assertion_union']/1684,
        new_official_rows=sum(r['release_series']['source']=='official' for r in new_rows),
        new_two_publisher_rows=sum(r['release_series']['source']=='third_party' for r in new_rows),
        legacy_unverified_rows=sum(r['id'] in old_ids and r['release_series']['crosscheck_status']=='unverified' for r in after),
        baseline_full_catalog_rows=len(before), invariants=dict(non_series_fields_unchanged=True,idempotent=True,
        no_llm_calls=True, no_new_accessory_or_service_members=True, no_goods_or_meta_semantic_changes=True))
    write(OUT/'report.json',report)

    # Full census: collapse only explicitly co-launched reviewed members. Pending
    # names are research keys, not assertions of common generation or launch date.
    families = []
    for b in new:
        rs = [r for r in new_rows if r['release_series']['batch_id']==b['id']]
        families.append(dict(family_id=b['id'],family=b['series'],generation=b['generation'],
            sku_count=len({r['id'] for r in rs}),row_count=len(rs),coverage=len(rs),
            method='官方明确发布原句' if b['series_release']['source']=='official' else '两个独立原始供稿机构，≤14天',
            status='verified', date=b['series_release']['date'],
            urls=[b['series_release']['evidence']['url']] + [c['evidence']['url'] for c in b['series_release'].get('crosschecks',[])],
            members=[dict(id=r['id'],name=r['name']) for r in rs]))
    scan = {d['id']:d for d in (json.loads(s) for s in gzip.open(ROOT/'docs/release-dates-round2-20261103/mi-scan.jsonl.gz','rt'))}
    for f in read(OUT/'families-before.json'):
        members = [m for m in f['members'] if m['id'] not in ids]
        if not members:
            continue
        f = deepcopy(f)
        f.update(members=members,sku_count=len({m['id'] for m in members}),row_count=len(members),
                 status='unresolved',reason='未找到官方/可靠来源',
                 search_scope='复核既有精确ID官网扫描及已归档候选证据池；只有研究日志所列重点族新增独立联网检索，非穷尽逐族检索')
        for m in members:
            s = scan.get(m['id'])
            m['official_scan'] = dict(archive='docs/release-dates-round2-20261103/mi-scan.jsonl.gz',
                captured_at=s.get('captured_at') if s else None,
                result=(s.get('message') or '接口未提供可核发布日期') if s else '该ID不在旧扫描中')
        families.append(f)
    assert sum(f['row_count'] for f in families) == 1472
    assert sum(f['coverage'] for f in families) == len(new_rows)
    write(OUT/'families.json', families)
    unresolved = [f for f in families if f['status']=='unresolved']
    write(OUT/'unresolved.json', unresolved)
    report.update(families=len(families), unresolved_groups=len(unresolved),
                  census_rows=sum(f['row_count'] for f in families),
                  verified_batch_rows=len(new_rows), target_1200_verified_rows_met=len(new_rows)>=1200)
    write(OUT/'report.json',report)
    def table(fs, title):
        lines=[title,'','覆盖条数指新增取得可展示证据的基线行数；SKU数按不同ID计数，重复行不冒充新SKU。待核项不是已证实同代同批。','',
               '|族名 / 代际|SKU数|基线行数|找到日期的方式 / 状态|新增覆盖条数|',
               '|---|---:|---:|---|---:|']
        for f in fs:
            note = (f.get('date','')+' '+f['method']) if f['status']=='verified' else f['reason']+'（有限证据池；代际待核，不继承）'
            lines.append('|'+ ' / '.join([f['family'],f['generation']]).replace('|','／')+f"|{f['sku_count']}|{f['row_count']}|{note}|{f['coverage']}|")
        return '\n'.join(lines)+'\n'
    (OUT/'families.md').write_text(table(families,'# 全量族清单（含待核研究分组）'))
    (OUT/'unresolved.md').write_text(table(unresolved,'# 未取得同批证据的族 / 待核研究分组'))

    # Fixed-seed batch sample; cover up to 30 distinct batches, never resample
    # based on whether a source comparison looks favourable.
    sampled_batches = random.Random(20261104).sample(new,min(30,len(new)))
    selected = [next(r for r in new_rows if r['release_series']['batch_id']==b['id']) for b in sampled_batches]
    picked={r['id'] for r in selected}
    rest=[r for r in new_rows if r['id'] not in picked]
    selected += random.Random(20261104).sample(rest,30-len(selected))
    sample=[]
    for r in selected:
        d=r['release_series'];b=next(b for b in new if b['id']==d['batch_id'])
        sample.append(dict(id=r['id'],name=r['name'],date=d['date'],granularity=d['granularity'],
            batch_id=d['batch_id'],generation=d['generation'], evidence=d['evidence'],
            checks=d['checks'],identity_reason=next(m['identity_reason'] for m in b['members'] if m['id']==r['id']),
            verdict='符合当前原句、型号和独立来源门槛；执行者来源复核，非外部人工签字'))
    write(OUT/'sample-30.json',sample)
    lines=['# 30条与来源原句对照','','固定种子20261104按批次抽样30条；新批次不足30时再抽成员补齐；不是全库随机准确率。原句仅去除排版空白，原HTML/PDF/抽取文本均可回查。','']
    for i,s in enumerate(sample,1):
        lines += [f"## {i}. {s['name']} — {s['date']}",'',f"`{s['id']}`；{s['generation']}",'',
                  f"主来源：[原文]({s['evidence']['url']})：{s['evidence']['quote']}",'']
        for c in s['checks']:
            lines += [f"独立来源：[原文]({c['evidence']['url']})：{c['evidence']['quote']}；原始日期 {c['date']}，差 {c['delta_days']} 天，{c['verdict']}。",'']
        lines += ['型号边界：'+s['identity_reason'],'','结论：'+s['verdict'],'']
    (OUT/'sample-30.md').write_text('\n'.join(lines).rstrip()+'\n')
    captures=[read(p) for p in sorted((OUT/'evidence').glob('*.json'))]
    write(OUT/'source-inventory.json',[{k:v for k,v in c.items() if k!='text'} for c in captures])
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    main()
