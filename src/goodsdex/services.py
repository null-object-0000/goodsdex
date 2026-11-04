"""Conservative name-only service decisions, with independently archived facts."""
import re
from copy import deepcopy

MODEL = re.compile(r'[A-Za-z]|\d|[零一二三四五六七八九十]+代|型号|款')
OTHER = ('延保服务', '上门清洗', '检测服务', '拆旧费', '上门勘测服务', '上门维修', '清洁保养服务', '清洁保养套装服务', '屏幕换新服务', '后盖换新服务', '勘测服务')


def classify_service(row):
    name = str(row.get('name') or '').strip()
    # Product descriptions and bundles must never establish a service identity.
    if re.search(r'免安装|安装尺寸|安装套件|安装组件|赠|附赠|含安装|送安装', name):
        return None
    for word in ('安装服务', '安装调试', '上门安装'):
        if word in name:
            return dict(reason='service:installation', basis='name', matched=word)
    if name.endswith('安装') and not MODEL.search(name[:-2]):
        return dict(reason='service:installation', basis='name_suffix_without_model', matched='安装')
    for word in OTHER:
        if word in name:
            return dict(reason='service:other', basis='name', matched=word)
    return None


def plan_services(rows, archive):
    kept = []
    archived = {r['id']: deepcopy(r) for r in archive}
    for row in rows:
        decision = classify_service(row)
        if decision:
            archived.setdefault(row['id'], deepcopy(row))
        else:
            kept.append(row)
    return kept, list(archived.values())
