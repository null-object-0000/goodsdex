"""Bounded incremental official product-image collection. Never use device icons as main images."""
from datetime import datetime,timezone
import hashlib,io,json
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
import requests
from PIL import Image
from goodsdex.mihome_intake import norm
from copy import deepcopy
from goodsdex.product_sources import envelopes, derive
from goodsdex.sources.mi_cn import MTOP_HEADERS, MTOP_URL
from goodsdex.xiaomi_covers import BAIKE_SOURCE, SOURCE, patch_cover
from backfill_xiaomi_baike_covers import collect as collect_realicon


def failure_status(exc):
    # A missing resource is expected; access failures do not prove absence.
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return 'no_official_image' if exc.response.status_code == 404 else 'network_error'
    if isinstance(exc, HTTPError):
        return 'no_official_image' if exc.code == 404 else 'network_error'
    if isinstance(exc, (requests.RequestException, URLError, TimeoutError, subprocess.TimeoutExpired)):
        return 'network_error'
    if isinstance(exc, (ValueError, OSError)):
        return 'no_official_image'
    raise exc  # Programming errors must not be reported as upstream absence.


def mtop_cover(row, fetch, post):
    pid = row['id'].rsplit(':', 1)[-1]
    response = post(MTOP_URL, headers=MTOP_HEADERS,
                    json=[{}, {'productId': int(pid)}], timeout=30)
    response.raise_for_status()
    payload = response.json()
    if payload.get('code', 0) != 0:
        # Known product absence is not a transport failure; unknown API errors are.
        if payload.get('code') in (400480502, 400480400):
            raise ValueError('商品已下架或不存在')
        raise requests.RequestException('mtop API error: ' + str(payload))
    data = payload.get('data') or {}
    product = data.get('product') or {}
    if norm(product.get('name')) != norm(row.get('name')):
        raise ValueError('产品名不完全一致，保留审核')
    if str(product.get('productId', pid)) != pid:
        raise ValueError('productId 不一致')
    goods = (data.get('goodsInfo') or {}).get('goodsList') or []
    main = goods[0] if goods else {}
    # Only official main-image fields, never icon, carousel, ads or detail posters.
    candidates = [main.get('picUrl'), main.get('imgUrl')]
    for pic in product.get('pics') or []:
        candidates.append(pic if isinstance(pic, str) else
                          pic.get('picUrl') or pic.get('imgUrl') or pic.get('url'))
    errors = []
    fallback = None
    for image in dict.fromkeys(candidates):
        if not isinstance(image, str) or not image.startswith('https://'):
            continue
        try:
            response = fetch(image, timeout=30)
            response.raise_for_status()
            raw = response.content
            with Image.open(io.BytesIO(raw)) as im:
                im.load()
                width, height = im.size
                # White-background main shots win over promotional main shots.
                thumb = im.convert('RGBA')
                thumb.thumbnail((32, 32))
                white = Image.new('RGBA', thumb.size, 'white')
                white.alpha_composite(thumb)
                corners = [(0, 0), (white.width - 1, 0),
                           (0, white.height - 1), (white.width - 1, white.height - 1)]
                white_background = all(min(white.getpixel(point)[:3]) >= 240 for point in corners)
            if min(width, height) < 400:
                raise ValueError('图片尺寸不足 400×400')
            cover = dict(image=image, width=width, height=height, source=SOURCE,
                        source_url=MTOP_URL + '?productId=' + pid,
                        captured_at=datetime.now(timezone.utc).isoformat(),
                        image_sha256=hashlib.sha256(raw).hexdigest())
            if white_background:
                return cover
            fallback = fallback or cover
        except Exception as exc:
            errors.append((failure_status(exc), str(exc)))
    if fallback:
        return fallback
    if any(status == 'network_error' for status, _ in errors):
        raise requests.RequestException(str(errors))
    raise ValueError('无可验证的官方主图: ' + str(errors))


def official_cover(row, fetch, post, baike):
    errors = []
    if row.get('miio_model'):
        try:
            observation = baike(row['miio_model'])
        except Exception as exc:
            status = failure_status(exc)
            observation = dict(failure=status)
            if status == 'network_error':
                errors.append(str(exc))
        if (not observation.get('failure') and observation.get('image')
                and min(observation.get('width', 0), observation.get('height', 0)) >= 400):
            return dict(observation, source=BAIKE_SOURCE)
        if observation.get('failure') == 'http_error':
            checks = [observation.get(k) or {} for k in ('product_request', 'image_request')]
            if any(c and c.get('http_status') not in (200, 404) for c in checks):
                errors.append(str(observation))
    try:
        return mtop_cover(row, fetch, post)
    except Exception as exc:
        status = failure_status(exc)
        if errors or status == 'network_error':
            raise requests.RequestException('; '.join(errors + [str(exc)])) from exc
        raise


def refresh(rows, fetch=None, limit=100, *, post=None, baike=None):
    fetch = fetch or requests.get
    post = post or requests.post
    baike = baike or collect_realicon
    result = list(rows)
    audit = []
    for i, row in enumerate(rows):
        if row.get('image') or not row['id'].startswith('CN:mi_cn:product:'):
            continue
        if len(audit) >= min(limit, 100):
            break
        try:
            cover = official_cover(row, fetch, post, baike)
            publisher = 'mihome_directory' if cover['source'] == BAIKE_SOURCE else 'mi_store'
            observation = dict(source=publisher, role='secondary', kind='channel_listing',
                source_url=cover['source_url'], captured_at=cover['captured_at'],
                fields=dict(image=cover['image'], image_kind='product_main',
                            width=cover['width'], height=cover['height']),
                evidence=dict(method='exact_model_realIcon_get' if publisher == 'mihome_directory'
                              else 'mtop_product_identity_and_image_get', http_status=200,
                              verified=True, sha256=cover['image_sha256']))
            # Resolve only the image. Re-materializing the row also recalculates prices/release.
            out = patch_cover(row, cover)
            if cover['source'] == SOURCE:
                out['image_note'] = ('mtop product.pics / goodsInfo.goodsList[0] main image; '
                                     'exact productId=' + row['id'].rsplit(':', 1)[-1])
            out['sources'] = envelopes([*deepcopy(row.get('sources', [])), observation])
            roles = {s['source']: s.get('role', 'secondary') for s in row.get('sources', [])}
            for source in out['sources']:
                source['role'] = roles.get(source['source'], 'secondary')
            out['display'] = deepcopy(row.get('display', {}))
            out['display']['image'] = derive(envelopes([observation]))['image']
            result[i] = out
            audit.append(dict(id=row['id'], status='added', source=cover['source'],
                              url=cover['image'], width=cover['width'], height=cover['height'],
                              sha256=cover['image_sha256']))
        except Exception as exc:
            audit.append(dict(id=row['id'], status=failure_status(exc), reason=str(exc)))
    return result, audit

def main():
    path=Path('_data/public/goods.json');rows=json.loads(path.read_text());after,audit=refresh(rows)
    path.write_text(json.dumps(after,ensure_ascii=False,indent=1)+'\n')
    target=Path('_data/data/categories/image-refresh-report.json');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(audit,ensure_ascii=False,indent=1)+'\n')
    counts={status:sum(a['status']==status for a in audit)
            for status in ('added','no_official_image','network_error')}
    print(f"本轮 {len(audit)} 个候选：补上 {counts['added']}、上游无图 {counts['no_official_image']}、网络失败 {counts['network_error']}")
    return int(bool(audit) and counts['network_error']>0 and counts['added']==0)


if __name__=='__main__':
    raise SystemExit(main())
