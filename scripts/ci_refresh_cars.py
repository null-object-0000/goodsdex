"""Daily refresh of the reviewed 24 BYD + 10 Xiaomi EV configurations only."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.cars import merge_cars, is_car
from goodsdex.supplements import metadata
from car_catalog import Capture, BYD, byd_candidates, verify_byd_parameters, xiaomi_candidates

CATALOG = ROOT / 'data/official/car-catalog.json'


def refresh(capture, catalog):
    approved = catalog['rows']
    rows = []
    for goods_id in sorted({r['id'].split(':goods-')[1].split(':')[0] for r in approved if r['brand'] == '比亚迪'}):
        info = capture.json(BYD + 'getGoodsInfoById?goodsId=' + goods_id)
        configs = capture.json(BYD + 'getGoodsAttrListForCompareByGoodsId?goodsId=' + goods_id)
        candidates = {r['id']: r for r in byd_candidates(info, configs, goods_id)}
        group = [deepcopy(candidates[r['id']]) for r in approved if ':goods-' + goods_id + ':' in r['id']]
        url = 'https://site-api.byd.com/domestic-official-api/goods/goodsParams?goodsId=' + goods_id
        headers = {'Content-Type': 'application/json', 'Origin': 'https://www.byd.com',
                   'Referer': 'https://www.byd.com/cn/parameter-comparison?goodsId=' + goods_id,
                   'User-Agent': 'Mozilla/5.0', 'from-api': url}
        stamp = str(int(time.time()))
        signature = json.loads(capture.get('https://site-api.byd.com/domestic-official-api/getSignature',
                                          json.dumps({'timeStamp': stamp}).encode(), headers))
        if signature.get('code') != 200 or not isinstance(signature.get('data'), str):
            raise ValueError('BYD visitor signature failed')
        headers.update({'X-HMAC-SIGNATURE': signature['data'], 'X-HMAC-TIMESTAMP': stamp,
                        'X-HMAC-SIGNKEY': '4a3688a5gcd88g443fga6b7fcb'})
        rows.extend(verify_byd_parameters(group, json.loads(capture.get(url, headers=headers))))

    payload = json.loads(capture.get('https://website-api.xiaomiev.com/mtop/guidemarketing/product/pc/paramComparison',
                                   b'[{}]', {'Content-Type': 'application/json',
                                             'x-user-agent': 'channel/car platform/car.pc'}))
    candidates = {r['id']: r for r in xiaomi_candidates(payload)}
    rows.extend(deepcopy(candidates[r['id']]) for r in approved if r['brand'] == '小米汽车')
    # Only visually reviewed, exact content hashes from the corresponding product page.
    # A new CDN object requires human review; never guess based on filename/dimensions.
    images, gaps = {}, []
    for series, image in catalog['images'].items():
        try:
            page = capture.get(image['page']).decode()
            if image['url'] not in page:
                raise ValueError('Reviewed vehicle image no longer appears on product page')
            body = capture.get(image['url'])
            if hashlib.sha256(body).hexdigest() != image['sha256']:
                raise ValueError('Reviewed vehicle image content changed')
            images[series] = image['url']
        except Exception as exc:
            images[series] = None
            gaps.append({'series': series, 'reason': str(exc)})
    now = datetime.now(timezone.utc).isoformat()
    seeds = {r['id']: r for r in approved}
    result = []
    for fresh in rows:
        seed = seeds[fresh['id']]
        if (fresh['name'], fresh['brand'], fresh['series'], fresh['trim']) != (seed['name'], seed['brand'], seed['series'], seed['trim']):
            raise ValueError('Reviewed car identity changed')
        row = {**seed, **fresh, 'review_status': 'approved', 'fetched_at': now}
        if row['brand'] == '小米汽车':
            row['image'] = images[row['series']]
            if row['image']:
                row.pop('image_missing_reason', None)
            else:
                row['image_missing_reason'] = 'Reviewed official whole-vehicle image unavailable; see car-refresh-audit.json'
        result.append(row)
    return result, gaps


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public', type=Path, required=True)
    ap.add_argument('--captures', type=Path, required=True, help='Fresh directory per daily run')
    args = ap.parse_args()
    catalog = json.loads(CATALOG.read_text())
    previous = json.loads((args.public / 'goods.json').read_text())
    capture = Capture(args.captures)
    cars, gaps = refresh(capture, catalog)
    result = merge_cars(previous, cars, catalog['rows'])
    old_meta = json.loads((args.public / 'meta.json').read_text())
    audit = {'approved_count': len(cars), 'previous_count': len(previous), 'count': len(result),
             'non_car_objects_unchanged': True, 'non_car_count': sum(not is_car(r) for r in previous),
             'network_requests': capture.requests, 'image_gaps': gaps, 'excluded': catalog['excluded']}
    # All checks above complete before writing either public artifact.
    for name, value in [('goods.json', result), ('meta.json', metadata(result, old_meta)), ('car-refresh-audit.json', audit)]:
        target = args.public / name
        tmp = target.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n')
        tmp.replace(target)
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == '__main__':
    main()
