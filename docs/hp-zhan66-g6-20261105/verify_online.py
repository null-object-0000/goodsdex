"""Verify exact published SKU fields and real production matching response."""
import gzip,hashlib,json,subprocess
from pathlib import Path
from urllib.parse import quote,urlencode
P=Path(__file__).parent
API='https://spend.snewbie.site'
OSS='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
def fetch(url):
 return subprocess.check_output(['curl','--noproxy','*','--compressed','-fsSL','--retry','2','--connect-timeout','10','--max-time','80',url])
def main():
 meta=json.loads(fetch(OSS+'meta.json'));desc=meta['files']['goods.json'];raw=fetch(OSS+'blobs/'+desc['sha256']+'.json');assert hashlib.sha256(raw).hexdigest()==desc['sha256'];goods=json.loads(raw)
 hp=[r for r in goods if r.get('source')=='hp_cn'];by_id={r['id']:r for r in hp};before=json.loads(gzip.decompress((P/'goods-before.json.gz').read_bytes()));assert {r['id'] for r in before if r.get('source')=='hp_cn'}<=by_id.keys()
 configs=json.loads((P/'configurations.json').read_text())
 for expected in configs:
  actual=by_id[expected['id']]
  assert actual['name']==expected['name'] and actual['part_number']==expected['part_number']
  assert actual['series']=='ProBook' and actual['generation']=='G10'
  assert actual['configuration_evidence']==expected['configuration_evidence']
  for key in ('屏幕尺寸','运行内存','屏幕规格','存储容量'):
   if key in expected['params']:assert actual['params'][key]==expected['params'][key],(actual['id'],key)
  assert actual['status']=='retired'
 assert by_id['CN:hp_cn:sku:7Z8L4PC']['params']['屏幕规格']=='QHD'
 result=json.loads(fetch(API+'/api/goods/match?'+urlencode({'name':'惠普（HP）战66 六代酷睿 15.6 英寸 i7-13代 32G 1T 2.5K 120Hz'})))
 assert result['match'] is None
 assert [r['part_number'] for r in result['candidates']]==['7P211PC','7P2D5PC']
 assert all(r['score']==.9 for r in result['candidates'])
 details=[]
 for sku in ('7P2D5PC','7Z8L4PC','9T0Q0PC'):
  row=json.loads(fetch(API+'/api/goods/'+quote('CN:hp_cn:sku:'+sku,safe='')));assert row==by_id[row['id']];details.append(row)
 (P/'match-after-online.json').write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n')
 (P/'online-details.json').write_text(json.dumps(details,ensure_ascii=False,indent=1)+'\n')
 summary=dict(revision=meta['revision'],goods_sha256=desc['sha256'],total=len(goods),hp_count=len(hp),verified_configurations=len(configs),new_sku='7Z8L4PC',no_lost_hp_ids=True,exact_api_details=True,actual_match=result)
 (P/'online-verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=1)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='actual_match'},ensure_ascii=False))
if __name__=='__main__':main()
