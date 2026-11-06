"""Exact-model covers: baike realIcon, verified pdicon, then store/existing image."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import json
import re

DEFAULT_EVIDENCE = Path(__file__).resolve().parents[2] / 'data/official/xiaomi-cover-images.json'
BAIKE_EVIDENCE = DEFAULT_EVIDENCE.with_name('xiaomi-realicon-images.json')
PDID_EVIDENCE = DEFAULT_EVIDENCE.with_name('xiaomi-pdid-map.json')
PDICON_BASE = 'https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/'
BAIKE_SOURCE = 'mijia_baike_realIcon'
BAIKE_URL = 'https://home.mi.com/cgi-op/api/v1/baike/v2/product?model='
SOURCE = 'mi_cn_mtop_cover'
LOCATOR = '$.data.goodsInfo.goodsList[0].imgUrl'

def is_xiaomi_product(key):
    return bool(re.fullmatch(r'CN:mi_cn:product:\d+', str(key)))

@lru_cache(maxsize=1)
def evidence():
    return json.loads(DEFAULT_EVIDENCE.read_text()) if DEFAULT_EVIDENCE.exists() else {}

@lru_cache(maxsize=1)
def baike_evidence():
    return json.loads(BAIKE_EVIDENCE.read_text()) if BAIKE_EVIDENCE.exists() else {}

@lru_cache(maxsize=1)
def pdid_evidence():
    return json.loads(PDID_EVIDENCE.read_text()) if PDID_EVIDENCE.exists() else {}

def apply_pdicons(rows, mappings=None):
    """Replay exact-model pdIds; failed URL checks retain the incoming image."""
    mappings = pdid_evidence() if mappings is None else mappings
    result = deepcopy(rows)
    for row in result:
        entry = mappings.get(row.get('miio_model'))
        if (not entry or not entry.get('usable')
                or str(row.get('image_source', '')).startswith('mijia_baike')):
            continue
        pd_id = entry.get('pd_id')
        if type(pd_id) is not int or pd_id <= 0:
            continue
        row.update(image=PDICON_BASE + str(pd_id) + '.png', image_source='mijia_pdicon')
        # Do not carry dimensions/provenance belonging to a replaced poster.
        for key in list(row):
            if key.startswith('image_') and key not in ('image_source', 'image_mihome'):
                row.pop(key)
        row.update(image_scope='model', image_source_url=PDICON_BASE + str(pd_id) + '.png')
        for key in ('width', 'height'):
            if entry.get(key):
                row['image_' + key] = entry[key]
    return result

def realicon_cover(row, observations):
    model = row.get('miio_model')
    observation = observations.get(model) if model else None
    if not observation or observation.get('model') != model:
        return None
    url = observation.get('image')
    if not isinstance(url, str) or not url.startswith('https://'):
        return None
    return patch_cover(row, dict(observation, source=BAIKE_SOURCE,
                                source_url=BAIKE_URL + model))

def patch_cover(row, observation):
    out = deepcopy(row)
    url = observation.get('image')
    valid = isinstance(url, str) and url.startswith('https://')
    if valid:
        out['image'] = url
        # Dimensions refer to the selected image, never to the previous poster.
        out.pop('image_width', None)
        out.pop('image_height', None)
        for key in ('width', 'height'):
            if observation.get(key): out['image_' + key] = observation[key]
    out['image_status'] = 'available' if valid else 'official_unavailable'
    out['image_checked_at'] = observation.get('captured_at')
    if not valid:
        if out.get('image'):
            out['image_fallback'] = 'mtop_official_unavailable'
        out['image_note'] = 'mtop 主图未验证；保留原图，不借用其他型号图片；checked_at=' + str(observation.get('captured_at'))
    else:
        source = observation.get('source', SOURCE)
        out.update(image_source=source,
                   image_source_url=observation.get('source_url', 'https://m.mi.com/mtop/xiaomishop/product/info'),
                   image_captured_at=observation.get('captured_at'), image_scope='model',
                   image_note=('$.data.realIcon; exact miio_model=' + row['miio_model']
                               if source == BAIKE_SOURCE else LOCATOR + '; exact productId=' + row['id'].split(':')[-1]))
        out.pop('image_missing', None)
        out.pop('image_fallback', None)
    return out

def apply_covers(rows, observations=None, realicons=None, pdicons=None):
    observations = evidence() if observations is None else observations
    realicons = baike_evidence() if realicons is None else realicons
    result = []
    for row in rows:
        if str(row.get('image_source', '')).startswith('mijia_baike') and row.get('image'):
            result.append(deepcopy(row))
            continue
        preferred = realicon_cover(row, realicons) if is_xiaomi_product(row.get('id')) else None
        if preferred is not None:
            result.append(preferred)
            continue
        observation = observations.get(row.get('id')) if is_xiaomi_product(row.get('id')) else None
        if observation is not None:
            # A newer collector observation wins over the frozen backfill.
            at = (row.get('image_checked_at') or (row.get('image_captured_at') if row.get('image_source') == SOURCE else '') or '') if row.get('image_source') != BAIKE_SOURCE else ''
            try:
                newer = datetime.fromisoformat(at) > datetime.fromisoformat(observation.get('captured_at', ''))
            except (ValueError, TypeError):
                newer = False
            if newer:
                result.append(deepcopy(row)); continue
            row = patch_cover(row, observation)
        result.append(deepcopy(row))
    return apply_pdicons(result, pdicons)

def record_cover(rec, row):
    if not is_xiaomi_product(row.get('id')): return row
    preferred = realicon_cover(row, baike_evidence())
    if preferred is not None: return preferred
    pid = row['id'].split(':')[-1]
    assertions = [a for a in rec.get('assertions', []) if a.get('source') == SOURCE
                  and a.get('attribute') == 'official_main_image' and str(a.get('subject_id')) == pid]
    if assertions:
        a = assertions[-1]
        cap = next((c for c in rec.get('captures', []) if c.get('capture_id') == a.get('capture_id')), {})
        return patch_cover(row, dict(image=a.get('raw_value'), captured_at=cap.get('fetched_at') or rec.get('fetched_at')))
    observation = evidence().get(row['id'])
    return patch_cover(row, observation or dict(image=None, captured_at=rec.get('fetched_at')))
