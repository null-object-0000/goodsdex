#!/usr/bin/env python3
"""Build hash-verifiable, endpoint-scoped missing-field evidence, never global absence."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def audit(directory=ROOT/'docs/release-coverage'):
    from release_lane_hp import inspect, read_json, PRODUCT_FIELDS
    rows=json.loads((directory/'before.json').read_text())
    captures={}
    for path in [ROOT/'docs/hp-history-20261105/support-evidence.json.gz',directory/'l1-hp/supplemental-support.json']:
        values=read_json(path)
        for c in values if isinstance(values,list) else [values]:
            if hashlib.sha256(c.get('body','').encode()).hexdigest()!=c.get('sha256'):continue
            for device in c.get('payload',{}).get('devices',[]):
                captures[device['productNumber']]=(c,path)
    hp=[]
    for row in rows:
        if not row['id'].startswith('CN:hp_cn:'):continue
        c,path=captures.get(row.get('part_number'),(None,None))
        if inspect(row,c)['missing_reason']!='no_release_field':continue
        devices=json.loads(c['body'])['data']['devices']
        spec=next(d['productSpecs']['data'] for d in devices if d.get('productSpecs',{}).get('data',{}).get('productNumber')==row['part_number'])
        hp.append(dict(id=row['id'],url=c['url'],method='POST',request_payload=c['payload'],
                       capture_file=str(path.relative_to(ROOT)),sha256=c['sha256'],captured_at=c['observed_at'],
                       locator='data.devices[].productSpecs.data; exact productNumber='+row['part_number'],
                       fields_observed=sorted(spec),absent_product_fields=[k for k in PRODUCT_FIELDS if not spec.get(k)],
                       rejected_web_metadata={k:spec.get(k) for k in ('webFirstPublishingDate','webReleaseDate')},
                       identity_quote=json.dumps({k:spec.get(k) for k in ('productNumber','productName')},ensure_ascii=False),
                       conclusion='Only this exact-SKU support response lacks explicit release fields; no claim about all HP sources.'))
    capture=directory/'l2-atour/live-capture.json'
    data=json.loads(capture.read_text())
    outcomes=json.loads((ROOT/'data/official/atour-release-evidence.json').read_text())['outcomes']
    atour=[]
    for item in data['details']:
        detail=item['detail'];spu=str(item['spuId'])
        encoded=json.dumps(detail,ensure_ascii=False,sort_keys=True).encode()
        atour.append(dict(spu_id=spu,ids=[o['id'] for o in outcomes if o['spu_id']==spu],
                          page_url=next((o['source_url'] for o in outcomes if o['spu_id']==spu),data['source_url']),
                          url='https://api-shoppingmall.yaduo.com/goods/spu/getNewDetail/v1',request=dict(spuId=item['spuId']),
                          capture_file=str(capture.relative_to(ROOT)),capture_sha256=hashlib.sha256(capture.read_bytes()).hexdigest(),
                          detail_sha256=hashlib.sha256(encoded).hexdigest(),hash_scope='detail JSON, ensure_ascii=False, sort_keys=True',
                          captured_at=data['captured_at'],fields_observed=sorted(detail),
                          release_named_fields=[k for k in detail if any(word in k.lower() for word in ('release','launch','publish','上市','发布'))],
                          rejected_createTime=detail.get('createTime'),identity_quote=json.dumps({k:detail.get(k) for k in ('id','spuName')},ensure_ascii=False),
                          conclusion='官方商城此详情响应不提供上市时间字段；不证明其他官方渠道没有首发信息。'))
    result=dict(policy='Endpoint-scoped absence only; not official_absent',hp=hp,atour=atour)
    (directory/'field-absence-evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(hp=len(hp),atour_spus=len(atour),atour_rows=sum(len(i['ids']) for i in atour)),ensure_ascii=False))

if __name__=='__main__':audit()
