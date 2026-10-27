"""Enumerate the public category page's own paginated product listing.

The HTML has categories but no product rows. Its public List chunk documents this
GET endpoint and page.current/page.pageSize/page.total. No account, cart or private
product API is used. Price/name/image publication still comes from detail HTML.
"""
import math
import re
from urllib.parse import urlencode
from dji_html import embedded
from dji_http import dump

BASE='https://store.dji.com'


def inventory(client):
    path=client.root/'inventory.json'
    if path.exists():
        import json
        cached=json.loads(path.read_text())
        if cached.get('complete'):return cached
    home,_=client.fetch(BASE+'/cn')
    categories=sorted(set(re.findall(r'/cn/list/([a-z0-9-]+)',home)) - {'service'})
    result={'categories':{},'items':{},'complete':False}
    import json
    for slug in categories:
        source,r=client.fetch(BASE+'/cn/list/'+slug)
        if r['status']!=200:raise RuntimeError('category unavailable: '+slug)
        _,st,_=embedded(source)
        selected=st.get('list',{}).get('selected',{})
        tab=selected.get('tab')
        page=1;total=None;count=0;pages=[]
        while True:
            query=urlencode({'country':'cn','language':'zh-CN','sort':'recommendation','page':page,**({'tab':tab} if tab else {})})
            url=BASE+'/api/ec-cms/pages/list/'+slug+'/products?'+query
            raw,response=client.fetch(url)
            if response['status']!=200:raise RuntimeError('inventory HTTP failure: '+url)
            payload=json.loads(raw)
            if not payload.get('success'):raise RuntimeError('inventory source error: '+url)
            data=payload['data'];pagination=data['page'];items=data['items']
            if pagination['current']!=page:raise RuntimeError('pagination did not advance')
            if total is None:total=pagination['total']
            elif total!=pagination['total']:raise RuntimeError('inventory changed during enumeration; use fresh snapshot')
            for item in items:
                key=str(item['variantId'])
                result['items'][key]=item
            count+=len(items);pages.append({'url':url,'count':len(items),'page':pagination})
            client.log(f'inventory {slug} page={page} items={count}/{total}')
            if page*pagination['pageSize']>=total:break
            if not items:raise RuntimeError('empty inventory page before total')
            page+=1
        if count!=total:raise RuntimeError('inventory row count mismatch')
        result['categories'][slug]={'total':total,'pages':pages}
        dump(path,result)
    result['complete']=True;dump(path,result)
    return result
