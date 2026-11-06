"""Offline replay, byte/quote checks, fixed-scope coverage and ten PDF audit rows."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.homeappliance_params import apply_params, named_capacities
from goodsdex.release_l7 import INPUT as DATE_INPUT
from goodsdex.series_release import DEFAULT_INPUT as SERIES_INPUT
from goodsdex.manual_params import apply_manual_params, parse_manual
from collect_homeappliance_params import read_rows

OWNED={'params','params_sources','params_missing','params_missing_evidence','params_conflicts','params_source_type'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--goods',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('docs/manual-params-20261106'))
    a=ap.parse_args();p=a.output; rows=apply_params(read_rows(a.goods)); after=apply_manual_params(rows)
    index=json.loads((p/'collection.json').read_text()); manifest=json.loads(Path('data/enrichment/manual-params.json').read_text())
    for m,c in index.items():
        raw_intro=gzip.decompress((p/'introductions'/(m+'.json.gz')).read_bytes())
        assert hashlib.sha256(raw_intro).hexdigest()==c['introduction_sha256']
        data=json.loads(raw_intro).get('data') or {}
        if c.get('pdf_url'): assert c['pdf_url']==data['introductionPdf']['url']
        if 'text_sha256' not in c: continue
        raw=gzip.decompress((p/'texts'/(m+'.txt.gz')).read_bytes())
        assert hashlib.sha256(raw).hexdigest()==c['text_sha256']
        parsed=parse_manual(raw.decode(),m,c['pdf_url'])
        for key,v in c.get('params',{}).items():
            assert {k:v[k] for k in parsed['params'][key]}==parsed['params'][key]
            assert v['quote'] in raw.decode().split('\f')[v['page']-1]
            assert v['value'] in v['quote'] and v['pdf_sha256']==c['pdf_sha256']
    assert all({k:v for k,v in x.items() if k not in OWNED}=={k:v for k,v in y.items() if k not in OWNED} for x,y in zip(rows,after))
    assert apply_manual_params(after)==after
    assert all(all(y['params'].get(k)==v for k,v in x.get('params',{}).items()) for x,y in zip(rows,after))
    old_targets=json.loads(Path('docs/homeappliance-params-20261106/targets.json').read_text())
    byid={r['id']:r for r in rows};newid={r['id']:r for r in after}
    groups={c:[x['id'] for x in old_targets if x['category']==c] for c in ('微波炉','扫地机器人','冰箱','空调')}
    groups['洗衣机']=[r['id'] for r in rows if r.get('category') in ('洗衣机','波轮洗衣机','滚筒洗衣机') and r.get('brand') in ('小米','米家','小米公司')]
    coverage={c:dict(total=len(ids),before=sum(bool(byid[i].get('params')) for i in ids),after=sum(bool(newid[i].get('params')) for i in ids)) for c,ids in groups.items()}
    for c,g in coverage.items(): g['percent']=round(g['after']/g['total']*100,2) if g['total'] else 0
    protected={x['id'] for x in json.loads(DATE_INPUT.read_text())['entries']}
    protected|={m['id'] for b in json.loads(SERIES_INPUT.read_text())['batches'] for m in b['members']}
    targets={x['id']:x for x in json.loads((p/'targets.json').read_text())}
    trace=[]
    for c,ids in groups.items():
        reasons=Counter()
        for i in ids:
            r=newid[i];m=targets.get(i,{}).get('model');status=index.get(m,{}).get('status','identity_unavailable')
            blocked=('release_identity_review_required' if i in protected else
                     'container_scope_unverified' if r.get('is_container') else
                     'variant_scope_review_required' if c=='冰箱' and len(named_capacities(r['name']))>1 else None)
            if not r.get('params'): reasons[blocked or status]+=1
            trace.append(dict(id=i,name=r['name'],category=c,model=m,collection_status=status,write_blocked_reason=blocked,
                before=bool(byid[i].get('params')),after=bool(r.get('params')),
                added_fields=sorted(set(r.get('params',{}))-set(byid[i].get('params',{})))))
        coverage[c]['remaining_statuses']=dict(reasons)
    (p/'record-outcomes.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2)+'\n')
    counts=Counter(v['status'] for v in index.values()); downloaded=sum('text_sha256' in x for x in index.values());with_table=sum(bool(x.get('sections')) for x in index.values())
    report=dict(baseline_commit='07ca197023203fa8f73336ba5effea2d8c0d100c',input_sha256=hashlib.sha256(a.goods.read_bytes()).hexdigest(),coverage=coverage,
        collection=dict(models=len(index),statuses=dict(counts),parsed_over_downloaded=dict(parsed=counts['parsed'],downloaded=downloaded,percent=round(counts['parsed']/downloaded*100,2)),parsed_over_heading_texts=dict(parsed=counts['parsed'],detected_heading_texts=with_table,percent=round(counts['parsed']/with_table*100,2))),
        invariant_checks=dict(non_parameter_fields_unchanged=True,existing_parameter_values_unchanged=True,replay_idempotent=True),
        added_fields=sum(len(x['added_fields']) for x in trace),records_with_added_fields=sum(bool(x['added_fields']) for x in trace),
        candidate_records=len(manifest['items']),candidate_fields=sum(len(e['params']) for e in manifest['items']))
    # Save the original acceptance scope, including washers, for standalone replay.
    scoped=[r for r in read_rows(a.goods) if any(r['id'] in ids for ids in groups.values())]
    (p/'baseline.json.gz').write_bytes(gzip.compress(json.dumps(scoped,ensure_ascii=False,sort_keys=True).encode(),mtime=0))
    samples=[];lines=['# 十条说明书原文与解析结果对照','','按类别和 ID 固定排序选择，每条列一项实际新增字段；不把未入库候选计作成功。','']
    for c,ids in groups.items():
        candidates=[]
        for i in ids:
            r=newid[i]
            fields={k:v for k,v in r.get('params_sources',{}).items() if v.get('source')=='manual_pdf' and k not in byid[i].get('params',{})}
            if fields:candidates.append((i,fields))
        for i,fields in sorted(candidates)[:2]:
            k=next(iter(sorted(fields)));v=fields[k];r=newid[i]
            samples.append(dict(id=i,name=r['name'],category=c,key=k,value=r['params'][k],**v))
            lines += [f"## {len(samples)}. {r['name']}（{i}）",'',f"`{v['model']}`，PDF 第 {v['page']} 页；[说明书]({v['pdf_url']})。",'', '```text',v['quote'],'```',f"解析：`{k}` → `{r['params'][k]}`；`source=manual_pdf`。",'']
    assert len(samples)==10, len(samples)
    report['sample_count']=len(samples)
    (p/'sample-10.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')
    (p/'sample-10.md').write_text('\n'.join(lines))
    (p/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
