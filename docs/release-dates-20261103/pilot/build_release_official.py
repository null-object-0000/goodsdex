import json,re,hashlib,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src');from goodsdex.release_dates import coverage
root=Path('docs/release-dates-20261103/evidence');rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'));captures={json.loads(p.read_text())['url']:(p,json.loads(p.read_text())) for p in root.glob('*.json') if not p.name.startswith('mi-')}
candidates=[]
def evidence(p,o,quote,locator,source_type='official'):
 return dict(url=o['url'],quote=quote,locator=locator,sha256=o['sha256'],captured_at=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),source_type=source_type)
def release(date,e,event='availability'):
 return dict(date=date,granularity='month',source='official',evidence=e,confidence='high',event=event,market='CN')
for p in sorted(root.glob('mi-*.json')):
 o=json.loads(p.read_text());found=[]
 def walk(v,path='$'):
  if isinstance(v,dict):
   if v.get('name') in ('发布时间','上市时间','发布日期','发售时间') and v.get('value') and v.get('isPageShow') is True:found.append((path,v['name'],str(v['value'])))
   for k,x in v.items():walk(x,path+'.'+k)
  elif isinstance(v,list):
   for i,x in enumerate(v):walk(x,f'{path}[{i}]')
 walk(o['raw'])
 vals=[]
 for loc,k,v in found:
  m=re.fullmatch(r'\s*(20\d{2})年\s*(\d{1,2})月\s*(?:\d{1,2}日)?\s*',v)
  if m and 1<=int(m[2])<=12:vals.append((f'{m[1]}-{int(m[2]):02d}',loc,k,v))
 if not vals or len({x[0] for x in vals})!=1:continue
 date,loc,k,v=vals[0];e=evidence(p,o,f'{k}：{v}',loc);e['url']='https://m.mi.com/commodity/detail/'+o['id'].split(':')[-1];e['capture_url']=o['url'];e['request']=o['request']
 candidates.append(dict(family=o['id'],ids=[o['id']],method='explicit_official_parameter',release=release(date,e,'announcement' if k=='发布时间' else 'availability')))
# Reviewed exact product IDs. No generation/year/colour suffix becomes a date.
recipes=[
 ('2025/03/apple-introduces-ipad-air-with-powerful-m3-chip-new-magic-keyboard/', ['ipada16_2025'], '2025-03','搭载 A16 芯片的新款 iPad'),
 ('2026/03/apple-introduces-the-new-ipad-air-powered-by-m4/',['ipadair11_m4_2026','ipadair13_m4_2026'],'2026-03','iPad Air'),
 ('2025/10/apple-introduces-ipad-pro-with-m5/',['ipadpro11_m5_2025','ipadpro13_m5_2025'],'2025-10','iPad Pro'),
 ('2025/10/iphone-air-will-be-available-in-china-beginning-october-22/',['iphoneair'],'2025-10','iPhone Air'),
 ('2026/03/apple-introduces-iphone-17e/',['iphone17e'],'2026-03','iPhone 17e'),
 ('2025/09/apple-introduces-apple-watch-se-3-cn/',['apple-watch-se-3'],'2025-09','Apple Watch SE 3'),
 ('2026/03/apple-introduces-the-new-macbook-air-with-m5/',[x.get('product_id','').split('product:')[-1] for x in rows if x.get('source')=='apple_cn' and 'RO_MBA_M5_' in x.get('product_id','')],'2026-03','MacBook Air'),
 ('2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/',[x.get('product_id','').split('product:')[-1] for x in rows if x.get('source')=='apple_cn' and 'RO_MBP_M5PRO_M5MAX_' in x.get('product_id','')],'2026-03','MacBook Pro'),
 ('2026/08/apple-introduces-mac-studio-with-m5-max-and-m5-ultra/',['RO_MACSTUDIO_M5MAX_M5ULTRA_BET_BES_2026'],'2026-09','Mac Studio'),
 ('2026/08/apple-unveils-powerful-mac-mini-with-m6-and-m5-pro/',['RO_MACMINI_M6_GOO_BET_BES_2026','RO_MACMINI_M5PRO_ULT_2026'],'2026-09','Mac mini'),
]
for suffix,products,date,identity in recipes:
 u='https://www.apple.com.cn/newsroom/'+suffix;p,o=captures[u];t=o['text'];y,mo=map(int,date.split('-'))
 # Anchor the quotation to the stated product where possible (A16 is in a combined announcement).
 start=t.find(identity,350) if 'A16' in identity else 300
 pattern=rf'{mo} 月 \d+ 日[^。]{{0,100}}(?:发售|发货)'
 matches=list(re.finditer(pattern,t[max(0,start):]))
 if not matches:raise ValueError((u,'no explicit availability'))
 m=matches[0];offset=max(0,start);quote=t[offset+max(0,m.start()-180):offset+m.end()+40]
 header=re.search(r'20\d{2} 年 \d+ 月 \d+ 日',t).group();quote=header+' | '+quote
 for product in dict.fromkeys(products):
  key='CN:apple_cn:product:'+product;ids=[r['id'] for r in rows if r.get('product_id')==key]
  if not ids:raise ValueError(key)
  candidates.append(dict(family=key,ids=ids,method='reviewed_exact_product_family',release=release(date,evidence(p,o,quote,'Newsroom: publication header + product pricing/availability paragraph'))))
print('official families',len(candidates),'rows',sum(len(c['ids']) for c in candidates))
Path('data/official/release-dates.json').write_text(json.dumps(dict(schema=1,candidates=candidates),ensure_ascii=False,indent=2)+'\n')
Path('docs/release-dates-20261103/official-recipes.json').write_text(json.dumps(recipes,ensure_ascii=False,indent=2))
