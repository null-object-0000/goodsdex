"""Scan every official category; collect details only for previously unknown IDs."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json

from .sources import mi_cn
from .pipeline import collect_one
from .publish import to_public
from .discovery_prices import normalize_discovery_quote


def discover(previous, excluded, categories, *, enumerate_products=mi_cn.enumerate_products,
             collect=collect_one, workers=4):
    known={row['id'] for row in [*previous,*excluded]}
    candidates={};observations={};failed=[];quarantined=[];records=[]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(enumerate_products,query):category for category,query in categories.items()}
        for future in as_completed(futures):
            category=futures[future]
            try:
                result=future.result();observations[category]=result['discovery']
                if result['discovery']['completeness'] in ('failed','unknown'):
                    failed.append(category)
                for item in result['items']:
                    pid=str(item['pid'])
                    if not pid.isdigit():raise ValueError('Invalid discovery product ID')
                    if 'CN:mi_cn:product:'+pid not in known:
                        candidates.setdefault(pid,(category,item))
            except Exception as exc:
                failed.append(category);observations[category]={'completeness':'failed','error':type(exc).__name__}
    # An interrupted scan never masquerades as complete and never changes data.
    if failed:
        return previous,[],{'ok':False,'failed_categories':sorted(set(failed)),'categories':observations}
    print(json.dumps({'phase':'discovered','categories':len(observations),'known':len(known),'new_candidates':len(candidates)}),flush=True)
    remaining=dict(candidates);seen=set()
    while remaining:
        batch=remaining;remaining={}
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(collect,pid,item.get('name',''),category,observations[category],item.get('variants')):(pid,category)
                     for pid,(category,item) in batch.items()}
            seen.update(batch)
            for future in as_completed(futures):
                pid,category=futures[future]
                try:
                    rec=future.result();product=rec['product'];identity=product.get('identity_evidence') or {}
                    if product.get('product_id')!='CN:mi_cn:product:'+pid or identity.get('mobile_product_id')!=pid:
                        raise ValueError('Unverified mobile product identity')
                    if product.get('is_container'):
                        for child in product.get('container_children',[]):
                            child=str(child)
                            if child.isdigit() and child not in seen and 'CN:mi_cn:product:'+child not in known:
                                remaining.setdefault(child,(category,{'name':'','variants':[]}))
                        raise ValueError('Container fields belong to child products')
                    row=normalize_discovery_quote(to_public(rec))
                    if not row.get('name') or not (row.get('name_source') or {}).get('identity_verified'):
                        raise ValueError('Unverified product name')
                    records.append(rec)
                except Exception as exc:
                    quarantined.append({'pid':pid,'category':category,'reason':str(exc)})
    records.sort(key=lambda r:r['product']['product_id'])
    # Existing business fields, source evidence and prices remain byte-for-byte
    # equal as JSON values. Independent collectors own their regular refreshes.
    after=[*previous,*(normalize_discovery_quote(to_public(r)) for r in records)]
    return after,records,{'ok':True,'categories':observations,'new_candidates':len(candidates),
                          'added':len(records),'known_retained':len(previous),'quarantined':quarantined}


def run(root, categories=None):
    public=root/'public';path=public/'goods.json'
    previous=json.loads(path.read_text(encoding='utf-8'))
    excluded_path=public/'goods-excluded.json'
    excluded=json.loads(excluded_path.read_text(encoding='utf-8')).get('items',[]) if excluded_path.exists() else []
    all_categories=mi_cn.list_categories()
    if categories:
        unknown=set(categories)-set(all_categories)
        if unknown:raise ValueError('Unknown official categories: '+','.join(sorted(unknown)))
        all_categories={name:all_categories[name] for name in categories}
    after,records,report=discover(previous,excluded,all_categories)
    report_path=root/'data/catalog-discovery-report.json';report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if not report['ok']:raise RuntimeError('Official category discovery failed; prior catalogue preserved')
    for rec in records:
        target=root/'data/categories'/('discovered-'+rec['product']['product_id'].rsplit(':',1)[-1]+'.json')
        target.parent.mkdir(parents=True,exist_ok=True)
        # Embed full evidence, not an ephemeral runner-local absolute path.
        for cap in rec.get('captures',[]):
            if cap.get('raw_ref'):
                cap['response_raw']=Path(cap['raw_ref']).read_text(encoding='utf-8');cap['raw_ref']=''
        target.write_text(json.dumps([rec],ensure_ascii=False),encoding='utf-8')
    if records:path.write_text(json.dumps(after,ensure_ascii=False),encoding='utf-8')
    return report
