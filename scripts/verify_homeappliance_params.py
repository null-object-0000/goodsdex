"""Verify every selected spec against captured source bytes; emit ten audit rows."""
import argparse
from collections import Counter
import gzip
import hashlib
from html import unescape
import json
from pathlib import Path
import random
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.homeappliance_params import apply_params
from collect_homeappliance_params import read_rows


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--goods',type=Path,required=True);ap.add_argument('--output',type=Path,default=Path('docs/homeappliance-params-20261106'));a=ap.parse_args();p=a.output
    rows=read_rows(a.goods);manifest=json.loads(Path('data/enrichment/homeappliance-params.json').read_text());after=apply_params(rows,manifest)
    before={r['id']:r for r in rows};after_by_id={r['id']:r for r in after};targets={t['id']:t for t in json.loads((p/'targets.json').read_text())}
    verified=Counter();proofs={}
    for entry in manifest['items']:
        for field,v in entry['params'].items():
            if v['method']=='structured_attribute':
                raw=gzip.decompress((p/'raw'/(v['sha256']+'.json.gz')).read_bytes());assert hashlib.sha256(raw).hexdigest()==v['sha256'];data=json.loads(raw)
                if v['locator'].startswith('$.data.list['):
                    i=int(re.search(r'\[(\d+)\]',v['locator'])[1]);item=data['data']['list'][i]
                    assert item['attributeName']==v['source_field'] and item['attributeValue']==v['raw_value']
                    assert v['value']==' / '.join(x+(item.get('unit') or '') for x in item['attributeValue'])
                    quote=json.dumps(item,ensure_ascii=False)
                else:
                    i=int(re.search(r'classParameters.list\[(\d+)\]',v['locator'])[1]);g=data['data']['goodsInfo']['goodsList'][0];item=g['classParameters']['list'][i]
                    assert item['name']==field and item['value']==v['value']==v['raw_value']
                    assert str(g['productId'])==v['identity_bridge']['pid'];quote=json.dumps(item,ensure_ascii=False)
            elif v['method']=='pdf_text':
                m=entry['model'];prefix='manufacturer-' if v['source']=='manufacturer_manual' else ''
                raw=gzip.decompress((p/'texts'/(prefix+m+'.txt.gz')).read_bytes());assert hashlib.sha256(raw).hexdigest()==v['text_sha256']
                page=raw.decode().split('\f')[v['page']-1];assert v['quote'] in page
                for line in v.get('scope_quote','').splitlines():assert line in page
                for model in v.get('hardware_models',[]):assert model in page
                compact=lambda s:re.sub(r'\s+','',s)
                assert compact(v['raw_value']) in compact(v['quote']) and compact(v['source_field']) in compact(v['quote'])
                quote=v['quote']
            elif v['method']=='third_party_html':
                raw=gzip.decompress((p/'third-party'/(v['sha256']+'.html.gz')).read_bytes());assert hashlib.sha256(raw).hexdigest()==v['sha256'];s=raw.decode('gb18030')
                span_id=v['locator'][1:];match=re.search(r'<span\b[^>]*\bid=["\']'+re.escape(span_id)+r'["\'][^>]*>(.*?)</span>',s,re.S);assert match
                text=unescape(re.sub('<[^>]+>','',re.sub(r'<br\s*/?>',' ',match[1],flags=re.I))).strip();assert text==v['value']==v['raw_value'];quote=v['quote']
                name_id=span_id.replace('newPmVal_','newPmName_')
                label=re.search(r'<span\b[^>]*\bid=["\']'+re.escape(name_id)+r'["\'][^>]*>(.*?)</span>',s,re.S)
                assert label and unescape(re.sub('<[^>]+>','',label[1])).strip()==v['source_field']
            else:raise ValueError(v['method'])
            proofs[(entry['id'],field)]={**v,'quote':quote};verified[v['source_type']]+=1
    # All non-spec fields, including all releases/identities/prices, are unchanged.
    owned={'params','params_sources','params_missing','params_missing_evidence','params_conflicts','params_source_type'}
    assert all({k:v for k,v in x.items() if k not in owned}=={k:v for k,v in y.items() if k not in owned} for x,y in zip(rows,after))
    assert apply_params(after,manifest)==after
    rng=random.Random(20261106);chosen=[]
    for category,n in [('微波炉',3),('空调',3),('扫地机器人',2),('冰箱',2)]:
        candidates=sorted([r for r in after if r['id'] in targets and targets[r['id']]['category']==category and r.get('params_sources')],key=lambda r:r['id'])
        if category=='扫地机器人':
            for kind in ('official','third_party'):
                subset=[r for r in candidates if r['params_source_type']==kind];chosen+=rng.sample(subset,1)
        else:chosen+=rng.sample(candidates,n)
    samples=[];lines=['# 十条参数原文逐项对照','','固定随机种子 20261106；3 微波炉、3 空调、2 扫地机（官方/第三方各一）、2 冰箱。P1 的日期身份待处理，不混入已写入样本。','']
    for r in chosen:
        item=dict(id=r['id'],name=r['name'],category=targets[r['id']]['category'],source_type=r['params_source_type'],params={})
        lines += [f'## {r["name"]}（{r["id"]}）','',f'来源类型：**{r["params_source_type"]}**。','']
        for k,v in r['params_sources'].items():
            proof=proofs[(r['id'],k)];assert r['params'][k]==proof['value'];item['params'][k]=proof
            display_value=proof['value'].replace('\n',r'\n')
            lines += [f'- **{k}**：`{display_value}`；[来源]({proof["url"]})，`{proof["locator"]}`。',f'  原文：{proof["quote"].strip().replace(chr(10), " / ")}']
        lines += [''];samples.append(item)
    (p/'sample-10.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n');(p/'sample-10.md').write_text('\n'.join(lines).rstrip()+'\n')
    result=dict(rows=len(rows),candidate_fields_verified=dict(verified),non_spec_fields_unchanged=True,replay_idempotent=True,sample_count=len(samples),
                deferred=[dict(id=e['id'],reason=e['deferred_reason'],available_fields=list(e['params'])) for e in manifest['items'] if e.get('deferred_reason')])
    (p/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
