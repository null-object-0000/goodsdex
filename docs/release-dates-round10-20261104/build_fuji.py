import json,pathlib,re,unicodedata,sys
sys.path.insert(0,'docs/release-dates-round10-20261104');from collect import fetch
root=pathlib.Path('docs/release-dates-round10-20261104');rows=json.loads(__import__('gzip').decompress((root/'baseline.json.gz').read_bytes()))
byid={r['id']:r for r in rows}
cs=[]
def add(key,date,event,market,cap,quote,locator,reason):
 row=byid[key];assert cap['status']==200
 txt=pathlib.Path(cap['text_file']).read_text(); assert quote in txt or quote in json.dumps(json.load(open(root/'mi-history-structured.json')),ensure_ascii=False)
 cs.append(dict(family='round10:'+key,ids=[key],name=row['name'],brand=row['brand'],method='official_retrospective',identity_review=reason,capture_file=cap['raw_file'],release=dict(date=date,event=event,market=market,source='official',granularity='month',confidence='high',retrospective=True,evidence={k:cap[k] for k in ('url','sha256','captured_at')})))
 cs[-1]['release']['evidence'].update(quote=quote,locator=locator,source_type='official',capture_type='http_response',capture_file=cap['raw_file'],text_file=cap['text_file'],verified=True)

cap=fetch('https://www.fujifilm.com.cn/cn/zh-hans/news/detail/3880')
for suffix,date,q in [('x-s20','2023-06','2023年6月推出的X-S20'),('x100vi','2024-02','2024年2月，公司推出了采用背照式4020万像素传感器和富士胶片最新处理器的X100VI高端便携式数码相机。')]:
 add('CN:fuji:model:'+suffix,date,'announcement','GLOBAL_REPORTED_BY_CN_OFFICIAL',cap,q,'2023财年财报 / 专业级影像业务正文','仅原文精确机身；官方回溯推出月份，不代表中国首销；不向套机传播')

def norm(s):
 s=unicodedata.normalize('NFKC',s).upper().replace('F1.0','F1')
 return re.sub(r'\s+','',s)
for row in rows:
 if row.get('brand')!='富士' or ':lens:' not in row['id'] or (row.get('release') or {}).get('source')=='official':continue
 name=row['name'].replace('FUJINON ','');matched=[]
 for p in (root/'evidence').glob('*.json'):
  cap=json.load(open(p));
  if '/shop/g/' not in cap['url'] or cap['status']!=200:continue
  text=pathlib.Path(cap['text_file']).read_text();title=text.splitlines()[0]
  # Exact full model; a different package (XF200 with converter) is ineligible.
  title=title.split(' | ')[0].split(':')[0].replace('フジノンレンズ ','')
  title=re.sub('[　 ]*(?:ブラック|シルバー)$','',title)
  if norm(title)!=norm(name):continue
  m=re.search(r'発売日[\s：:]*(20\d\d)年(\d{1,2})月(\d{1,2})日',text)
  if m:matched.append((cap,m))
 if matched:
  assert len({(m[1],m[2]) for _,m in matched})==1
  cap,m=sorted(matched,key=lambda x:x[0]['url'])[0]
  text=pathlib.Path(cap['text_file']).read_text();title=text.splitlines()[0];q=title+'\n'+m[0]
  # Discontiguous title and spec rows retained separately, never fabricate a continuous quote.
  add(row['id'],f'{m[1]}-{int(m[2]):02}','availability','JP',cap,m[0],'商品标题 + 製品仕様/発売日', '完整镜头型号逐字规范化匹配（空格/全半角/F1.0）；日本独立商品历史发售字段，不代表国行首销')
  cs[-1]['release']['evidence']['identity_quote']=title
for suffix,sku in [('x-h2s','16944868'),('x-h2','16944894')]:
 cap=fetch(f'https://mall-jp.fujifilm.com/shop/g/g{sku}/');txt=pathlib.Path(cap['text_file']).read_text();m=re.search(r'発売日\s*(20\d\d)年(\d{1,2})月\d{1,2}日',txt)
 add('CN:fuji:model:'+suffix,f'{m[1]}-{int(m[2]):02}','availability','JP',cap,m[0],'FUJIFILM机身标题 + 製品仕様/発売日','仅该机身日本发售，不传播套机或冒充国行')
 cs[-1]['release']['evidence']['identity_quote']=txt.splitlines()[0]
for suffix,sku in [('x-e5-xf23mmf28-r-wr','16949818'),('x-h2-16-80mm','16944923'),('x-t50-xc15-45mm','16945616')]:
 cap=fetch(f'https://mall-jp.fujifilm.com/shop/g/g{sku}/');txt=pathlib.Path(cap['text_file']).read_text();m=re.search(r'発売日\s*(20\d\d)年(\d{1,2})月\d{1,2}日',txt)
 add('CN:fuji:kit:'+suffix,f'{m[1]}-{int(m[2]):02}','availability','JP',cap,m[0],'完整套机商品标题 + 该套机自己的製品仕様/発売日','相机型号与配套镜头逐项核对；日期来自套机自身页面，未继承机身日期；仅日本市场')
 cs[-1]['release']['evidence']['identity_quote']=txt.splitlines()[0]
for key,path,reason in [
 ('CN:fuji:model:x-t5','cameras/x-t5/','仅X-T5机身日期；官方当前表格同时列出后来上市的XF16-50套机，因此共同発売日不向任何套机传播'),
 ('CN:fuji:lens:xf200mmf2-r-lm-ois-wr','lenses/xf200mmf2-r-lm-ois-wr/','厂商历史型号表产品名精确FUJINON XF200mmF2 R LM OIS WR；与商城增距镜套装分开审核，只采用厂商该镜头自己的日期字段')]:
 cap=fetch('https://www.fujifilm-x.com/ja-jp/products/'+path);txt=pathlib.Path(cap['text_file']).read_text();m=re.search(r'発売日\s*(20\d\d)年(\d{1,2})月\d{1,2}日',txt)
 add(key,f'{m[1]}-{int(m[2]):02}','availability','JP',cap,m[0],'製品名 + 発売日 历史产品表',reason)
 cs[-1]['release']['evidence']['identity_quote']=txt[txt.rfind('製品名'):txt.rfind('製品名')+180]
(root/'new-candidates.json').write_text(json.dumps(cs,ensure_ascii=False,indent=2)+'\n');print('fuji candidates',len(cs));print('\n'.join(c['name']+' '+c['release']['date'] for c in cs))
