"""Bounded incremental official product-image collection. Never use device icons as main images."""
from datetime import datetime,timezone
import hashlib,io,json
from pathlib import Path
import requests
from PIL import Image
from goodsdex.mihome_intake import norm
from goodsdex.product_sources import materialize


def refresh(rows,fetch=requests.get,limit=100):
    result=list(rows);audit=[];attempts=0
    for i,row in enumerate(rows):
        if row.get('image') or not row['id'].startswith('CN:mi_cn:product:'):continue
        if attempts>=limit:break
        attempts+=1;pid=row['id'].rsplit(':',1)[-1]
        try:
            url='https://api2.order.mi.com/product/view'
            response=fetch(url,params=dict(product_id=pid,version=2),timeout=30);response.raise_for_status();data=response.json().get('data') or {}
            product=data.get('product') or {};goods=(data.get('goodsInfo') or {}).get('goodsList') or []
            if norm(product.get('name'))!=norm(row.get('name')):raise ValueError('产品名不完全一致，保留审核')
            images={g.get('imgUrl') for g in goods if g.get('imgUrl')}
            if len(images)!=1:raise ValueError('多商品图身份不明确，保留审核')
            image=images.pop()
            if not image.startswith('https://'):raise ValueError('图片地址必须为 HTTPS')
            response=fetch(image,timeout=30);response.raise_for_status();raw=response.content;im=Image.open(io.BytesIO(raw));im.verify()
            if min(im.size)<300:raise ValueError('图片尺寸不足')
            at=datetime.now(timezone.utc).isoformat();proof=url+'?product_id='+pid+'&version=2'
            observation=dict(source='mi_store',role='secondary',kind='channel_listing',source_url=proof,captured_at=at,fields=dict(image=image,image_kind='product_main',width=im.width,height=im.height),evidence=dict(method='api_product_identity_and_image_get',http_status=200,verified=True,sha256=hashlib.sha256(raw).hexdigest()))
            result[i]=materialize(row,observations=[observation],at=at)
            audit.append(dict(id=row['id'],status='added',url=image,sha256=hashlib.sha256(raw).hexdigest()))
        except Exception as exc:audit.append(dict(id=row['id'],status='pending',reason=str(exc)))
    return result,audit

if __name__=='__main__':
    path=Path('_data/public/goods.json');rows=json.loads(path.read_text());after,audit=refresh(rows)
    path.write_text(json.dumps(after,ensure_ascii=False,indent=1)+'\n')
    target=Path('_data/data/categories/image-refresh-report.json');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(audit,ensure_ascii=False,indent=1)+'\n')
    if audit and all(a['status']=='pending' for a in audit):raise SystemExit('No official image verified; see image-refresh-report.json')
