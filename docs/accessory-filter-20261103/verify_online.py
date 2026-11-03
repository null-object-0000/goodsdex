"""Read the real API and verify the filtered release, including all review samples."""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from goodsdex.accessories import classify


def main():
 p=argparse.ArgumentParser();p.add_argument('--expected',type=Path,required=True);a=p.parse_args()
 out=Path(__file__).parent
 stamp=datetime.now(timezone.utc).isoformat()
 def fetch(route):
  url='https://spend.snewbie.site'+route
  with urlopen(Request(url,headers={'Accept-Encoding':'gzip','Cache-Control':'no-cache'}),timeout=45) as r:
   data=r.read()
   if r.headers.get('Content-Encoding')=='gzip':data=gzip.decompress(data)
  return json.loads(data),data
 meta,mb=fetch('/api/meta');goods,gb=fetch('/api/goods')
 summary=dict(checked_at=stamp,meta_count=meta.get('count'),goods_count=len(goods),
  brands=meta.get('brands'),release_dates_other_brands=meta.get('release_dates_other_brands'),
  release_dates_cars=meta.get('release_dates_cars'),accessories=meta.get('accessories'))
 expected=json.loads(a.expected.read_text())
 summary['ids_match']=Counter(r['id'] for r in expected)==Counter(r['id'] for r in goods)
 summary['no_accessories']=not any(classify(r)['accessory'] for r in goods)
 summary['cars_unchanged']=[r for r in expected if classify(r)['basis']=='car']==[r for r in goods if classify(r)['basis']=='car']
 summary['goods_sha256']=hashlib.sha256(gb).hexdigest()
 summary['goods_match_manifest']=meta.get('files',{}).get('goods.json',{}).get('sha256')==summary['goods_sha256']
 (out/'online-attempts.jsonl').open('a').write(json.dumps(summary,ensure_ascii=False)+'\n')
 print(json.dumps(summary,ensure_ascii=False))
 assert meta['count']==len(goods)==len(expected) and all(summary[k] for k in ('ids_match','no_accessories','cars_unchanged','goods_match_manifest')), 'API has not synchronized this release yet'
 actual={r['id']:r for r in goods}
 samples=json.loads((out/'sample-30.json').read_text())
 assert all((s['id'] not in actual)==(s['decision']=='配件') for s in samples)
 summary['sample_30_presence_correct']=True
 details=[]
 for key in ('CN:mi_cn:product:16549', 'CN:mi_cn:product:13143', 'CN:mi_cn:product:10050050', 'CN:mi_cn:product:11374', 'CN:dji:sku:101241', 'CN:mi_cn:product:10050015', 'CN:mi_cn:product:16684'):
  expected_present=key in actual
  try:
   row,_=fetch('/api/goods/'+quote(key,safe=''))
   assert expected_present and row['id']==key
   details.append(dict(id=key,status=200,name=row.get('name')))
  except HTTPError as error:
   assert not expected_present and error.code==404, (key,error.code)
   details.append(dict(id=key,status=404))
 summary['detail_checks']=details
 (out/'api-meta-after.json').write_bytes(mb)
 (out/'api-goods-after.json.gz').write_bytes(gzip.compress(gb,mtime=0))
 (out/'online-verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
