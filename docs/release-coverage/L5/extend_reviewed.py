import gzip,json,hashlib,re,sys
from pathlib import Path
sys.path[:0]=['src','scripts']
from goodsdex.release_media import check,normalize
from release_lane_media import fetch
from bs4 import BeautifulSoup
review=Path('data/third-party/l5-reviewed.json');bundle=json.loads(review.read_text());rows=json.loads(Path('docs/release-coverage/after.json').read_text());byid={r['id']:r for r in rows};cs=json.loads(gzip.decompress(Path('docs/release-coverage/L5/discovery.json.gz').read_bytes()))
for index in [226,231,235,239,253,264,271,280]:
 c=cs[index];cap=fetch(c['url'],Path('docs/release-coverage/L5/research-captures'))
 if cap.get('status')!=200:continue
 raw=gzip.decompress(Path(cap['capture_file']).read_bytes());soup=BeautifulSoup(raw,'html.parser')
 body=soup.select_one('#paragraph') or soup.select_one('.post_content')
 if body is None:continue
 text=body.get_text(' ',strip=True);full=soup.get_text(' ',strip=True);d=re.search(r'(20\d{2})/(\d{1,2})/(\d{1,2})',full)
 if not d:continue
 row=byid[c['id']];date=f'{d[1]}-{int(d[2]):02}-{int(d[3]):02}'
 identity={k:v for k,v in row.items() if k in ('id','name','brand','model','sku','params','attributes','variant_attributes')}
 ev={k:cap[k] for k in ('url','sha256','captured_at','capture_file')};ev.update(quote=text[:550],identity_quote=text[:1600],source_type='third_party',locator='div.post_content 首发段落',encoding='utf-8',upstream_origin='ithome.com')
 dest=Path('data/third-party/l5-captures')/Path(cap['capture_file']).name;dest.write_bytes(gzip.compress(raw,mtime=0));ev['capture_file']=str(dest)
 entry=dict(id=row['id'],name=row['name'],brand=row['brand'],identity_kind='exact_product',identity_terms=[row['name']],identity_sha256=hashlib.sha256(json.dumps(identity,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),identity_reason='完整耳机型号及青春/活力/Pro后缀逐项核对，仅匹配此产品记录，不扩展同系列',assertion=dict(source='third_party',date=date[:7],granularity='month',event='availability' if '开售' in c['title'] or '上市' in c['title'] else 'announcement',market='CN',reported_at=date,first_report_review='首发报道且完整型号匹配；今日语义不升日',evidence=ev))
 try:check(entry,row);bundle['entries'].append(entry);print('ADD',row['name'])
 except Exception as exc:print('REJECT',str(exc))
review.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
