#!/usr/bin/env python3
"""Repeatable bounded lane collection and strict published-row coverage report."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import gzip
import importlib
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from goodsdex.release_coverage import apply_priority_dates, matrix, effective

FILES = {'L1':'hp-release-evidence.json','L2':'atour-release-evidence.json',
         'L3':'xiaomi-priority-release-evidence.json','L4':'priority-series-release-evidence.json','L5':'l5-release-evidence.json','L6':'l6-release-evidence.json','L7':'l7-release-evidence.json'}
MODULES = {'L1':'hp','L2':'atour','L3':'xiaomi','L4':'series','L5':'media','L6':'structured'}


def run_lane(lane, rows, directory, live, full=False):
    if lane == 'L7':
        from goodsdex.release_l7 import apply
        after=apply(rows)
        return {'summary':{'changed':sum(a!=b for a,b in zip(rows,after)), 'mode':'reviewed_capture_revalidation'}}
    target = ROOT/('data/third-party' if lane in ('L5','L6') else 'data/official')/FILES[lane]
    if not live and lane not in ('L4', 'L5','L6') and target.exists():
        return json.loads(target.read_text())
    module = importlib.import_module('release_lane_' + MODULES[lane])
    if lane == 'L1':
        result = module.run(rows, directory/lane, live=live, cache_paths=[ROOT/'docs/hp-history-20261105/support-evidence.json.gz', ROOT/'docs/release-coverage/l1-hp/supplemental-support.json'])
    elif lane == 'L2':
        result = module.run(rows, directory/lane, live=live,
            capture_path=ROOT/'docs/release-coverage/l2-atour/live-capture.json' if not live else None)
    elif lane in ('L5','L6'):
        official_rows = apply_priority_dates(rows, [ROOT/'data/official'/FILES[key] for key in ('L1','L2','L3','L4')])
        result = module.run(official_rows, directory/lane, live=live, **({'full':full} if lane=='L6' else {}))
    elif lane == 'L3':
        result = module.run_all(rows, directory/'l3-xiaomi/full', live=live)
    else:
        result = module.run(rows, directory/lane, live=live)
    target = ROOT/('data/third-party' if lane in ('L5','L6') else 'data/official')/FILES[lane]
    temporary = target.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(target)
    return result


def report(before, after, results, directory, provenance):
    b, a = matrix(before), matrix(after)
    now = datetime.now(timezone.utc)
    lines = ['# 发布时间覆盖率 '+now.date().isoformat(), '',
        f'快照：{provenance}；{len(before)} 个发布行（包含历史留档，不按商品族合并）。',
        '仅 day / month；网页首存和 LLM 估算不计。系列继承最多月，保留来源范围。',
        'none 默认「可得未取到」（待采集，不保证确实可得）；只有明确官方否认并留证才叫「官方无此信息」。', '',
        '| 优先品类 | 前 | 后 | 命中率（前 → 后） |','|---|---:|---:|---:|']
    for g, c in a['priority'].items():
        old=b['priority'].get(g,dict(covered=0,total=0,ratio=0))
        lines.append(f"| {g} | {old['covered']}/{old['total']} | {c['covered']}/{c['total']} | {old['ratio'] or 0:.1%} → {c['ratio'] or 0:.1%} |")
    lines += ['', '| 品牌 | day 前→后 | month 前→后 | none 前→后 | official | third_party | series_inherit |', '|---|---:|---:|---:|---:|---:|---:|']
    for brand, c in a['brands'].items():
        old=b["brands"].get(brand,{"day":0,"month":0,"none":0})
        lines.append(f"| {brand} | {old['day']}→{c['day']} | {old['month']}→{c['month']} | {old['none']}→{c['none']} | {c['official']} | {c['third_party']} | {c['series_inherit']} |")
    lines += ['', f"全库有效覆盖：{b['total']['covered']}/{b['total']['total']} ({b['total']['ratio']:.1%}) → {a['total']['covered']}/{a['total']['total']} ({a['total']['ratio']:.1%})，净增 {a['total']['covered']-b['total']['covered']} 行。",
        '', f"全库前：{b['total']}；后：{a['total']}",
        '', '初始快照 day=0：旧管线将产品日期统一存到月；系列继承也一律截到月。原文出现具体日不代表已有产品级日精度记录。',
        '本轮只在精确产品身份和官方事件原文明示日期时新增 day；系列公告仍只继承 month，不能把新闻发布时间或系列发布日冒充配置首售日。',
        '', '## 采集线结果']
    for lane,result in sorted(results.items()):
        lines += [f"- {lane}: `{json.dumps(result.get('summary',{}),ensure_ascii=False)}`"]
    if 'L6' in results:
        from release_lane_structured import append_report
        append_report(lines, before, after, results['L6'], directory)
    if 'L3' in results:
        l3_only = matrix(apply_priority_dates(before, [ROOT/'data/official'/FILES['L3']]))
        lines += ['', f"L3 命中数包含已有日期复核；单独应用 L3 的净新增有效覆盖为 {l3_only['total']['covered']-b['total']['covered']} 行，其余为复核或精度提升。"]
    samples=[]
    before_dates = {r['id']: effective(r) for r in before}
    candidates=sorted((r for r in after if effective(r) and effective(r) != before_dates.get(r['id'])
                       and effective(r).get('evidence', {}).get('source_type') == 'official'),
                      key=lambda r:(effective(r)['granularity'] != 'day', r['id']))
    seen=set()
    for row in candidates:
        r=effective(row);e=r.get('evidence') or {};key=row['id']
        if key in seen: continue
        seen.add(key)
        samples.append(dict(id=row['id'],name=row.get('name'),date=r['date'],precision=r['granularity'],
            url=e.get('url'),quote='\n[…]\n'.join(fragment[:550].rstrip() for fragment in (e.get('quote') or '').split('\n[…]\n')),why='精确系列成员继承，截到证据月份；非SKU上市日' if r.get('release_source')=='series_inherit' or r.get('source')=='series_inherit' else '来源明示年月日' if r['granularity']=='day' else '来源支持月份；不填未知日',market=r.get('market')))
        if len(samples)==10:break
    lines += ['', '## 10条本轮新增或精度提升的可复核日期样本']
    for s in samples:
        lines += [f"- {s['id']} · {s['name']} · {s['date']} ({s['precision']}) · {s['why']} · market={s['market']}\n  {s['url']}\n  原文：{s['quote']}"]
    if 'L5' in results:
        from release_lane_media_report import append_report
        append_report(lines, before, after, results['L5'], directory)
    notes = ROOT/'docs/release-coverage/report-notes.md'
    if notes.exists():
        lines += ['', notes.read_text()]
    directory.mkdir(parents=True,exist_ok=True)
    (directory/(str(now.date())+'.md')).write_text('\n'.join(lines).rstrip()+'\n')
    (directory/'coverage.json').write_text(json.dumps(dict(before=b,after=a,provenance=provenance),ensure_ascii=False,indent=2)+'\n')
    (directory/'samples.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lane',choices=[*FILES,'all'],default='all')
    p.add_argument('--goods',type=Path)
    p.add_argument('--output',type=Path,default=ROOT/'docs/release-coverage')
    p.add_argument('--no-live',action='store_true',help='Replay existing captures explicitly')
    p.add_argument('--l6-full',action='store_true',help='Explicitly expand L6 after the committed 300-gid pilot')
    p.add_argument('--apply',action='store_true',help='Append dates to --goods (CI candidate baseline)')
    args=p.parse_args()
    if args.goods:
        raw=args.goods.read_bytes(); provenance=str(args.goods)
    else:
        url='https://raw.githubusercontent.com/null-object-0000/goodsdex/data/public/goods.json'
        with urllib.request.urlopen(url,timeout=90) as response:raw=response.read()
        provenance=url
    if raw.startswith(b'\x1f\x8b'):
        raw = gzip.decompress(raw)
    provenance += '; sha256='+hashlib.sha256(raw).hexdigest()
    before=json.loads(raw)
    lanes=list(FILES) if args.lane=='all' else [args.lane]
    args.output.mkdir(parents=True,exist_ok=True)
    # L5 consumes official evidence, so wait for L1-L4 writes before evaluating it.
    official_lanes = [lane for lane in lanes if lane not in ('L5','L6')]
    results = {}
    if official_lanes:
        with ThreadPoolExecutor(max_workers=len(official_lanes)) as pool:
            jobs={lane:pool.submit(run_lane,lane,before,args.output,not args.no_live) for lane in official_lanes}
            results={lane:job.result() for lane,job in jobs.items()}
    if 'L5' in lanes:
        results['L5'] = run_lane('L5',before,args.output,not args.no_live)
    if 'L6' in lanes:
        results['L6'] = run_lane('L6',apply_priority_dates(before),args.output,not args.no_live,full=args.l6_full)
    after=apply_priority_dates(before)
    report(before,after,results,args.output,provenance)
    from release_tolerance_run import report as tolerance_report
    tolerance_report(before, after, args.output)
    if args.apply:
        if not args.goods:raise ValueError('--apply requires --goods')
        args.goods.write_text(json.dumps(after,ensure_ascii=False,indent=1)+'\n')
    print(json.dumps(matrix(after)['total'],ensure_ascii=False))

if __name__=='__main__':main()
