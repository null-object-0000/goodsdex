import json,gzip,hashlib,sys,re
from pathlib import Path
from bs4 import BeautifulSoup
sys.path.insert(0,'src');from goodsdex.release_media import check
rows=json.loads(Path('docs/release-coverage/after.json').read_text());byid={r['id']:r for r in rows}
p=Path('data/third-party/l5-reviewed.json');bundle=json.loads(p.read_text())
for sku,url,day,terms in [('136671','https://www.ithome.com/0/686/332.htm','2023-04-13',['DJI DL 18 mm F2.8 ASPH']),('134691','https://www.ithome.com/0/678/043.htm','2023-03-07',['DL PZ 17-28','T3.0','ASPH']),('158331','https://www.ithome.com/0/739/308.htm','2023-12-14',['禅思 X9-8K'])]:
 cap=next(json.loads(f.read_text()) for f in Path('docs/release-coverage/L5/research-captures').glob('*.json') if json.loads(f.read_text()).get('url')==url)
 raw=gzip.decompress(Path(cap['capture_file']).read_bytes());soup=BeautifulSoup(raw,'html.parser');body=soup.select_one('#paragraph') or soup.select_one('.post_content');text=body.get_text(' ',strip=True)
 row=byid['CN:dji:sku:'+sku];identity={k:v for k,v in row.items() if k in ('id','name','brand','model','sku','params','attributes','variant_attributes')}
 ev={k:cap[k] for k in ('url','sha256','captured_at','capture_file')};ev.update(quote=text[:700],identity_quote=text,source_type='third_party',locator='div.post_content: release event and explicitly named separately sold lens/camera',encoding='utf-8',upstream_origin='ithome.com')
 dest=Path('data/third-party/l5-captures')/Path(cap['capture_file']).name;dest.write_bytes(gzip.compress(raw,mtime=0));ev['capture_file']=str(dest)
 e=dict(id=row['id'],name=row['name'],brand=row['brand'],identity_kind='exact_product',identity_terms=terms,identity_sha256=hashlib.sha256(json.dumps(identity,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),identity_reason='原文逐项写明单独售卖的精确镜头焦段/光圈或X9-8K云台相机；不复制无人机/电影机套装日期给未点名配件',assertion=dict(source='third_party',date=day[:7],granularity='month',event='announcement',market='CN',reported_at=day,first_report_review='同步发布精确配件并明示独立定价的首发原文，默认仅到月',evidence=ev))
 check(e,row);bundle['entries'].append(e);print('ADD',row['name'])
p.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
