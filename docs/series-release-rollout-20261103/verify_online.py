"""Read-only live index and exact detail checks against the finalized data branch."""
import argparse,gzip,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
import requests
P=Path(__file__).parent

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--expected',type=Path,required=True);a=parser.parse_args()
 expected=json.loads(a.expected.read_bytes());byid={r['id']:r for r in expected};s=requests.Session();s.trust_env=False
 stamp=datetime.now(timezone.utc).isoformat()
 def get(path):
  r=s.get('https://spend.snewbie.site'+path,headers={'Cache-Control':'no-cache'},timeout=40);r.raise_for_status();return r.json(),r.content
 goods,raw=get('/api/goods');meta,_=get('/api/meta')
 matching=goods==expected
 summary=dict(checked_at=stamp,goods_count=len(goods),full_catalog_equal=matching,series_count=sum(bool(r.get('series_release')) for r in goods),expected_series_count=sum(bool(r.get('series_release')) for r in expected),goods_sha256=hashlib.sha256(raw).hexdigest(),manifest_sha256=meta.get('files',{}).get('goods.json',{}).get('sha256'))
 (P/'online-attempts.jsonl').open('a').write(json.dumps(summary,ensure_ascii=False)+'\n')
 print(json.dumps(summary,ensure_ascii=False),flush=True)
 assert matching,'API catalogue has not synchronized the new data release'
 details=[]
 for key in ['CN:mi_cn:product:21825','CN:mi_cn:product:25466','CN:mi_cn:product:23577']:
  row,_=get('/api/goods/'+quote(key,safe=''));assert row.get('series_release')==byid[key].get('series_release'),key
  assert row.get('release')==byid[key].get('release'),key
  assert row['series_release']['level']=='series'
  details.append(dict(id=key,name=row['name'],url='https://spend.snewbie.site/api/goods/'+quote(key,safe=''),series_release=row['series_release'],release=row.get('release'),matches=True))
 # Cross-generation / capacity exclusions must also hold online.
 for tail in ['21243','21378','23676']:
  row,_=get('/api/goods/'+quote('CN:mi_cn:product:'+tail,safe=''));assert not row.get('series_release'),tail
 summary.update(details=details,negative_detail_checks=['21243','21378','23676'])
 (P/'online-verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 (P/'api-goods-after.json.gz').write_bytes(gzip.compress(raw,mtime=0))
if __name__=='__main__':main()
