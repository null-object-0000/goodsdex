"""Build an evidence manifest and a local replay; does not publish or alter gates."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit, parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.homeappliance_params import apply_params, parse_attribute_list, parse_robot_battery, parse_manual_scalars, parse_aircon_table, parse_fridge_table, named_capacities
from collect_homeappliance_params import read_rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--goods',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('docs/homeappliance-params-20261106'))
    ap.add_argument('--manifest',type=Path,default=Path('data/enrichment/homeappliance-params.json'))
    a=ap.parse_args();p=a.output;rows=read_rows(a.goods)
    allowed={k for r in rows for k in r.get('params',{})}
    cs=json.loads((p/'captures.json').read_text());ts=json.loads((p/'targets.json').read_text())
    ms=json.loads((p/'manuals.json').read_text())
    if (p/'priority-manuals.json').exists():ms.update(json.loads((p/'priority-manuals.json').read_text()))
    manufacturers=json.loads((p/'manufacturer-manuals.json').read_text()) if (p/'manufacturer-manuals.json').exists() else {}
    if (p/'microwave-manufacturer.json').exists():
        v=json.loads((p/'microwave-manufacturer.json').read_text());manufacturers[v['model']]=v
    bridges=json.loads((p/'shop-bridges.json').read_text());shop=json.loads((p/'shop-captures.json').read_text())
    def raw(c):
        data=gzip.decompress((p/'raw'/(c['sha256']+'.json.gz')).read_bytes())
        if hashlib.sha256(data).hexdigest()!=c['sha256']: raise ValueError('Corrupt source capture')
        return json.loads(data)
    pid_models=defaultdict(set)
    for key,c in cs.items():
        if not key.endswith(':product') or not c.get('sha256'):continue
        d=raw(c).get('data') or {};u=urlsplit((d.get('buyUrl') or {}).get('channelUrl',''));q=parse_qs(u.query)
        pid=(q.get('product_id') or q.get('commodityId') or [''])[0]
        if pid:pid_models[pid].add(d.get('model'))
    from collect_homeappliance_third_party import parse as parse_zol
    reviews=json.loads((p/'third-party-review.json').read_text()) if (p/'third-party-review.json').exists() else []
    third_party={v['id']:v for v in reviews if v['accepted']}
    third_caps=json.loads((p/'third-party-captures.json').read_text()) if (p/'third-party-captures.json').exists() else {}
    l7_path=Path(__file__).resolve().parents[1]/'data/third-party/l7-release-evidence.json'
    locked_ids={e['id'] for e in json.loads(l7_path.read_text())['entries']}
    entries=[];new_proofs=[]
    for t in ts:
        if t['had_params']:continue
        m=t['model'];e=dict(id=t['id'],expected_name=t['expected_name'],category=t['category'],
                            model=m,identity_method='audited_product_id' if t['id'].startswith('CN:mi_cn:product:') else t['mapping'],
                            identity_evidence=dict(id=t['id'],name=t['expected_name'],model=m),params={},attempts=[])
        c=cs.get(str(m)+':product',{});prod=raw(c).get('data') or {} if c.get('sha256') else {}
        if not m or prod.get('model')!=m:
            e['params_missing']='identity_unverified';entries.append(e);continue
        for ep in ('product','attribute','introduction'):
            cap=cs.get(str(m)+':'+ep,{})
            attempt=dict(endpoint=ep,**cap)
            if cap.get('sha256'):
                response=raw(cap);attempt['api_code']=response.get('code')
                if response.get('code')!=0:attempt['status']='source_error'
            e['attempts'].append(attempt)
        cap=cs.get(str(m)+':attribute',{})
        if cap.get('sha256'):
            d=raw(cap)
            if d.get('code')==0:
                for k,v in parse_attribute_list((d.get('data') or {}).get('list') or [],allowed).items():
                    e['params'][k]=dict(v,url=cap['url'],sha256=cap['sha256'],source_type='official',source='mijia_baike',captured_at=cap['captured_at'])
        b=bridges.get(t['id'])
        if b:
            cap=shop[b['pid']];attempt=dict(endpoint='linked_shop',**cap,pid=b['pid']);e['attempts'].append(attempt)
            if len(pid_models[b['pid']])!=1:attempt['status']='ambiguous_shop_model'
            elif cap.get('sha256'):
                d=raw(cap);gl=((d.get('data') or {}).get('goodsInfo') or {}).get('goodsList') or []
                if d.get('code')!=0:attempt['status']='source_error'
                elif not gl or str(gl[0].get('productId'))!=b['pid']:attempt['status']='shared_or_container_product'
                else:
                    for i,item in enumerate((gl[0].get('classParameters') or {}).get('list') or []):
                        k,v=item.get('name'),item.get('value')
                        if k not in allowed or not isinstance(v,str) or not v.strip():continue
                        e['params'].setdefault(k,dict(value=v,source_field=k,raw_value=v,locator=f'$.data.goodsInfo.goodsList[0].classParameters.list[{i}].value',
                            url=f'https://www.mi.com/shop/buy/detail?product_id={b["pid"]}',api_url=cap['url'],sha256=cap['sha256'],source_type='official',source='mi_store',
                            method='structured_attribute',captured_at=cap['captured_at'],identity_bridge=b))
        for prefix,collection in [('',ms),('manufacturer-',manufacturers)]:
            manual=collection.get(m,{})
            attempt=dict(endpoint=prefix+'manual',**manual);e['attempts'].append(attempt)
            textpath=p/'texts'/(prefix+str(m)+'.txt.gz')
            if not manual.get('sha256') or not textpath.exists():continue
            textbytes=gzip.decompress(textpath.read_bytes())
            if hashlib.sha256(textbytes).hexdigest()!=manual['text_sha256']:raise ValueError('Corrupt manual text')
            text=textbytes.decode()
            values=parse_robot_battery(text) if t['category']=='扫地机器人' else parse_manual_scalars(text,t['category'])
            if t['category']=='空调':values.update(parse_aircon_table(text))
            if t['category']=='冰箱':
                if len(named_capacities(t['expected_name']))>1:
                    values={}
                    attempt['scope_status']='shared_capacity_profile_requires_explicit_columns'
                values.update(parse_fridge_table(text,t['expected_name']))
            for k,v in values.items():
                if k not in allowed:raise ValueError('New parameter spelling: '+k)
                proof=dict(v,url=manual['url'],sha256=manual['sha256'],text_sha256=manual['text_sha256'],source_type='official',
                            source='manufacturer_manual' if prefix else 'mijia_manual',model=m)
                if k not in e['params']:
                    e['params'][k]=proof;new_proofs.append(dict(id=t['id'],name=t['expected_name'],field=k,**proof))
        review=third_party.get(t['id'])
        if not e['params'] and review:
            cap=third_caps[review['url']]
            rawbytes=gzip.decompress((p/'third-party'/(review['sha256']+'.html.gz')).read_bytes())
            if hashlib.sha256(rawbytes).hexdigest()!=review['sha256']:raise ValueError('Corrupt third-party capture')
            title,fields=parse_zol(rawbytes)
            if title!=review['title'] or review['model']!=m or review['expected_name']!=t['expected_name']:raise ValueError('Third-party identity drift')
            aliases={'吸尘能力':'吸力','集尘容量':'尘盒容量'}
            for source_field in ('额定功率','额定电压','产品尺寸','充电时间','水箱容量','吸尘能力','集尘容量'):
                k=aliases.get(source_field,source_field)
                if source_field in fields and k in allowed:
                    e['params'][k]=dict(fields[source_field],url=review['url'],sha256=review['sha256'],source_type='third_party',source='zol',
                        method='third_party_html',reviewed_model=m,source_title=title,captured_at=cap['captured_at'])
        if not e['params']:
            has_error=any(v.get('error') or v.get('status')=='source_error' for v in e['attempts'] if v.get('endpoint')!='manufacturer-manual')
            status=ms.get(m,{}).get('status')
            if has_error:e['params_missing']='source_error'
            elif m not in ms:e['params_missing']='not_collected'
            elif status=='image_only':e['params_missing']='image_only_spec'
            elif status=='text':e['params_missing']='no_unambiguous_text_spec'
            else:
                intro=cs.get(str(m)+':introduction',{})
                content=((raw(intro).get('data') or {}).get('introductionHtml') or {}).get('introduction','') if intro.get('sha256') else ''
                e['params_missing']='image_only_spec' if '<img' in content or '"type":"picture"' in content else 'page_no_spec'
        if e['params'] and e['id'] in locked_ids:
            e['deferred_reason']='release_identity_review_required'
        entries.append(e)
    manifest=dict(schema=1,scope='homeappliance-params-20261106',items=entries)
    a.manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    after=apply_params(rows,manifest)
    # This replay owns only specification values and their evidence/missing metadata.
    owned={'params','params_sources','params_missing','params_missing_evidence','params_conflicts','params_source_type'}
    assert len(after)==len(rows)
    assert all({k:v for k,v in x.items() if k not in owned}=={k:v for k,v in y.items() if k not in owned} for x,y in zip(rows,after))
    assert apply_params(after,manifest)==after
    stats={}
    for cat in ('微波炉','空调','扫地机器人','冰箱'):
        ids={t['id'] for t in ts if t['category']==cat};before=[r for r in rows if r['id'] in ids];rr=[r for r in after if r['id'] in ids]
        stats[cat]=dict(total=len(rr),before=sum(bool(r.get('params')) for r in before),after=sum(bool(r.get('params')) for r in rr),
                        missing_reasons=dict(Counter(r.get('params_missing','unverified') for r in rr if not r.get('params'))))
    (p/'coverage.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    (p/'manual-claims.json').write_text(json.dumps(new_proofs,ensure_ascii=False,indent=2)+'\n')
    scoped=[r for r in after if r['id'] in {t['id'] for t in ts}]
    (p/'goods-after-scoped.json.gz').write_bytes(gzip.compress(json.dumps(scoped,ensure_ascii=False).encode(),mtime=0))
    (p/'goods-before-scoped.json.gz').write_bytes(gzip.compress(json.dumps([r for r in rows if r['id'] in {t['id'] for t in ts}],ensure_ascii=False).encode(),mtime=0))
    print(json.dumps(stats,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
