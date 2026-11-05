#!/usr/bin/env python3
"""Repeatable bounded lane collection and strict published-row coverage report."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from goodsdex.release_coverage import apply_priority_dates, matrix, effective

FILES = {'L1':'hp-release-evidence.json','L2':'atour-release-evidence.json',
         'L3':'xiaomi-priority-release-evidence.json','L4':'priority-series-release-evidence.json'}
MODULES = {'L1':'hp','L2':'atour','L3':'xiaomi','L4':'series'}


def run_lane(lane, rows, directory, live):
    target = ROOT/'data/official'/FILES[lane]
    if not live and lane != 'L4' and target.exists():
        return json.loads(target.read_text())
    module = importlib.import_module('release_lane_' + MODULES[lane])
    if lane == 'L1':
        result = module.run(rows, directory/lane, live=live, cache_paths=[ROOT/'docs/hp-history-20261105/support-evidence.json.gz', ROOT/'docs/release-coverage/l1-hp/supplemental-support.json'])
    elif lane == 'L2':
        result = module.run(rows, directory/lane, live=live,
            capture_path=ROOT/'docs/release-coverage/l2-atour/live-capture.json' if not live else None)
    else:
        result = module.run(rows, directory/lane, live=live)
    target = ROOT/'data/official'/FILES[lane]
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result


def report(before, after, results, directory, provenance):
    b, a = matrix(before), matrix(after)
    now = datetime.now(timezone.utc)
    lines = ['# 发布时间覆盖率 '+now.date().isoformat(), '',
        f'快照：{provenance}；{len(before)} 个发布行（包含历史留档，不按商品族合并）。',
        '仅 day / month；网页首存和 LLM 估算不计。系列继承最多月，保留来源范围。',
        '后值为本次采集与所有已审 sidecar 的共同重放；各线增量不冒充单品命中。',
        'none 默认「可得未取到」（待采集，不保证确实可得）；只有明确官方否认并留证才叫「官方无此信息」。', '',
        '| 优先品类 | 前 | 后 | 命中率（前 → 后） |','|---|---:|---:|---:|']
    for g, c in a['priority'].items():
        old=b['priority'].get(g,dict(covered=0,total=0,ratio=0))
        lines.append(f"| {g} | {old['covered']}/{old['total']} | {c['covered']}/{c['total']} | {old['ratio'] or 0:.1%} → {c['ratio'] or 0:.1%} |")
    lines += ['', '| 品牌 | day | month | none | 可得未取到 | 官方无此信息 |', '|---|---:|---:|---:|---:|---:|']
    for brand, c in a['brands'].items():
        lines.append(f"| {brand} | {c['day']} | {c['month']} | {c['none']} | {c['not_obtained']} | {c['official_absent']} |")
    lines += ['', f"全库前：{b['total']}；后：{a['total']}", '', '## 四线结果']
    for lane,result in sorted(results.items()):
        lines += [f"- {lane}: `{json.dumps(result.get('summary',{}),ensure_ascii=False)}`"]
    samples=[]
    candidates=sorted((r for r in after if effective(r)),key=lambda r:(not bool(r.get('release_inherited')),r['id']))
    seen=set()
    for row in candidates:
        r=effective(row);e=r.get('evidence') or {};key=(r['date'],e.get('url'))
        if key in seen: continue
        seen.add(key)
        samples.append(dict(id=row['id'],name=row.get('name'),date=r['date'],precision=r['granularity'],
            url=e.get('url'),quote=e.get('quote'),why='精确系列成员继承，截到证据月份；非SKU上市日' if r.get('release_source')=='series_inherit' or r.get('source')=='series_inherit' else '来源明示年月日' if r['granularity']=='day' else '来源支持月份；不填未知日',market=r.get('market')))
        if len(samples)==10:break
    lines += ['', '## 10条可复核日期样本']
    for s in samples:
        lines += [f"- {s['id']} · {s['name']} · {s['date']} ({s['precision']}) · {s['why']} · market={s['market']}\n  {s['url']}\n  原文：{s['quote']}"]
    directory.mkdir(parents=True,exist_ok=True)
    (directory/(str(now.date())+'.md')).write_text('\n'.join(lines)+'\n')
    (directory/'coverage.json').write_text(json.dumps(dict(before=b,after=a,provenance=provenance),ensure_ascii=False,indent=2)+'\n')
    (directory/'samples.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lane',choices=[*FILES,'all'],default='all')
    p.add_argument('--goods',type=Path)
    p.add_argument('--output',type=Path,default=ROOT/'docs/release-coverage')
    p.add_argument('--no-live',action='store_true',help='Replay existing captures explicitly')
    p.add_argument('--apply',action='store_true',help='Append dates to --goods (CI candidate baseline)')
    args=p.parse_args()
    if args.goods:
        raw=args.goods.read_bytes(); provenance=str(args.goods)
    else:
        url='https://raw.githubusercontent.com/null-object-0000/goodsdex/data/public/goods.json'
        with urllib.request.urlopen(url,timeout=90) as response:raw=response.read()
        provenance=url
    provenance += '; sha256='+hashlib.sha256(raw).hexdigest()
    before=json.loads(raw)
    lanes=list(FILES) if args.lane=='all' else [args.lane]
    args.output.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=len(lanes)) as pool:
        jobs={lane:pool.submit(run_lane,lane,before,args.output,not args.no_live) for lane in lanes}
        results={lane:job.result() for lane,job in jobs.items()}
    after=apply_priority_dates(before)
    report(before,after,results,args.output,provenance)
    if args.apply:
        if not args.goods:raise ValueError('--apply requires --goods')
        args.goods.write_text(json.dumps(after,ensure_ascii=False,indent=1)+'\n')
    print(json.dumps(matrix(after)['total'],ensure_ascii=False))

if __name__=='__main__':main()
