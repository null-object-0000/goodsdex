"""Mirror only new catalogue covers; publish tiny routes to MySQL, never catalogue JSON to OSS."""
import concurrent.futures
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import os
import sys
import time
import threading
import re
from urllib.parse import urlparse, urlsplit, urlunsplit, parse_qsl, urlencode
import requests
from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 16_000_000
MAX_BYTES = 8 * 1024 * 1024
_downloads = threading.local()


def image_get(*args, **kwargs):
    # Keep source connections separate from authenticated metadata publication.
    if not hasattr(_downloads, 'session'):
        _downloads.session = requests.Session()
    return _downloads.session.get(*args, **kwargs)
HOSTS = {'cdn.cnbj0.fds.api.mi-img.com', 'cdn.cnbj1.fds.api.mi-img.com',
         'static.home.mi.com', 'store.storeimages.cdn-apple.com', 'cdsassets.apple.com',
         'fujifilm-x.b-cdn.net', 'hp.widen.net', 'media.hpstore.cn',
         'ssl-product-images.www8-hp.com', 'www.hp.com', 'se-cdn.djiits.com', 'xbu-qiniu.yaduo.com',
         's1.xiaomiev.com', 'www.bydauto.com.cn', 'www.byd.com'}


def keys(src):
    u = urlsplit(src)
    host=u.hostname or ''
    drop = ['thumb','w','h'] if host.endswith('.mi-img.com') else ['wid','hei'] if host.endswith(('.apple.com','.cdn-apple.com')) else []
    plain = urlunsplit((u.scheme,u.netloc,u.path,urlencode([(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True) if k not in drop]),u.fragment))
    return [hashlib.sha1(v.encode()).hexdigest()[:32] for v in dict.fromkeys([src,plain])]


def pending(urls, routes, now=None, retry_failed=False, repair_legacy=False):
    now = now or datetime.now(timezone.utc)
    result=[]
    for src in sorted(set(urls)):
        if not isinstance(src,str) or urlparse(src).scheme!='https': continue
        entries=[routes[k] for k in keys(src) if k in routes]
        # The old SHA1-named JPEG pipeline discarded source transparency. Repair
        # these only on explicit backfill; modern assets never download again.
        # JPEG 不可能带透明通道：任何 .jpg 物件都是「拍平过的」封面，值得重取一次。
        legacy=lambda key:bool(re.fullmatch(r'goods/[a-f0-9]{40,64}\.jpg',key))
        if any(e.get('objectKey') and not e['objectKey'].endswith('.webp') and not (repair_legacy and legacy(e['objectKey'])) for e in entries): continue
        # Failed source URLs retry at most once a day across all collectors.
        if not retry_failed and any(not e.get('objectKey') and e.get('checkedAt') and (now-datetime.fromisoformat(e['checkedAt'].replace('Z','+00:00'))).total_seconds()<86400 for e in entries): continue
        result.append(src)
    return result


def download(src, get=image_get):
    for _ in range(4):
        u=urlparse(src)
        if u.scheme!='https' or u.username or u.password or u.port not in (None,443) or u.hostname not in HOSTS:
            raise ValueError('Unapproved image source')
        response=get(src,stream=True,timeout=(5,12),allow_redirects=False)
        try:
            if response.status_code in (301,302,303,307,308):
                from urllib.parse import urljoin
                src=urljoin(src,response.headers['Location']);continue
            response.raise_for_status()
            # Xiaomi's iotweb CDN serves valid PNGs as text/plain. The bounded
            # decoder below validates actual pixels instead of trusting MIME.
            chunks=[];size=0
            for chunk in response.iter_content(65536):
                size+=len(chunk)
                if size>MAX_BYTES:raise ValueError('Oversized image')
                chunks.append(chunk)
            return b''.join(chunks)
        finally: response.close()
    raise ValueError('Too many image redirects')


def convert(raw):
    with Image.open(io.BytesIO(raw)) as image:
        if image.width*image.height>16_000_000:raise ValueError('Oversized image dimensions')
        image=ImageOps.exif_transpose(image).convert('RGBA')
        image.thumbnail((480,480),Image.Resampling.LANCZOS)
        out=io.BytesIO()
        if image.getextrema()[3][0]<255:image.save(out,format='PNG',optimize=True)
        else:image.convert('RGB').save(out,format='JPEG',quality=82,optimize=True,progressive=True)
        return out.getvalue()


def mirror(src,bucket,existing=None):
    try:
        # Re-encode our initial WebP assets once; do not crawl their origins again.
        previous=(existing or {}).get(keys(src)[0],{}).get('objectKey')
        if previous and previous.endswith('.webp'):
            response=image_get('https://spend-good.oss-cn-shanghai.aliyuncs.com/'+previous,timeout=15)
            try:response.raise_for_status();raw=response.content
            finally:response.close()
            if len(raw)>MAX_BYTES:raise ValueError('Oversized stored image')
        else:raw=download(src)
        data=convert(raw)
    except Exception:
        # A source 404/timeout never switches the client back to an unapproved CDN.
        return dict(sourceUrl=src,objectKey=None),0
    transparent=data.startswith(b'\x89PNG')
    key='goods/'+hashlib.sha256(data).hexdigest()+('.png' if transparent else '.jpg')
    # Infrastructure failures abort publication rather than marking valid images missing.
    bucket.put_object(key,data,headers={'Content-Type':'image/png' if transparent else 'image/jpeg','Cache-Control':'public, max-age=31536000, immutable'})
    return dict(sourceUrl=src,objectKey=key),len(data)


def publish_routes(base,token,assets,post=requests.post,sleep=time.sleep):
    wire=gzip.compress(json.dumps({'assets':assets},ensure_ascii=False).encode(),mtime=0)
    for attempt in range(6):
        response=None
        try:
            response=post(base.rstrip('/')+'/admin/api/catalog/images',data=wire,
                headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','Content-Encoding':'gzip'},
                timeout=60,allow_redirects=False)
            response.raise_for_status()
            if response.status_code!=200 or not response.json().get('ok'):raise ValueError('Image route publication rejected')
            return
        except requests.RequestException:
            if attempt==5 or (response is not None and response.status_code not in (408,429) and response.status_code<500):raise
        finally:
            if response is not None:response.close()
        sleep(2**(attempt+1))


def main():
    data=json.load(sys.stdin);base=os.environ['CATALOG_API_URL'];token=os.environ['CATALOG_IMPORT_TOKEN']
    assert urlparse(base).scheme=='https' and len(token)>=32
    urls=pending(data['urls'],data['routes'],retry_failed=data.get('retryFailed',False),repair_legacy=data.get('repairLegacy',False))
    # Nothing new: no source downloads, no OSS operations, no route writes.
    if not urls: print(json.dumps(dict(uploaded=0,failed=0,bytes=0)));return
    import oss2
    bucket=oss2.Bucket(oss2.Auth(os.environ['OSS_ACCESS_KEY_ID'],os.environ['OSS_ACCESS_KEY_SECRET']),
        'https://oss-cn-shanghai.aliyuncs.com','spend-good')
    result=dict(uploaded=0,failed=0,bytes=0);batch=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(mirror,src,bucket,data['routes']) for src in urls]
        try:
            for future in concurrent.futures.as_completed(futures):
                asset,size=future.result()
                batch.append(asset)
                result['uploaded' if asset['objectKey'] else 'failed']+=1;result['bytes']+=size
                if len(batch)==50:publish_routes(base,token,batch);batch=[]
            if batch:publish_routes(base,token,batch)
        except Exception:
            for task in futures:task.cancel()
            raise
    print(json.dumps(result))


if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'error':type(error).__name__,'status':getattr(error,'status',None)}),file=sys.stderr)
        sys.exit(1)
