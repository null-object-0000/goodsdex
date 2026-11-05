"""Release-only apparel policy. Source categories and full facts stay intact."""
from copy import deepcopy
import re

CATEGORY_WORDS = ('服饰', '服装', '鞋', '箱包', '内衣', '家居服')
# Source leaf labels for the requested category families, not product identities.
CATEGORY_LEAVES = (
    '睡衣', '睡袍', '浴袍', '运动鞋', '拖鞋', '双肩包', '单肩包', '胸包',
    '小背包', '背包', '旅行箱', '行李箱', '登机箱',
)
NAME_WORDS = (
    '睡衣', '睡袍', '浴袍', '家居服', '内衣', 'T恤', '衬衫', '卫衣', '外套',
    '西裤', '西装', '连衣裙', '袜', '鞋', '拖鞋', '帽', '围巾', '背包', '行李箱',
)
# A source search category may include unrelated merchandise (e.g. 运动鞋/水杯).
# Explicit appliance/digital or non-apparel leaf evidence wins such conflicts.
PROTECTED_CATEGORY = re.compile(
    r'家电|数码|洗衣机|洗烘|空调|冰箱|电视|净水器|净饮机|洗地机|吸尘器|'
    r'扫地机器人|除湿机|加湿器|空气净化器|电饭煲|电磁炉|微蒸烤|洗碗机|'
    r'吹风机|剃须刀|电暖器|风扇|手机|笔记本|电脑|平板|相机|摄像机|'
    r'耳机|音箱|路由器|显示器|打印机|投影仪|智能|手表|手环|无人机|'
    r'水杯|水壶|清洁剂|清洁液|喷雾|护理剂|灯具|台灯|烟灶|插座|门锁|对讲机|'
    r'电源|牙刷|洗手机|除螨仪|体脂秤|体重秤|料理机|家庭屏|螺丝刀|门铃|'
    r'走步机|工作站|穿戴|云台|传输|键鼠|电动|微波炉|烤箱|消毒柜|摄影|键盘|数据线')
BUNDLED = re.compile(r'(?:含|赠送|附赠|赠|送)[^，,;；。|]*?(?:睡衣|睡袍|浴袍|家居服|内衣)')


def categories(row):
    values = [row.get(k) for k in ('category_l1', 'category_l2', 'category')]
    values += row.get('categories') or []
    return list(dict.fromkeys(str(c).strip() for c in values if c))


def classify_apparel(row):
    cats = categories(row)
    name = str(row.get('name') or '')
    # Included apparel never establishes the identity of a mixed set.
    if BUNDLED.search(name) or any(PROTECTED_CATEGORY.search(c) for c in cats):
        return None
    for category in cats:
        # Match complete labels/path segments, never a character inside a noun
        # such as 鞋护理剂 or 内衣物洗烘一体机.
        labels = re.split(r'[/＞>、|]', category)
        for label in labels:
            if label.strip() in (*CATEGORY_WORDS, *CATEGORY_LEAVES):
                return dict(reason='apparel', basis='category', matched=category,
                            matched_rule='category', matched_text=category)
    for word in NAME_WORDS:
        match = re.search(re.escape(word), name, re.I)
        if match:
            return dict(reason='apparel', basis='name', matched=match.group(),
                        matched_rule='name', matched_text=match.group())
    return None


def plan_apparel(rows, archive):
    archived = {r['id']: deepcopy(r) for r in archive}
    kept = []
    for row in rows:
        if classify_apparel(row):
            archived.setdefault(row['id'], deepcopy(row))
        else:
            kept.append(row)
    return kept, list(archived.values())
