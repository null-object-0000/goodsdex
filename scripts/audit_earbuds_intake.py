"""Read-only duplicate and date-coverage audit of the reviewed Earbuds append."""
import argparse
from collections import defaultdict,Counter
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.earbuds_intake import apply_intake
from goodsdex.release_coverage import matrix
ROOT=Path(__file__).resolve().parents[1]/'docs/earbuds-intake-20261106'

def save(name,value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=1)+'\n')

def duplicates(rows):
    groups=defaultdict(list)
    for ordinal,r in enumerate(rows):
        groups[(r.get('brand'),r.get('name'),r.get('price'))].append((ordinal,r))
    out=[]
    for (brand,name,price),items in groups.items():
        if len(items)<2:continue
        ids=[r['id'] for _,r in items];sources=[r.get('source') for _,r in items]
        # Same name and price is a review key, NOT proof that SKUs are identical.
        allkeys=set().union(*(r for _,r in items))
        differing=[k for k in sorted(allkeys) if any(r.get(k)!=items[0][1].get(k) for _,r in items[1:])]
        out.append(dict(brand=brand,name=name,price=price,count=len(items),excess_rows=len(items)-1,ids=ids,distinct_id_count=len(set(ids)),sources=sources,same_id=len(set(ids))==1,differing_fields=differing,rows=[dict(ordinal=i,id=r['id'],source=r.get('source'),primary_source=r.get('primary_source'),gid=r.get('gid'),sku_no=r.get('sku_no'),model=r.get('model'),record_level=r.get('record_level'),source_url=r.get('source_url'),attrs=r.get('attrs'),variant_attrs=r.get('variant_attrs'),part_number=r.get('part_number')) for i,r in items],decision='review_only_no_merge'))
    return sorted(out,key=lambda g:(-g['count'],str(g['brand']),g['name'],str(g['price'])))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--goods',type=Path,required=True);a=ap.parse_args()
    before=json.loads(a.goods.read_text());after=apply_intake(before)
    assert after[:len(before)]==before
    new=after[len(before):]
    save('all-23.json',new)
    sample_models=['miwear.headphone.l76c','miwear.headphone.l77c','miwear.headphone.l71c','miwear.headphone.k75sc','miwear.headphone.l77sc','miwear.headphone.k75mcn','miwear.headphone.n75c','miwear.headphone.o76cn','miwear.headphone.o71c','miwear.headphone.q74cc']
    samples=[r for model in sample_models for r in after if r['id']==model];save('sample-10.json',samples)
    gs=duplicates(before)
    summary=dict(groups=len(gs),involved_rows=sum(g['count'] for g in gs),excess_rows=sum(g['excess_rows'] for g in gs),priced_groups=sum(g['price'] is not None for g in gs),null_price_groups=sum(g['price'] is None for g in gs),same_id_groups=sum(g['same_id'] for g in gs),byte_equivalent_groups=sum(not g['differing_fields'] for g in gs),cross_source_groups=sum(len(set(g['sources']))>1 for g in gs),deleted=0)
    save('duplicates.json',dict(summary=summary,groups=gs));save('duplicates-first-20.json',gs[:20])
    b=matrix(before)['total'];e=matrix(after)['total'];save('coverage.json',dict(before=b,after=e,added=len(new),date_numerator_unchanged=b['covered']==e['covered'],historical_reference=dict(before_total=3572,after_total=3595,covered=1646,before_percent=1646/3572*100,after_percent=1646/3595*100)))
    probes=json.loads((ROOT/'channel-searches.json').read_text());by={p['model']:p for p in probes};sample=[by[k] for k in sample_models]
    stats=lambda ps:dict(total=len(ps),matched=sum(bool(p['matches']) for p in ps),rate=sum(bool(p['matches']) for p in ps)/len(ps),mi_store=sum(any(m['channel']=='mi_store' for m in p['matches']) for p in ps),youpin=sum(any(m['channel']=='youpin' for m in p['matches']) for p in ps),errors=sum(bool(p['mi']['error'] or p['youpin']['error']) for p in ps))
    save('channel-summary.json',dict(all_23=stats(probes),sample_10=stats(sample),sampling='固定人工覆盖样本，含6条历史主线/限定、2条新主线与2条已知渠道候选；不是随机总体命中率估计',sample_models=sample_models,matches=[dict(model=p['model'],name=p['name'],matches=p['matches']) for p in probes if p['matches']]))
    print(json.dumps(dict(before=len(before),after=len(after),duplicates=summary,channels=stats(probes)),ensure_ascii=False))
if __name__=='__main__':main()
