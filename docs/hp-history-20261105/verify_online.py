"""Verify immutable OSS release, exact API responses, two target families and retention."""
import argparse,gzip,hashlib,json,subprocess
from pathlib import Path
from urllib.parse import quote,urlencode
from datetime import datetime,timezone
P=Path(__file__).parent
API='https://spend.snewbie.site'
OSS='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
def fetch(url):
    return subprocess.check_output(['curl','--noproxy','*','--compressed','-fsSL','--retry','2','--connect-timeout','10','--max-time','90',url])
def main():
    meta=json.loads(fetch(OSS+'meta.json'));desc=meta['files']['goods.json'];raw=fetch(OSS+'blobs/'+desc['sha256']+'.json');goods=json.loads(raw)
    assert hashlib.sha256(raw).hexdigest()==desc['sha256'] and len(raw)==desc['bytes']
    baseline=json.loads((P/'baseline-hp.json').read_text());hp=[r for r in goods if r.get('brand')=='惠普'];assert len(hp)==790
    assert {r['id'] for r in baseline}<={r['id'] for r in hp}
    assert all(r.get('part_number') or r.get('part_number_missing') for r in hp)
    assert all(r.get('image') or r.get('image_missing') for r in hp)
    api_meta=json.loads(fetch(API+'/api/meta'));assert api_meta['revision']==meta['revision'];assert api_meta['retired_count']==meta['retired_count']
    actual_raw=fetch(API+'/api/goods');actual=json.loads(actual_raw);assert actual==goods
    by_id={r['id']:r for r in hp};queries=[]
    for q,key in [('战66','CN:hp_cn:family:zhan66-generation6-14'),('暗影精灵','CN:hp_cn:family:omen-generation10-25l')]:
        url=API+'/api/goods?'+urlencode({'q':q});body=fetch(url);response=json.loads(body)
        # This compatibility endpoint exports the full dataset and ignores q.
        # Retain its original response; clearly label the local display excerpt.
        assert isinstance(response,list)
        matches=[r for r in response if r.get('brand')=='惠普' and q in r.get('name','')]
        target=next(r for r in response if r['id']==key);assert target==by_id[key]
        detail=json.loads(fetch(API+'/api/goods/'+quote(key,safe='')));assert detail==target
        slug='zhan66' if q=='战66' else 'omen';(P/f'api-{slug}.json.gz').write_bytes(gzip.compress(body,mtime=0))
        excerpt={k:target.get(k) for k in ('id','name','part_number','part_number_missing','series','generation','category','source_url','status')}
        (P/f'api-{slug}-target.json').write_text(json.dumps(detail,ensure_ascii=False,indent=1)+'\n')
        queries.append(dict(url=url,response_count=len(response),matching_hp_count=len(matches),query_ignored_by_legacy_export_endpoint=response==goods,target=excerpt,detail_equal=True))
    retired=[]
    for old in [r for r in baseline if r.get('sale_status')=='delisted'][:3]:
        row=by_id[old['id']];assert row['status']=='retired' and row['retired_at']==old['delisted_at']
        for key,value in old.items():assert row[key]==value
        retired.append({k:row[k] for k in ('id','name','status','retired_at','source_url')})
    for sample in json.loads((P/'samples.json').read_text()):
        row=by_id[sample['id']];assert row['name']==sample['official_name'] and row['part_number']==sample['official_part_number'] and row['series']==sample['series']
    result=dict(checked_at=datetime.now(timezone.utc).isoformat(),revision=meta['revision'],goods_sha256=desc['sha256'],total=len(goods),hp_count=len(hp),hp_before=len(baseline),hp_retired=sum(r.get('status')=='retired' for r in hp),retired_count=meta['retired_count'],retired_by_brand=meta['retired_by_brand'],no_lost_hp_ids=True,api_equal_release=True,samples_verified=30,queries=queries,retired_samples=retired)
    (P/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');(P/'online-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=1)+'\n');(P/'online-goods.json.gz').write_bytes(gzip.compress(actual_raw,mtime=0));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
