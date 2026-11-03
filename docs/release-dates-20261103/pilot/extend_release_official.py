import json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
path=Path('data/official/release-dates.json');b=json.loads(path.read_text());rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'));root=Path('docs/release-dates-20261103/evidence')
recipes=[
 ('83e931e0b601057b',['iphone18pro','iphone18promax'],'2026-09',False),
 ('75b63acd70c22221',['iphone17'],'2025-09',False),
 ('4f9307ba7e8802cf',[r['product_id'].split('product:')[1] for r in rows if r.get('source')=='apple_cn' and 'MBN_2026_' in r.get('product_id','')],'2026-03',False),
]
for needle,products,date in [
 ('introducing-apple-watch-series-12-with-the-all-new-health-sensing-system/',['apple-watch-series-12'],'2026-09'),
 ('apple-unveils-apple-watch-ultra-4/',['apple-watch-ultra-4'],'2026-09'),
 ('apple-introduces-airpods-5/',['airpods-5'],'2026-09')]:
 f=next(p for p in root.glob('*.json') if json.loads(p.read_text())['url'].endswith('/2026/09/'+needle));recipes.append((f.stem,products,date,False))
# Only explicit, not-yet-reached official sale schedules; never mark as released.
for needle,products in [
 ('apple-gives-ipad-mini-its-biggest-update-ever/',['ipadmini_a20pro_2026']),
 ('apple-introduces-the-new-14-inch-macbook-pro-with-m6/',[r['product_id'].split('product:')[1] for r in rows if 'RO_MBP_M6_' in r.get('product_id','')]),
 ('apple-unveils-new-imac-with-m6/',[r['product_id'].split('product:')[1] for r in rows if 'RO_IMAC_M6_' in r.get('product_id','')])]:
 f=next(p for p in root.glob('*.json') if json.loads(p.read_text())['url'].endswith('/2026/10/'+needle));recipes.append((f.stem,products,'2026-11',True))
for key,products,date,planned in recipes:
 p=root/(key+'.json');doc=json.loads(p.read_text());t=doc['text'];m=int(date[5:]);year=date[:4]
 header=re.search(r'20\d{2} 年 \d+ 月 \d+ 日',t).group()
 pattern=rf'(?:{m} 月 \d+ 日|本月 \d+ 日)[^。]{{0,80}}(?:发售|发货)'
 a=next(re.finditer(pattern,t));quote=header+' | '+t[max(0,a.start()-180):a.end()+110]
 if '本月' in a.group():assert re.search(rf'{year} 年 {m} 月',header)
 e=dict(url=doc['url'],quote=quote,locator='Newsroom publication header + explicit sale/schedule sentence',source_type='official',sha256=doc['sha256'],captured_at=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat())
 for product in dict.fromkeys(products):
  family='CN:apple_cn:product:'+product;ids=[r['id'] for r in rows if r.get('product_id')==family];assert ids
  b['candidates'].append(dict(family=family,ids=ids,method='reviewed_exact_product_family',release=dict(date=date,granularity='month',source='official',confidence='high',market='CN',event='planned_availability' if planned else 'availability',evidence=e)))
path.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
print('official extension',sum(len(c['ids']) for c in b['candidates'] if c['release']['source']=='official'),'planned',sum(len(c['ids']) for c in b['candidates'] if c['release']['event']=='planned_availability'))
