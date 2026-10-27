#!/usr/bin/env python3
"""DJI CN goods: enumerate -> parse cached detail JSON -> official specs -> append.

python scripts/dji_catalog.py collect [--offline] [--root data/dji]
python scripts/dji_catalog.py publish --public /path/to/data-worktree/public
Persistent request budget covers all runs in the same root. For a fresh observation,
use a new root; existing captures are deliberately never silently refreshed.
"""
import argparse
from collections import Counter
import datetime as dt
import html
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from dji_enumerate import enumerate_catalog
from dji_html import embedded, parameters, plain
from dji_http import Client, dump

ROOT=Path(__file__).resolve().parents[1]
BASE='https://store.dji.com/cn/product/'
# Classification only; these names never manufacture technical parameters.
ACCESSORY=re.compile(r'电池|充电|桨叶|螺旋桨|保护|镜头盖|收纳|背包|单肩包|套袋|转接|连接线|数据线|延长|支架|安装|底座|快拆|贴纸|滤镜|ND 镜|广角镜|增广镜|挂绳|磁吸|浮力|防水壳|防风|发射器|接收器|遥控器|摇杆|眼镜|镜头|适配器|提壶|手柄|脚架|配重|拓展|扩展|信号增强|束带|背带|清洁|尘袋|滚刷|边刷|拖布|集尘|润滑|电源线|电缆|线材|夹具|手机夹|腕带|腕绳|自拍杆|头带|胸带|头盔|骑行|车把|吸盘|弯臂|万向|冷靴|螺丝|电机|跟焦|激光雷达|麦克风线|线|模块|配件|镜片|柔光镜|微距镜|补光灯|固定|连接头|追踪套件|太阳能|行车闪充|插座|Expansion Battery|漂浮块|挂脖|减震|硅胶|充气|遮光|聚光|电源分配|推车|兔笼|手轮|LiDAR|快装板|双手持|4D Flex|桨|背夹|磁铁|手绳|附件|开发板|雷达|云台组件|Ronin 图传')
MACHINE_PATTERNS=[
 (r'^(?:DJI |御 )?(?:Mavic|Air|Mini|Lito|Flip|Neo|Avata|FPV|Inspire|Matrice|经纬|精灵|悟|特洛|Tello)\b|^DJI (?:Mavic|Air|Mini|Lito|Flip|Neo|Avata|FPV|Inspire|Matrice)', '无人机','DJI'),
 (r'^(?:Osmo |DJI )?(?:Action|Nano|360)\b|^Osmo (?:Action|Nano|360)', '运动相机','Osmo'),
 (r'^(?:Osmo Pocket|DJI Pocket|Osmo$)', '相机','Osmo'),
 (r'^DJI Ronin 4D', '相机','Ronin'),
 (r'^(?:Osmo Mobile|DJI OM|DJI RS|DJI RSC|如影|DJI Ronin)', '云台','Ronin'),
 (r'^DJI Mic', '麦克风','Mic'),
 (r'^DJI Power', '户外电源','Power'),
 (r'^DJI ROMO', '扫地机器人','ROMO'),
 (r'^(?:机甲大师|RoboMaster|DJI RoboMaster)', '教育机器人','RoboMaster'),
 (r'^DJI (?:SDR|Transmission|Focus Pro)', '影像传输与控制设备','Ronin'),
]


def classify(v, siblings):
    name=v.get('title','')
    if re.match(r'^DJI Mic(?: Mini)?(?: \d+[A-Z]?)?\s*[（(](?:手机版)?[一两三四单双12].*(?:发.*收|拖)',name):
        return 'machine','麦克风','Mic'
    # A bundle inherits its actual hardware constituent, not the accessory in its title.
    if v.get('type')=='Bundle':
        parts=[siblings.get(x.get('id'),{}) for x in v.get('items',[])]
        for p in parts:
            if p and p.get('type')!='Bundle':
                k,c,s=classify(p,{})
                if k=='machine': return k,c,s
    for pattern, category, series in MACHINE_PATTERNS:
        if re.search(pattern,name,re.I):
            # Genuine main hardware is explicitly marked by the storefront.
            main=v.get('variantCategory')=='dji_care_main'
            if main or not ACCESSORY.search(name):
                if 'Mobile' in name or 'DJI OM' in name: series='Osmo'
                if category=='无人机':
                    m=re.search(r'Mavic|Air|Mini|Lito|Flip|Neo|Avata|FPV|Inspire',name,re.I)
                    if m:series=m[0]
                return 'machine',category,series
            return 'accessory',category+'配件',series
    if re.search(r'^(?:DJI )?(?:Matrice|经纬|Tello|特洛|机甲大师|RoboMaster)',name,re.I) and not ACCESSORY.search(name):return 'machine','无人机' if not re.search('机甲|RoboMaster',name,re.I) else '教育机器人','DJI'
    if re.search(r'ROMO|扫地|尘袋|拖布|滚刷|边刷',name,re.I): return 'accessory','扫地机器人配件','ROMO'
    if re.search(r'Power',name,re.I):return 'accessory','户外电源配件','Power'
    return 'accessory','摄影器材配件',None


def parse_detail(source, url, fetched_at=None):
    ld,state,_=embedded(source)
    variants=state.get('products',{}).get('variants',[])
    meta=state.get('shoppingFlow',{}).get('meta',{})
    siblings={v.get('id'):v for v in variants}
    products={p.get('id'):p for p in state.get('products',{}).get('products',[])}
    family=set(meta.get('slugs',[]))|{urlsplit(url).path.rsplit('/',1)[-1]}
    product=next((x for x in ld if isinstance(x,dict) and x.get('@type')=='Product'),{})
    offers=product.get('offers') or {}
    localization=state.get('localization',{})
    currency=(localization.get('currency') or {}).get('code')
    cny=isinstance(offers,dict) and (offers.get('priceCurrency')=='CNY' or (not offers.get('priceCurrency') and localization.get('country')=='cn' and currency=='CNY'))
    rows=[]; excluded=[]
    for v in variants:
        ident=v.get('id');name=v.get('title');slug=v.get('slug')
        reason=None
        if v.get('type') not in {'Sku','Bundle'} or v.get('virtual') or re.search(r'Care|随心换|保障|延保|保险|课程|授权码|订金|定金|预付款|责任险|司空|Flighthub|大疆智图|大疆智模|DJI Terra|DJI Modify|软件|订阅|授权',name or '',re.I):reason='service_or_virtual'
        elif re.match(r'雷克沙|北桔|PORTABLE|SanDisk|Lexar|闪迪|Livox',name or '',re.I):reason='third_party_brand'
        elif (v.get('status') or {}).get('code')!='on_sale':reason='not_on_sale'
        elif not isinstance(ident,int) or isinstance(ident,bool) or not name or not slug:reason='missing_identity_or_name'
        if reason:
            excluded.append({'id':ident,'name':name,'reason':reason,'status':v.get('status')});continue
        price=v.get('price')
        if not cny or not str(v.get('priceLabel','')).startswith(('¥','￥')) or not isinstance(price,(int,float)) or isinstance(price,bool) or price<=0:price=None
        cover=v.get('cover') or {}
        image=cover.get('origin') or cover.get('original') or cover.get('ultra')
        kind,category,series=classify(v,siblings)
        params={}
        if v.get('attrs'):params['官方销售选项']=v['attrs']
        product_data=products.get(v.get('productId'),{})
        boxes=v.get('inTheBoxes') or product_data.get('inTheBoxes')
        if boxes:params['包装清单']=[{k:x.get(k) for k in ['name','quantity','remark']} for x in boxes]
        if product_data.get('specs'):params['商城商品规格']=product_data['specs']
        if v.get('items'):
            params['套装组成']=[{'mall_id':x.get('id'),'name':siblings.get(x.get('id'),{}).get('title'),'quantity':x.get('quantity')} for x in v['items']]
        if v.get('bundleDescription'):params['官方套装说明']=plain(v['bundleDescription'])
        if v.get('specs'):params['商城规格']=v['specs']
        rows.append({'id':f'CN:dji:sku:{ident}','mall_sku_id':ident,'brand':'大疆','name':name,
          'kind':kind,'category':category,'series':series,'price':price,'price_kind':'listing',
          'image':urljoin(url,image) if image else None,'source_url':BASE+slug+'?vid='+str(ident),
          'catalog_identity':'dji_mall_json','lookup_keys':['大疆','DJI'],'model':None,'model_or_part_number':None,
          'variant_hint':name,'params':params,'fetched_at':fetched_at,
          'family_id':f'CN:dji:sku:{meta.get("mainVariant")}' if slug in family and meta.get('mainVariant') else None,
          'source':'dji_mall_json','_family_match':slug in family,'_overview':meta.get('overviewUrl') if slug in family else None,
          '_ean':v.get('ean'),'_evidence_url':url,'_sale_status':v.get('status'),'_slug':slug})
    return rows,excluded,meta


def specs_for(client,overview):
    if not overview:return [],None
    u=urlsplit(overview)
    if u.hostname!='www.dji.com':return [],None
    p=u.path.strip('/')
    if p.startswith('cn/'):p=p[3:]
    target='https://www.dji.com/cn/'+p.rstrip('/')+'/specs'
    source,r=client.fetch(target)
    refresh=re.search(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*URL=([^"\' >]+)',source,re.I)
    if refresh:
        target=urljoin(target,html.unescape(refresh[1]));source,r=client.fetch(target)
    return parameters(source) if r['status']==200 else [],r.get('url',target)


def collect(args):
    client=Client(args.root,args.offline)
    state=enumerate_catalog(client)
    records={};excluded={};failures=[]
    inv=json.loads((args.root/'inventory.json').read_text())
    listed=inv['items']
    for index,url in enumerate(sorted(state['detail_products']),1):
        if url in state.get('unavailable',{}) and url not in state['pages']:continue
        source,r=client.fetch(url)
        if r['status']!=200:
            failures.append({'url':url,'reason':'http_'+str(r['status'])});continue
        rows,skips,meta=parse_detail(source,url,r.get('fetched_at'))
        if not rows and not skips:failures.append({'url':url,'reason':'no_embedded_variants'})
        for x in skips:excluded[str(x['id'])]=x
        for row in rows:
            listing=listed.get(str(row['mall_sku_id']))
            if listing and (listing.get('status')or{}).get('code')!='on_sale':
                excluded[str(row['mall_sku_id'])]={'id':row['mall_sku_id'],'name':row['name'],'reason':'listing_not_on_sale'}
                continue
            old=records.get(row['id'])
            # Prefer its own family page over incidental recommendations.
            if old is None or (row['_family_match'] and not old['_family_match']):records[row['id']]=row
        if index%50==0:
            dump(args.root/'catalog.checkpoint.json',list(records.values()))
            client.log(f'parsed {index} product pages; {len(records)} unique on-sale SKUs; checkpoint')
    missing_listed=[];listing_aliases=[]
    for ident,item in listed.items():
        name=item.get('title','')
        if (item.get('status')or{}).get('code')!='on_sale':continue
        if re.search(r'Care|随心换|保障|延保|保险|课程|授权码|订金|定金|预付款|责任险|司空|Flighthub|大疆智图|大疆智模|DJI Terra|DJI Modify|软件|订阅|授权',name,re.I) or re.search('care|refresh|warranty|service',item['slug']):continue
        if re.match(r'雷克沙|北桔|PORTABLE|SanDisk|Lexar|闪迪|Livox',name,re.I):continue
        if 'CN:dji:sku:'+ident not in records:
            matches=[r for r in records.values() if r['_slug']==item['slug'] and r['name']==name and item.get('ean') and r['_ean']==item['ean']]
            if len(matches)==1:
                listing_aliases.append({'listing_id':ident,'detail_id':matches[0]['id'],'slug':item['slug'],'name':name,'ean':item['ean'],'rule':'exact slug + exact official title + exact EAN; identity remains detail JSON id'})
                continue
            missing_listed.append({'id':ident,'name':name,'reason':'listed_sku_not_parsed','url':BASE+item['slug']})
    failures.extend(missing_listed)
    dump(args.root/'listing-id-aliases.json',listing_aliases)
    specs_cache={}
    for index,row in enumerate(records.values(),1):
        overview=row['_overview']
        if overview:
            if overview not in specs_cache:specs_cache[overview]=specs_for(client,overview)
            specs,spec_url=specs_cache[overview]
            if specs:
                row['params']['官网系列规格']=specs
                row['params']['规格适用范围']='官网系列/部件规格原文，不代表套装总重或所有配色共享规格'
                row['specs_source_url']=spec_url
            else:failures.append({'url':spec_url,'id':row['id'],'reason':'specs_unavailable'})
        if index%50==0:
            dump(args.root/'catalog.checkpoint.json',list(records.values()))
            client.log(f'specs processed {index}/{len(records)}; checkpoint')
    dump(args.root/'field-evidence.json',[{'id':r['id'],'evidence_url':r['_evidence_url'],'sale_status':r['_sale_status'],'family_match':r['_family_match']} for r in records.values()])
    public=[{k:v for k,v in row.items() if not k.startswith('_')} for row in records.values()]
    public.sort(key=lambda x:x['mall_sku_id'])
    dump(args.root/'catalog.json',public)
    dump(args.root/'exclusions.json',list(excluded.values()))
    dump(args.root/'failures.json',failures)
    summary={'enumerated_links':len(state['products']),'enumeration_pages':len(state['pages']),
             'inventory_categories':{k:v['total'] for k,v in inv['categories'].items()},
             'inventory_unique_variants':len(listed),'inventory_complete':inv['complete'],'missing_listed':len(missing_listed),'listing_id_aliases':len(listing_aliases),
             'detail_links':len(state['detail_products']),'pending':len(state['pending']),'success_product_pages':sum('/product/' in u and r['status']==200 for u,r in state['pages'].items()),
             'sku_count':len(public),'by_kind':dict(Counter(x['kind'] for x in public)),
             'technical_params':sum(any(x['params'].get(k) for k in ['官网系列规格','商城规格','商城商品规格']) for x in public),
             'packaging':sum(bool(x['params'].get('包装清单') or x['params'].get('套装组成')) for x in public),
             'fields':{key:sum(bool(x.get(key)) for x in public) for key in ['name','price','image','source_url','params','specs_source_url']},
             'failure_reasons':dict(Counter(x['reason'] for x in failures)),
             'exclusion_reasons':dict(Counter(x['reason'] for x in excluded.values())),
             'total_requests':client.used+2,'network_this_run':client.network,'delay':client.delay}
    dump(args.root/'summary.json',summary);client.log(json.dumps(summary,ensure_ascii=False))


def append_only(old, additions):
    ids=[x['id'] for x in old]
    seen=set(ids);new=[]
    for x in additions:
        if x['id'] not in seen:new.append(x);seen.add(x['id'])
    result=old+new
    assert result[:len(old)]==old
    assert len(result)==len(old)+len(new)
    assert not set(ids)-{x['id'] for x in result}
    return result,{'old_count':len(old),'old_unique_ids':len(set(ids)),'added':len(new),'new_count':len(result),'new_unique_ids':len(seen),'missing_existing_ids':0,'existing_rows_unchanged':result[:len(old)]==old}


def publish(args):
    source=args.public/'goods.json'
    old=json.loads(source.read_text())
    incoming=json.loads((args.root/'catalog.json').read_text())
    if not incoming:raise ValueError('empty DJI catalog')
    result,audit=append_only(old,incoming)
    meta_path=args.public/'meta.json';meta=json.loads(meta_path.read_text())
    meta.update(generated_at=dt.datetime.now(dt.timezone.utc).isoformat(),count=len(result),
                by_kind=dict(Counter(x.get('kind') or 'unknown' for x in result)),
                with_price=sum(x.get('price') is not None for x in result),
                brands=dict(Counter(x.get('brand') or ('小米' if x['id'].startswith('CN:mi_cn:') else 'unknown') for x in result)))
    dump(args.root/'publish-audit.json',audit)
    dump(source,result);dump(meta_path,meta)
    print(json.dumps(audit,ensure_ascii=False))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('command',choices=['collect','publish'])
    ap.add_argument('--root',type=Path,default=ROOT/'data/dji');ap.add_argument('--offline',action='store_true')
    ap.add_argument('--public',type=Path,default=ROOT/'public');args=ap.parse_args()
    collect(args) if args.command=='collect' else publish(args)
