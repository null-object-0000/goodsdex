"""Incremental directory intake using stable model IDs and existing publication guards."""
from datetime import datetime,timezone
import hashlib
import io
import json
from urllib.parse import urlencode, urlsplit
import requests
from PIL import Image
from goodsdex.mihome_intake import classify,apply_intake as mihome_apply,norm
from goodsdex.earbuds_intake import apply_intake as earbuds_apply


def intake(rows,devices,source,fetch=requests.get):
    now=datetime.now(timezone.utc).isoformat()
    known={r.get('miio_model') or r.get('mihome_model') or r.get('model') for r in rows}
    names={norm(r.get('name')) for r in rows}
    entries=[];pending=[]
    digest=hashlib.sha256(json.dumps(devices,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    for d in devices:
        model=d.get('model')
        if not model or model in known or norm(d.get('name')) in names:continue
        try:
            if source=='gap':
                if classify(d)[0]!='A':
                    pending.append(dict(model=model,reason='整机白名单以外，保留人工审核'));continue
                url='https://home.mi.com/cgi-op/api/v1/baike/v2/product?'+urlencode(dict(model=model))
                response=fetch(url,timeout=30);response.raise_for_status();proof=response.json().get('data') or {}
                if proof.get('model')!=model or proof.get('pdId')!=d['pdId']:
                    raise ValueError('百科型号与目录 ID 不一致')
                r=dict(id=f"mihome:{d['pdId']}",name=d['name'],name_mihome=d['name'],category=d['categoryName'],category_mihome=d['categoryName'],brand=d.get('brandName') or '未知',miio_model=model,mihome_model=model,mihome_pd_id=d['pdId'],image=None,image_missing=True,image_mihome=dict(url=d.get('icon'),scope='device_icon',source='mihome_directory',note='设备图标，非商品主图'),price=None,price_missing='no_channel_price',price_kind='unknown',price_comparable=False,source='mihome',discovered_by='mihome_directory',source_url=url,source_channels=['mihome'],kind='machine',record_level='device_reference',catalog_identity='mihome_durable_device_v1',captured_at=now,params={},channel_search_status='not_searched',mihome_catalog_evidence=dict(source_url=url,captured_at=now,sha256=digest))
                entries.append(dict(classification='A',directory_sha256=digest,channel_verified=False,row=r))
            else:
                if not model.startswith('miwear.headphone.'):raise ValueError('非耳机型号身份')
                icons=d.get('icon_static') or [];url=next((i['icon_url'] for i in icons if i.get('icon_url')),None)
                if not url or urlsplit(url).hostname!='cdn.cnbj1.fds.api.mi-img.com':raise ValueError('商品图域名或角色未确认')
                response=fetch(url,timeout=30);response.raise_for_status();image=Image.open(io.BytesIO(response.content));image.verify()
                if min(image.size)<200:raise ValueError('目录图尺寸不足')
                source_url='https://cn.tws.wear.xiaomiwear.com/twswear/product/get_product_list'
                fields=dict(name=d['name'],model=model,image=url,image_kind='white_background',width=image.width,height=image.height,category='耳机')
                observation=dict(source='earbuds_directory',role='primary',kind='device_directory',source_url=source_url,captured_at=now,fields=fields,evidence=dict(method='anonymous_api',cookie_kind='app_static',http_status=200,verified=True,sha256=digest))
                entries.append(dict(id=model,model=model,region='CN',name=d['name'],brand='小米',category='耳机',kind='machine',record_level='model_reference',catalog_identity='earbuds_directory_cn_v1',source='earbuds_directory',source_url=source_url,source_channels=['earbuds_directory'],primary_source='earbuds_directory',discovered_by='earbuds_directory',captured_at=now,intake_at=now,image=url,image_missing=False,image_scope='product_image',image_source='earbuds_directory',price=None,price_kind='unknown',price_missing='no_channel_price',price_comparable=False,sale_status='unverified',params={},sources=[observation],channel_links=[]))
            known.add(model);names.add(norm(d['name']))
        except Exception as exc:
            pending.append(dict(model=model,reason=str(exc)))
    result=(mihome_apply if source=='gap' else earbuds_apply)(rows,dict(schema=1,items=entries))
    return result,pending
