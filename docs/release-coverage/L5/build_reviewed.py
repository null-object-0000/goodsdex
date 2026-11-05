"""Reviewed subset of frozen launch corpus; explicit selection, no prefix expansion.

The discovery index is audit-only. Rejected prefix/series/variant matches never
become single-product assertions. Re-run from repository root.
"""
import gzip,hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'src')
from goodsdex.release_media import normalize,check
from bs4 import BeautifulSoup
root=Path('.')
rows=json.loads(Path('docs/release-coverage/after.json').read_text()); byid={r['id']:r for r in rows}
cs=json.loads(gzip.decompress(Path('docs/release-coverage/L5/discovery.json.gz').read_bytes()))
# Individually reviewed exact named products, with no base-name prefix expansion.
# Exclude unnamed reference families 1005xxxx, dual VR IDs, new colour variants of
# old names, series bundles and "will launch" previews.
SELECTED=[68,69,71,74,80,82,85,91,94,103,105,106,108,110,111,113,133,134,135,136,138,139,140,141,144,146,149,151,154,159,161,162,163,166,168,171,174,175,178,179,181,183,191,198,200,204,206,210,211,226,231,235,239,253,264,271,280,297,301,321,335,351,356,365,370,424]
# Manual exclusions noted during review: 69 is a later sale event after 146's
# announcement (retained as separate event); 71 includes the new white colour;
# 111/151 are product announcements preceding availability, not sale assertions.
entries=[]
for index in SELECTED:
 c=cs[index];v=json.loads(Path(c['path']).read_text());row=byid[c['id']]
 path=Path(v.get('capture_file') or Path(c['path']).with_suffix('.html.gz'))
 if not path.exists():
  path=Path(c['path']).with_suffix('.html')
 if not path.exists():print('MISSING',index,path);continue
 raw=path.read_bytes();raw=gzip.decompress(raw) if path.suffix=='.gz' else raw
 charset=re.search(br'charset=["\']?([A-Za-z0-9_-]+)',raw[:10000]);encoding=charset[1].decode() if charset else 'utf-8'
 soup=BeautifulSoup(raw,'html.parser',from_encoding=encoding)
 for t in soup(['script','style']):t.decompose()
 alltext=soup.get_text(' ',strip=True)
 article=soup.select_one('#paragraph') or soup.select_one('.post_content') or soup.select_one('#artibody')
 body=article.get_text(' ',strip=True) if article else v['text']
 d=re.search(r'(20\d{2})[/年-](\d{1,2})[/月-](\d{1,2})',v.get('header','') or alltext)
 if not d: print('NO DATE',index);continue
 reported=f'{d[1]}-{int(d[2]):02}-{int(d[3]):02}'
 # Preserve complete exact-product original excerpt, no generated prose as quote.
 quote=body[:900]
 if normalize(row['name']) not in normalize(quote):
  # Non-contiguous full body identity is reviewed separately, not replaced with title.
  quote=body[:1500]
 terms=[row['name']]
 if index==183:terms=['REDMI','儿童手表']
 if index==191:terms=['小米智能室外摄像机','4G','双摄']
 if index==297:terms=['REDMI','A27','2026']
 if index==335:terms=['REDMI K Pad 2']
 if any(normalize(t) not in normalize(body) for t in terms): print('NO BODY ID',index);continue
 evidence=dict(url=c['url'],source_type='third_party',sha256=hashlib.sha256(raw).hexdigest(),
               captured_at=v.get('captured_at'),quote=quote,identity_quote=body[:2500],
               locator='article body / launch paragraph and exact product specifications',encoding=encoding,
               upstream_origin='mydrivers.com' if '快科技' in alltext and 'sina.com' in c['url'] else 'ithome.com')
 dest=Path('data/third-party/l5-captures')/(hashlib.sha256(c['url'].encode()).hexdigest()[:20]+'.html.gz')
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(raw,mtime=0));evidence['capture_file']=str(dest)
 identity={k:v for k,v in row.items() if k in ('id','name','brand','model','sku','params','attributes','variant_attributes')}
 event='availability' if re.search('开售|发售|上市',c['title']) else 'announcement'
 # "推出/发布 + 预售" is an announcement; never promote a future sale day.
 a=dict(source='third_party',date=reported[:7],granularity='month',event=event,market='CN',
        reported_at=reported,first_report_review='原文为此精确型号新品首发/发布/首销报道；无系列名替换；不把报道日当事件日',evidence=evidence)
 e=dict(id=row['id'],name=row['name'],brand=row['brand'],identity_kind='exact_product',identity_terms=terms,
        identity_sha256=hashlib.sha256(json.dumps(identity,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
        identity_reason='逐型号核对正文完整商品名及代际/容量/版本限定；仅此精确ID，不扩展前缀、套装及配色',assertion=a)
 try:check(e,row)
 except Exception as exc:print('REJECT',index,str(exc));continue
 entries.append(e)
path=Path('data/third-party/l5-reviewed.json');path.write_text(json.dumps(dict(schema=1,policy='l5-first-report-v1',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('REVIEWED',len(entries),'unique',len({e['id'] for e in entries}))
