"""Enumerate official CN storefront navigation and product links to closure."""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from dji_html import embedded
from dji_http import Client, dump
from dji_inventory import inventory

BASE='https://store.dji.com'

def links(source):
    source=html.unescape(source).replace('\\/','/')
    return sorted(set(BASE+'/cn/'+kind+'/'+slug for kind,slug in
        re.findall(r'(?:https://store\.dji\.com)?/cn/(product|list|shop|selection|category)/([a-z0-9-]+)',source)))


def enumerate_catalog(client):
    path=client.root/'enumeration.json'
    state=json.loads(path.read_text()) if path.exists() else {'pending':[BASE+'/cn',BASE+'/robots.txt',BASE+'/sitemap.xml'], 'pages':{},'products':{},'excluded':{}}
    inv=inventory(client)
    active={BASE+'/cn/product/'+v['slug']:BASE+'/cn/list' for v in inv['items'].values() if (v.get('status')or{}).get('code')=='on_sale' and not re.search(r'care|refresh|warranty|service',v['slug']) and not re.search(r'Care|随心换|保障|延保|保险|课程|授权码',v.get('title',''),re.I)}
    state.setdefault('detail_products',{})
    state['detail_products'].update(active)
    state['inventory_complete']=inv['complete']
    state['pending']=[u for u in state['detail_products'] if u not in state['pages'] and u not in state.get('unavailable',{})]
    # Sitemap is a candidate universe, not a claim of current availability.
    state.setdefault('unavailable',{})
    for seed in [BASE+'/robots.txt',BASE+'/sitemap.xml','https://assets.djicdn.com/sitemap/store/store-cn.xml']:
        if seed not in state['pages'] and seed not in state['pending']:state['pending'].insert(0,seed)
    while state['pending']:
        url=state['pending'][0]
        source,r=client.fetch(url)
        found=links(source) if r['status']==200 else []
        _,data,_=embedded(source)
        # Product JSON gives all sibling variant slugs even if no anchor was rendered.
        if '/product/' in url:
            for v in data.get('products',{}).get('variants',[]):
                slug=v.get('slug')
                if slug and (v.get('status') or {}).get('code') in {'not_sale','out_of_stock'}:
                    state['unavailable'][BASE+'/cn/product/'+slug]=(v.get('status') or {}).get('code')
                if slug and re.fullmatch('[a-z0-9-]+',slug) and (v.get('status') or {}).get('code')=='on_sale': found.append(BASE+'/cn/product/'+slug)
        if 'sitemap' in url:
            found += [html.unescape(x) for x in re.findall(r'<loc>(.*?)</loc>',source) if x.startswith(BASE+'/cn/product/') or (x.startswith(BASE+'/') and re.search(r'\.xml(?:\.gz)?$',x))]
        state['pages'][url]={'status':r['status'],'links':len(set(found)),'fetched_at':r.get('fetched_at')}
        for link in sorted(set(found)):
            # Services are outside the physical goods scope, but retain counts.
            if re.search(r'care|refresh|warranty|service',urlsplit(link).path):
                state['excluded'][link]='service'
                continue
            if '/product/' in link:
                state['products'].setdefault(link,url)
                if 'sitemap' not in url:state['detail_products'].setdefault(link,url)
            if link in state['unavailable']:
                continue
            if 'sitemap' in url:continue
            if link not in state['pages'] and link not in state['pending']:
                state['pending'].append(link)
        state['pending'].pop(0)
        state['pending']=[x for x in state['pending'] if x not in state['unavailable']]
        dump(path,state)
        client.log(f'enumeration pages={len(state["pages"])} products={len(state["products"])} pending={len(state["pending"])}')
    return state

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('data/dji'));ap.add_argument('--offline',action='store_true')
    a=ap.parse_args();enumerate_catalog(Client(a.root,a.offline))
