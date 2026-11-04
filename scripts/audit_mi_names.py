#!/usr/bin/env python3
"""Resumable Xiaomi title audit, serial requests separated by >=2.15 seconds."""
import argparse, collections, difflib, gzip, html, json, random, re, sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_source_urls import fetch

def compare(old, new):
    if old == new: return 'exact'
    norm=lambda x: re.sub(r'\s+', '', x).casefold()
    a,b=norm(old),norm(new)
    if a==b: return 'format_only'
    if b in a: return 'database_extra'
    if a in b: return 'database_missing'
    if difflib.SequenceMatcher(None,a,b).ratio()<.45: return 'unrelated'
    # Mixed changes require explicit inspection; never label them as exact.
    return 'changed_review'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('docs/name-fidelity-20261104'));ap.add_argument('--targeted',action='store_true');a=ap.parse_args();root=a.root
    rows=json.loads(gzip.decompress((root/'baseline-goods.json.gz').read_bytes()))
    mi=list({r['id']:r for r in rows if r['id'].startswith('CN:mi_cn:product:')}.values())
    sample=random.Random(20261104).sample(sorted(mi,key=lambda r:r['id']),200)
    plan=root/'sample-plan.json';plan.write_text(json.dumps(sample,ensure_ascii=False,indent=1)+'\n')
    results_path=root/'titles.jsonl'; results=[json.loads(l) for l in results_path.read_text().splitlines()] if results_path.exists() else []
    done={r['id'] for r in results}; folder=root/'responses';folder.mkdir(exist_ok=True)
    sample_ids={r['id'] for r in sample}
    # Random sample remains unbiased; required case studies run separately.
    priority=[r for r in mi if r['id'].rsplit(':',1)[-1] in ('22104','22105','22547','23722')]
    queue=sample+[r for r in priority if r['id'] not in sample_ids]
    if a.targeted:
        keyword=json.loads((root/'accessory-keyword-before.json').read_text())
        groups=json.loads(gzip.decompress((root/'all-same-name-groups-before.json.gz').read_bytes()))
        ids={r['id'] for r in keyword}
        ids.update(r['id'] for g in groups for r in g['rows'] if r['id'].startswith('CN:mi_cn:product:'))
        ids.update(r['id'] for r in priority)
        queue=[r for r in mi if r['id'] in ids]
        (root/'targeted-plan.json').write_text(json.dumps(queue,ensure_ascii=False,indent=1)+'\n')
    last=0
    def collect(queue):
      nonlocal last
      for row in queue:
        if row['id'] in done: continue
        time.sleep(max(0,2.15-(time.monotonic()-last)));last=time.monotonic()
        pid=row['id'].rsplit(':',1)[-1];url='https://www.mi.com/shop/buy/detail?product_id='+pid
        result,body=fetch(url,folder,int(pid))
        match=re.search(r'<title[^>]*>(.*?)</title>',body,re.S|re.I)
        title=html.unescape(match[1]).strip() if match else ''
        valid=result['status']==200 and title.endswith('立即购买-小米商城') and result['final_url']==url
        official=title.removesuffix('立即购买-小米商城').strip() if valid else None
        entry=dict(id=row['id'],name=row['name'],price=row.get('price'),url=url,**result,title=title,official_name=official,comparison=compare(row['name'],official) if official else 'unavailable',sample=row['id'] in sample_ids)
        with results_path.open('a') as out:out.write(json.dumps(entry,ensure_ascii=False)+'\n')
        results.append(entry);done.add(row['id']);print(len(done),pid,entry['comparison'],official or str(result['status']),flush=True)
    collect(queue)
    if a.targeted:
        print("TARGETED DONE",len(queue),flush=True)
        return
    sampled=[r for r in results if r['id'] in sample_ids]
    counts=collections.Counter(r['comparison'] for r in sampled)
    # Mixed changes are conservatively treated as potentially missing. The report
    # separately classifies distinctive words from mere spacing/colour variants.
    rate=(counts['database_missing']+counts['changed_review'])/200
    summary=dict(seed=20261104,sample_count=200,universe=len(mi),counts=counts,potential_missing_ratio=rate,full_required=rate>.02)
    (root/'sample-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print('SUMMARY',json.dumps(summary),flush=True)
    if rate>.02: collect(mi)
    print('DONE',len(done),flush=True)
if __name__=='__main__':main()
