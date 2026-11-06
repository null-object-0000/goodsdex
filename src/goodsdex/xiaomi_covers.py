"""Exact-id mtop covers. No series substitution and no image mirroring."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import json
import re

DEFAULT_EVIDENCE = Path(__file__).resolve().parents[2] / 'data/official/xiaomi-cover-images.json'
SOURCE = 'mi_cn_mtop_cover'
LOCATOR = '$.data.goodsInfo.goodsList[0].imgUrl'

def is_xiaomi_product(key):
    return bool(re.fullmatch(r'CN:mi_cn:product:\d+', str(key)))

@lru_cache(maxsize=1)
def evidence():
    return json.loads(DEFAULT_EVIDENCE.read_text()) if DEFAULT_EVIDENCE.exists() else {}

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
        out.update(image_source=SOURCE,
                   image_source_url='https://m.mi.com/mtop/xiaomishop/product/info',
                   image_captured_at=observation.get('captured_at'), image_scope='model',
                   image_note=LOCATOR + '; exact productId=' + row['id'].split(':')[-1])
        out.pop('image_missing', None)
        out.pop('image_fallback', None)
    return out

def apply_covers(rows, observations=None):
    observations = evidence() if observations is None else observations
    result = []
    for row in rows:
        observation = observations.get(row.get('id')) if is_xiaomi_product(row.get('id')) else None
        if observation is not None:
            # A newer collector observation wins over the frozen backfill.
            at = row.get('image_checked_at') or (row.get('image_captured_at') if row.get('image_source') == SOURCE else '') or ''
            try:
                newer = datetime.fromisoformat(at) > datetime.fromisoformat(observation.get('captured_at', ''))
            except (ValueError, TypeError):
                newer = False
            if newer:
                result.append(deepcopy(row)); continue
            row = patch_cover(row, observation)
        result.append(deepcopy(row))
    return result

def record_cover(rec, row):
    if not is_xiaomi_product(row.get('id')): return row
    pid = row['id'].split(':')[-1]
    assertions = [a for a in rec.get('assertions', []) if a.get('source') == SOURCE
                  and a.get('attribute') == 'official_main_image' and str(a.get('subject_id')) == pid]
    if assertions:
        a = assertions[-1]
        cap = next((c for c in rec.get('captures', []) if c.get('capture_id') == a.get('capture_id')), {})
        return patch_cover(row, dict(image=a.get('raw_value'), captured_at=cap.get('fetched_at') or rec.get('fetched_at')))
    observation = evidence().get(row['id'])
    return patch_cover(row, observation or dict(image=None, captured_at=rec.get('fetched_at')))
