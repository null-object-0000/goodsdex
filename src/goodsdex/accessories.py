"""Brand-independent release-only accessory policy; source records are never mutated."""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from goodsdex.cars import is_car

# Product nouns in compatibility prefixes do not establish a complete device.
ACCESSORY_WORDS = (
    '配件', '滤芯', '滤网', '替换装', '替换芯', '耗材', '充电器', '数据线', '充电线',
    '保护壳', '手机壳', '贴膜', '支架', '底座', '转接头', '转接线', '转接器',
    '收纳包', '收纳保护包', '清洁液', '镜头盖', '遮光罩', '相机包', '电脑包',
    '扩展坞', '电源适配器', '桨叶', '螺旋桨', '电池', '充电管家', '充电盒',
    '表带', '腕带', '表圈', '键盘', '保护膜', '保护盖', '保护框', '保护罩',
    '保护套', '连接线', '供电线', '电源线', '快充线', '转接件', '拓展板',
    '扩展板', '拓展配件', '防水壳', '拖布', '滚刷', '尘袋', '喷嘴',
    '背带', '肩带', '半链', '桌搭', '增幅仪', '影像套装', '充电桩', '充放电枪', '刀头', '墨粉', '织布面板', 'Battery', '发射端', '接收器', '防风毛套',
)
# Explicitly listed devices, including ones miscategorised as accessories. A model
# number alone is NEVER sufficient. These patterns require a product noun/family.
DEVICE = re.compile(
    r'(?:净水器|净饮机|空调|电视|扫(?:地|拖)机器人|机器人|显示器|充电宝|对讲机|'
    r'笔记本|平板|手机|无人机|运动相机|手环|手表|云台相机|相机机身|套机|'
    r'蓝牙音箱|电动剃须刀|手动剃须刀|口袋吉他|断电保护电源|行车记录仪|'
    r'\bXiaomi\s+Sound\b|'
    r'\biPhone\b|\biPad\b|\bMac(?:Book)?\b|\bAirPods\b|\bWatch\b|'
    r'\b(?:Xiaomi|REDMI)\s+(?:Pad|Book|Note|MIX|\d)|'
    r'麦克风|户外电源)', re.I)
MODEL_DEVICE = re.compile(r'(?:DJI\s+(?:Mini|Mavic|Air|Avata|Neo|Flip|Inspire|Matrice|Mic|RS|Power)|Osmo\s+(?:Action|Pocket|Nano|360))[\s\dA-Za-z.-]*(?:(?:畅飞|智选|全能|标准|套机|徒步|自媒体|直流供电)[^（(]*套装)?$', re.I)
PARTS = re.compile(r'配件|模块|减震|拓展|扩展|连接|转接|保护(?:组件|贴纸|锁扣|胶套)|收纳|遮光|镜头盖|电池|滤芯|滤网|充电器|充电线|数据线|表带|腕带|表圈|键盘|背带|肩带|半链|桌搭|增幅仪|影像套装|充电桩|充放电枪|喷嘴|拖布|滚刷|尘袋|刀头|墨粉|织布面板|音频连接器|触控笔|手机夹|主刷|边刷|手链|自动上下水|面板|防水壳|控制线|滤镜|ND\s*镜')


def classify(row):
    """Return a reviewable decision, never relying on brand, IDs or old kind."""
    if is_car(row) or row.get('brand') in ('比亚迪', '小米汽车'):
        return dict(accessory=False, basis='car', matched='汽车单列')
    name = str(row.get('name') or '')
    categories = list(dict.fromkeys([row.get('category') or '', *(row.get('categories') or [])]))
    words = [w for w in ACCESSORY_WORDS if w.casefold() in name.casefold()]
    # Bundled accessories after 配/含/赠/送 do not change the principal product.
    principal = re.split(r'(?:[（(]?含|[（(]?赠|[（(]?送|\s配\s|\s配(?=MagSafe|无线充电盒)|[+＋])', name, maxsplit=1)[0]
    principal = re.sub(r'[（(][^）)]*(?:电池版|mAh\s*电池)[^）)]*[）)]', '', principal)
    # Splitting a bundled 含/赠 clause can leave an open parenthesis.
    principal = re.sub(r'[（(][^）)]*$', '', principal)
    # An integrated adjustable stand is a monitor feature, not a loose stand.
    principal = re.sub(r'多功能支架(?:版)?', '', principal)
    principal = re.sub(r'磁吸支架(?=充电宝)', '', principal)
    principal = re.sub(r'^无线充电盒款(?=\s*AirPods)', '', principal, flags=re.I)
    device = DEVICE.search(principal) or MODEL_DEVICE.fullmatch(principal.strip())
    lens = re.search(r'镜头(?:\s|$|[（(])', principal)
    body = re.search(r'(?:相机|机身|套机)(?:\s|$|[（(])', principal)
    # Lens/body names have priority over an erroneous accessory category, but a
    # "机身拓展板"/"镜头保护盖" is still a part.
    if (device or lens or body) and not PARTS.search(principal) and not any(w.casefold() in principal.casefold() for w in ACCESSORY_WORDS):
        return dict(accessory=False, basis='whole_device', matched=(device or lens or body).group())
    accessory_category = next((c for c in categories if c.strip().endswith('配件')), None)
    if accessory_category:
        return dict(accessory=True, basis='category', matched=accessory_category)
    if words:
        return dict(accessory=True, basis='name', matched=words)
    if re.search(r'\bMagSafe\b', name, re.I):
        return dict(accessory=True, basis='name', matched=['MagSafe'])
    return dict(accessory=False, basis='no_accessory_match', matched=None)


def fingerprint(rows):
    # Review approval is bound to identities, names and exact rule decisions.
    evidence = sorted((dict(id=r['id'], name=r.get('name'), decision=classify(r)) for r in rows), key=lambda r: (r['id'], str(r['name'])))
    return hashlib.sha256(json.dumps(evidence, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def plan(rows, previous, archive=(), reviewed_sha256=None):
    kept, excluded = [], []
    for row in rows:
        (excluded if classify(row)['accessory'] else kept).append(row)
    known = {r['id'] for r in archive}
    # Replaying cached/supplemental accessories is not a new exclusion. Existing
    # archive cannot conceal a product that has actually re-entered the release.
    previous_ids = {r['id'] for r in previous}
    newly = [r for r in excluded if r['id'] not in known or r['id'] in previous_ids]
    denominator = len({r['id'] for r in [*previous, *kept, *newly] if classify(r)['basis'] != 'car'})
    ratio = len({r['id'] for r in newly}) / denominator if denominator else 0
    digest = fingerprint(newly)
    red = ratio > .05
    audit = dict(excluded_count=len(excluded), newly_excluded_count=len({r['id'] for r in newly}),
                 denominator=denominator, newly_excluded_ratio=ratio, threshold=.05,
                 gate='red' if red else 'green', review_sha256=digest,
                 reviewed=bool(red and reviewed_sha256 == digest))
    print('accessory gate: ' + json.dumps(audit, ensure_ascii=False))
    if red and reviewed_sha256 != digest:
        raise ValueError('Accessory exclusion exceeds 5%; review this exact batch: ' + json.dumps(audit))
    archived = {r['id']: deepcopy(r) for r in archive}
    for row in excluded:
        entry = deepcopy(row)
        entry.update(excluded_reason='accessory', exclusion=classify(row))
        # Preserve the first excluded snapshot. Replayed supplements may be
        # older and less complete than the record removed from the release.
        archived.setdefault(row['id'], entry)
    return kept, list(archived.values()), audit
