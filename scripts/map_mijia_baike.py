import json,zipfile,unicodedata,re,collections,hashlib,random
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--goods',type=Path,required=True)
parser.add_argument('--apk',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=args.output
root.mkdir(parents=True,exist_ok=True)
r=json.load(args.goods.open()); rows={x['id']:x for x in r if x['id'].startswith('CN:mi_cn:product:')}
with zipfile.ZipFile(args.apk) as z: raw=z.read('assets/device_config/plugin_config_cn-zh_cn')
devices=json.loads(raw)['result']['devices']['list']
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).casefold())
byname=collections.defaultdict(set)
for d in devices:byname[norm(d['name'])].add(d['model'])
maps={k:{'id':k,'old_name':x['name'],'models':sorted(byname[norm(x['name'])]),'method':'apk_exact_name'} for k,x in rows.items() if byname[norm(x['name'])]}
links=collections.defaultdict(set)
for p in (root/'raw').glob('*.json'):
 if p.name=='miot-instances.json':continue
 x=json.loads(p.read_text());d=x.get('response',{}).get('data') or {};u=(d.get('buyUrl') or {}).get('channelUrl',''); parsed=urlsplit(u)
 if parsed.hostname not in ('m.mi.com','www.mi.com'):continue
 q=parse_qs(parsed.query);pid=(q.get('product_id') or q.get('commodityId') or [''])[0];key='CN:mi_cn:product:'+pid
 if key in rows:links[key].add(x['model'])
for k,ms in links.items():maps[k]={'id':k,'old_name':rows[k]['name'],'models':sorted(ms),'method':'baike_official_shop_link'}
(root/'mapping.json').write_text(json.dumps({'schema':1,'snapshot_sha256':hashlib.sha256(args.goods.read_bytes()).hexdigest(),'catalog_asset_sha256':hashlib.sha256(raw).hexdigest(),'apk_sha256':hashlib.sha256(args.apk.read_bytes()).hexdigest(),'apk_source_url':'https://app.mi.com/details?id=com.xiaomi.smarthome','miot_catalog_url':'https://miot-spec.org/miot-spec-v2/instances?status=all','population':len(rows),'items':list(maps.values())},ensure_ascii=False,indent=2))
sample=random.Random(20261106).sample(sorted(rows),50)
(root/'sample-50.json').write_text(json.dumps([maps.get(k,{'id':k,'old_name':rows[k]['name'],'models':[],'method':'unresolved'}) for k in sample],ensure_ascii=False,indent=2))
(root/'apk-catalog.json').write_text(json.dumps([{'model':d['model'],'name':d['name'],'cate_name':d['cate_name']} for d in devices],ensure_ascii=False))
print('population',len(rows),'mapped',len(maps),'unique',sum(len(x['models'])==1 for x in maps.values()),'sample unique',sum(len(maps.get(k,{}).get('models',[]))==1 for k in sample),'sample candidate',sum(k in maps for k in sample),'shop',len(links))
print([(k,rows[k]['name'],sorted(v)) for k,v in list(links.items())[:8]])
