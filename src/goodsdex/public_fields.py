"""Exact public-field policy. Never infer aliases from substrings or strip model tokens."""
from copy import deepcopy
import re

PROTECTED_IDS = {
    'CN:mi_cn:product:20425': 'true_variant',
    'CN:mi_cn:product:22172': 'true_variant',
    'CN:mi_cn:product:10050186': 'source_drift',
}
OPERATIONAL_KEYS = frozenset({
    'evaluate_total', 'evaluate_real', 'qa_total', 'favorite_total', 'favorites_count',
    'favorite_count', 'collect_total', 'collect_count', 'collection_count',
    'review_count', 'reviews_count', 'rating_count', 'question_count', 'qa_count',
    '评价数', '评价数量', '评论数', '问答数', '问答数量', '收藏数', '收藏数量',
})
# Public Chinese spellings already used by the API facts projection.
PARAM_ALIASES = {
    'care.ion': '护发因子', 'heat.levels': '温度挡位', 'motor.rpm': '马达转速',
    'noise.max': '最大噪音', 'power.rated': '额定功率', 'speed.levels': '风速挡位',
    'wind.speed': '最大风速', 'wind.volume': '最大风量',
    'cpu': 'CPU型号', 'cpu.clock': 'CPU主频', 'nfc': 'NFC',
    'battery': '电池容量', 'cam.front': '前置摄像头', 'cam.rear': '后置摄像头',
    'charge.wired': '有线快充', 'charge.wireless': '无线快充',
    'fingerprint': '指纹识别', 'ir': '红外遥控', 'network': '网络类型',
    'port': '数据接口', 'ram': '运行内存', 'rom': '存储容量',
    'screen.res': '屏幕分辨率', 'screen.size': '屏幕尺寸', 'screen.type': '屏幕',
    'sim': '网络模式', 'thickness': '机身厚度',
}


def normalize_params(params):
    output = {}
    for key, value in params.items():
        if key in OPERATIONAL_KEYS:
            continue
        target = PARAM_ALIASES.get(key, key)
        if target in output and output[target] != value:
            raise ValueError(f'Conflicting parameter aliases: {key} -> {target}')
        output[target] = deepcopy(value)
    return output


def normalize_public_row(row):
    output = deepcopy(row)
    if row.get('id') in PROTECTED_IDS:
        return output
    # These aliases describe Xiaomi's resolved view, not arbitrary other sources.
    if str(row.get('id', '')).startswith('CN:mi_cn:'):
        if isinstance(row.get('params'), dict):
            output['params'] = normalize_params(row['params'])
        name = output.get('name')
        if isinstance(name, str) and not row.get("name_source"):
            name = re.sub(r'\s*系列$', '', name)
            # A container may append its child label, already present in the name.
            head, sep, tail = name.rpartition(' ')
            if (sep and tail in head and
                    re.fullmatch(r'(?:反渗透滤芯|[0-9]+号滤芯（PPC）)', tail)):
                name = head
            output['name'] = name
    else:
        if isinstance(row.get('params'), dict):
            output['params'] = {k: deepcopy(v) for k, v in row['params'].items()
                                if k not in OPERATIONAL_KEYS}
    return {k: v for k, v in output.items() if k not in OPERATIONAL_KEYS}


def prepare_group(rows):
    """Missing params are absence, not disagreement; fill only compatible same-gid rows.

    Brand, category and price semantics stay with the strict existing merger.
    Conflicting nonempty values always keep the entire original group.
    """
    if any(row.get('id') in PROTECTED_IDS for row in rows):
        return deepcopy(rows)
    prepared = [normalize_public_row(row) for row in rows]
    gids = {str(row.get('gid')) for row in rows}
    if (len(gids) != 1 or any(row.get('gid') in (None, '') for row in rows)
            or not all(str(row.get('id', '')).startswith('CN:mi_cn:') for row in rows)):
        return prepared
    union = {}
    for row in prepared:
        for key, value in (row.get('params') or {}).items():
            if key in union and union[key] != value:
                return prepared
            union[key] = value
    # from_container is provenance: preserve True when other rows lack the key.
    provenance = {row['from_container'] for row in rows if 'from_container' in row}
    for row in prepared:
        if union or any('params' in r for r in rows):
            row['params'] = deepcopy(union)
        if len(provenance) == 1:
            row['from_container'] = next(iter(provenance))
    return prepared


def assert_public_fields(rows):
    """Fail publication if a future publisher bypasses the field policy."""
    for row in rows:
        if row.get('id') in PROTECTED_IDS:
            continue  # Explicit original-row preservation exception.
        params = row.get('params') or {}
        bad = (set(params) | set(row)) & OPERATIONAL_KEYS
        if bad:
            raise ValueError(f'Operational fields in public product {row["id"]}: {sorted(bad)}')
        if str(row.get('id', '')).startswith('CN:mi_cn:') and set(params) & PARAM_ALIASES.keys():
            raise ValueError(f'Unnormalized public params: {row["id"]}')
