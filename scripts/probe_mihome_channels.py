"""Capture anonymous channel search evidence with exact-identity gates."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
import urllib.parse
import re
from discover_mihome_gaps import norm,save
ROOT=Path(__file__).resolve().parents[1]/'docs/mihome-gap-20261106'
HEAD={'User-Agent':'Mozilla/5.0','Referer':'https://www.mi.com/','Accept':'*/*'}

def fetch(url,body=None,headers=None):
    key=hashlib.sha256((url+json.dumps(body,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
    p=ROOT/'raw'/f'{key}.json.gz';p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():return json.loads(gzip.decompress(p.read_bytes()))
    e=dict(url=url,body=body,captured_at=datetime.now(timezone.utc).isoformat())
    try:
        req=urllib.request.Request(url,data=json.dumps(body,ensure_ascii=False).encode() if body is not None else None,headers=headers or HEAD)
        with urllib.request.urlopen(req,timeout=20) as r:raw=r.read(5*1024*1024);e.update(status=r.status,sha256=hashlib.sha256(raw).hexdigest(),raw=raw.decode())
        txt=e['raw'];txt=re.sub(r'^cb\(', '',txt);txt=re.sub(r'\);?\s*$','',txt);e['response']=json.loads(txt)
    except Exception as exc:e['error']=str(exc)
    p.write_bytes(gzip.compress(json.dumps(e,ensure_ascii=False).encode(),mtime=0));e['file']=str(p.relative_to(ROOT));return e

def mi_search(name):
    url='https://api2.order.mi.com/search/index?'+urllib.parse.urlencode(dict(query=name,page_index=1,page_size=40,filter_tag=0,main_sort=0,province_id='',city_id='',sort_by='asc',callback='cb'))
    e=fetch(url);r=e.get('response',{});data=r.get('data') or {};cs=[]
    for group in data.get('pc_list') or []:
        for c in group.get('commodity_list') or []:cs.append(dict(c,product_id=(re.search(r'&pid=(\d+)', c.get('log_code','')) or [None,group.get('product_id')])[1]))
    return dict(url=url,error=e.get('error') or (None if r.get('code') in (0,200) and 'pc_list' in data else 'api_or_schema_error'),total=data.get('total'),candidates=cs)

def yp_search(name):
    body=[{}, {'query':[{'queryName':name,'queryType':0,'rule':[]}],'sortBy':0,'pageIdx':0,'strategyInfo':None,'filter':None,'baseParam':{'imei':'','clientVersion':'','ypClient':3},'source':'searchPage','recentAddress':None,'requestExtraInfo':{},'pageSize':40}]
    url='https://www.xiaomiyoupin.com/mtop/market/search/v2/doSearch'
    e=fetch(url,body,{'Content-Type':'application/json','X-Yp-App-Source':'front-PC','X-User-Agent':'channel/youpin platform/youpin.pc','User-Agent':'Mozilla/5.0'})
    r=e.get('response',{});cs=[x['data']['goodsInfo'] for x in (r.get('data') or {}).get('data',{}).get('goods',[]) if x.get('data',{}).get('goodsInfo')]
    return dict(url=url,error=e.get('error') or (None if r.get('code')==0 else 'api_or_schema_error'),candidates=cs)

def probe(d):
    e=fetch('https://home.mi.com/cgi-op/api/v1/baike/v2/product?'+urllib.parse.urlencode(dict(model=d['model'])));r=e.get('response',{});b=r.get('data') or {}
    mi=mi_search(d['name']);yp=yp_search(d['name']);links=[]
    if b.get('model')==d['model'] and b.get('pdId')==d['pd_id']:
        buy=b.get('buyUrl') or {};u=buy.get('channelUrl') or '';links.append(u) if u else None
    matches=[]
    for c in mi['candidates']:
        if norm(c.get('name'))==norm(d['name']):matches.append(dict(channel='mi_cn',product_id=str(c['product_id']),name=c['name'],price=c.get('price'),image=c.get('image'),source_url='https://www.mi.com/shop/buy/detail?product_id='+str(c['product_id']),identity='exact_name'))
    for c in yp['candidates']:
        if norm(c.get('name'))==norm(d['name']):matches.append(dict(channel='youpin',product_id=str(c['gid']),name=c['name'],price_fen=c.get('priceMin'),image=c.get('img800s') or c.get('imgSquare'),source_url='https://www.xiaomiyoupin.com/detail?gid='+str(c['gid']),identity='exact_name'))
    for u in links:
        p=urllib.parse.urlsplit(u);q=urllib.parse.parse_qs(p.query);pid=(q.get('product_id') or q.get('commodityId') or [''])[0]
        if p.hostname in ('m.mi.com','www.mi.com') and pid.isdigit():
            v=fetch('https://api2.order.mi.com/product/view?'+urllib.parse.urlencode(dict(product_id=pid,version=2)));data=v.get('response',{}).get('data') or {};prod=data.get('product') or {};gs=(data.get('goodsInfo') or {}).get('goodsList') or []
            # Link alone may be a multi-generation/size container: require exact name.
            if norm(prod.get('name'))==norm(d['name']) and gs:
                g=gs[0];matches.append(dict(channel='mi_cn',product_id=pid,name=prod['name'],price=g.get('price'),image=g.get('imgUrl'),source_url=u,identity='baike_link_and_exact_channel_name'))
    for u in links:
        parsed=urllib.parse.urlsplit(u);gid=(urllib.parse.parse_qs(parsed.query).get('gid') or [''])[0]
        if parsed.hostname in ('www.xiaomiyoupin.com','m.xiaomiyoupin.com','youpin.mi.com') and gid.isdigit():
            matches.append(dict(channel='youpin',product_id=gid,name=d['name'],source_url='https://www.xiaomiyoupin.com/detail?gid='+gid,identity='baike_buy_link_and_exact_channel_name'))
    confirmed=[]
    for m in { (m['channel'],m['product_id']):m for m in matches }.values():
        if m['channel']=='youpin':
            de=fetch('https://www.xiaomiyoupin.com/api/gateway/detail',{'groupName':'details','groupParams':[[m['product_id']]],'pid':'','methods':[],'version':'1.0.0','debug':False,'channel':'','vipMode':False,'system':'3'}, {'Content-Type':'application/json','X-Yp-App-Source':'front-PC','X-User-Agent':'channel/youpin platform/youpin.pc','User-Agent':'Mozilla/5.0'})
            g=(de.get('response',{}).get('data') or {}).get('goods') or {};info=g.get('goodsInfo') or {}
            if norm(info.get('name'))!=norm(d['name']):continue
            m.update(price_fen=info.get('priceMin'),image=info.get('picUrl') or info.get('img800s') or info.get('imgSquare') or m.get('image'),channel_category=g.get('category'),channel_verified=True,detail_evidence=de['url'])
        else:
            de=fetch('https://api2.order.mi.com/product/view?'+urllib.parse.urlencode(dict(product_id=m['product_id'],version=2)));data=de.get('response',{}).get('data') or {};prod=data.get('product') or {};gs=(data.get('goodsInfo') or {}).get('goodsList') or []
            if not prod or not gs:continue
            exact=[g for g in gs if norm(g.get('name'))==norm(d['name'])]
            if norm(prod.get('name'))!=norm(d['name']) and not exact:continue
            g=(exact or gs)[0];m.update(price=g.get('price'),image=g.get('imgUrl'),name=g.get('name') if exact else prod['name'],channel_verified=True,detail_evidence=de['url'])
        confirmed.append(m)
    matches=confirmed
    mi['candidates']=[{k:c.get(k) for k in ('product_id','commodity_id','name','price','image')} for c in mi['candidates']]
    yp['candidates']=[{k:c.get(k) for k in ('gid','name','priceMin','img800s')} for c in yp['candidates']]
    return dict(model=d['model'],name=d['name'],category=d['category'],brand=d['brand'],pd_id=d['pd_id'],mi=mi,youpin=yp,baike=dict(url=e['url'],error=e.get('error'),valid=b.get('model')==d['model'] and b.get('pdId')==d['pd_id'],buy_urls=links),matches=matches,status='channel_hit' if matches else 'unresolved_channel_error' if mi['error'] or yp['error'] else 'archive_only_no_exact_channel_match')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=ROOT/'sample-50-input.json');ap.add_argument('--output',type=Path,default=ROOT/'sample-50.json');a=ap.parse_args();ds=json.loads(a.input.read_text());out=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(probe,ds):
            out.append(r);save(a.output,out);print(len(out),r['name'],r['status'],len(r['matches']),flush=True)
if __name__=='__main__':main()
