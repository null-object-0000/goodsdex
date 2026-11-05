"""Reviewed legacy inventory, source time semantics and lossless family annotations."""
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import re

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/mi-legacy-categories.json'


def category_of(name):
    from goodsdex.accessories import classify
    from goodsdex.services import classify_non_goods
    if classify_non_goods({'name':name}):
        return '服务'
    if classify({'name':name})['accessory']:
        return '配件'
    rules=[
      ('笔记本',r'笔记本|游戏本'),('手机',r'^(?:红米\d|红米Note|小米(?:\d|MIX|Max))'),
      ('电视',r'电视'),('相机',r'微单|全景相机|小相机|云台相机|小默相机'),
      ('配件',r'插线板|电力猫|转换器|遥控器|主刷|边刷|主刷罩|机器人传感器|载物筐|手机云台|逆变器'),
      ('服务',r'会员年卡'),('配件',r'米粉卡'),
      ('服饰',r'板鞋|运动鞋|T恤|羽绒服'),('箱包',r'包$|包\s|双肩包|胸包|登机箱|旅行箱|拉杆箱'),
      ('眼镜',r'太阳镜|护目镜|眼镜架|近视镜'),('出行',r'平衡车|自行车|滑板车'),
      ('车载设备',r'后视镜|记录仪'),('摄像机',r'摄像机'),('无人机',r'无人机|小飞机'),
      ('智能家居',r'传感器|智能灯泡|随身灯|吸顶灯|球泡灯|床头灯|感应夜灯|多功能网关|智能插座|报警器|温湿度计|智能闹钟'),
      ('路由器',r'路由器|WiFi放大器'),('耳机',r'耳机'),('音箱',r'音箱|家庭影院|故事机'),
      ('电视盒子',r'小米盒子'),('VR设备',r'VR'),('充电宝',r'移动电源'),('鼠标',r'鼠标'),
      ('净水器',r'净水器'),('电饭煲',r'电饭煲'),('空气净化器',r'空气净化器'),
      ('健康测量',r'血压计|体脂秤|电子厨房秤|PM2.5检测仪'),('家纺家具',r'乳胶枕|护颈枕|床垫|沙发|针织件套|腰靠|毛巾|浴巾'),
      ('学习机',r'学习机'),('玩具',r'积木|机器人'),('生活用品',r'签字笔|口罩|折叠伞|手电筒|保温杯|驱蚊器'),
      ('手环',r'手环'),('手表',r'手表|石英表'),('乐器',r'尤克里里'),('首饰',r'吊坠|手链'),
      ('电磁炉',r'电磁炉'),('投影仪',r'投影仪'),('风扇',r'落地扇'),('料理机',r'料理机'),
      ('电动牙刷',r'电动牙刷'),('对讲机',r'对讲机'),('儿童定位设备',r'定位电话'),
    ]
    return next((cat for cat,pat in rules if re.search(pat,name,re.I)),None)

def family(row):
    name = row.get('name') or ''
    attrs = deepcopy(row.get('attrs') or {})
    series = None
    if row.get('category') == '手机':
        match = re.match(r'((?:红米(?:Note\s*)?|小米(?:MIX\s*|Max\s*)?)\d+(?:[sSXx]|\s*(?:SE|Pro|Plus))?)', name)
        series = match.group(1).strip() if match else name
        if re.match(r'^红米5(?:A| Plus)?(?:\s|$)', name):
            series = '红米5 系列'
        if name.startswith(series):
            suffix = name[len(series):].strip()
            if suffix:
                attrs['configuration'] = suffix
        attrs['model'] = re.split(r'\s+\d+G', name)[0]
    elif row.get('category') == '笔记本':
        series = ('小米笔记本 Air' if re.search(r'Air', name, re.I) else
                  '小米笔记本 Pro' if re.search(r'Pro', name) else
                  '小米游戏本' if '游戏本' in name else '小米笔记本')
        size = re.search(r'(\d+(?:\.\d+)?)\s*["″英寸]', name)
        if size:
            attrs['size'] = size.group(1) + '英寸'
        cpu = re.search(r'(?:第?[七八九十7-9]代)?(?:四核|六核|八核)?(?:i[3579]|m3)', name, re.I)
        if cpu:
            attrs['cpu'] = cpu.group()
        gpu = re.search(r'MX\d+|GTX\d+|集显', name)
        if gpu:
            attrs['gpu'] = gpu.group()
        attrs['configuration'] = name.replace(series, '', 1).strip()
    if not series:
        return
    memory = re.search(r'(\d+)\s*G(?:B)?\s*\+\s*(\d+)\s*G(?:B)?', name, re.I)
    if memory:
        attrs.update(ram=memory[1]+'GB', storage=memory[2]+'GB')
    else:
        values = re.findall(r'(?<![\w.])(\d+)\s*G(?:B)?\b', name, re.I)
        if row.get('category') == '笔记本' and values:
            attrs['ram'] = values[0]+'GB'
            if len(values)>1:
                attrs['storage'] = values[1]+'GB'
        elif values:
            attrs['storage'] = values[-1]+'GB'
    color = re.search(r'(深空灰|银色|皓月白|翡翠色|透明探索版)$', name)
    if color:
        attrs['color'] = color[1]
    generation = re.search(r'(?:第?八代|8代|四核增强)', name)
    if generation:
        attrs['generation'] = generation.group()
    row.update(series=series, attrs=attrs, attrs_source='legacy_name_literal',
               family_group_key=json.dumps([row.get('brand') or '小米', series],ensure_ascii=False,separators=(',',':')),
               series_key=json.dumps([row.get('brand') or '小米',series,attrs.get('size'),attrs.get('generation')],ensure_ascii=False,separators=(',',':')))


def apply_legacy_catalog(rows, manifest=None):
    document = json.loads(DEFAULT.read_text()) if manifest is None else manifest
    entries = {e['id']: e for e in document['items']}
    if document.get('schema') != 1 or len(entries) != document['scope_count']:
        raise ValueError('Invalid legacy category inventory')
    result = deepcopy(rows)
    for row in result:
        entry = entries.get(row['id'])
        legacy = (row.get('category') == '待人工' and row.get('category_review_source') == 'mi-legacy-categories-v1') or row.get('category') == '旧款机型' or '旧款机型' in (row.get('categories') or [])
        if not entry and not legacy:
            # Existing correctly classified Air reference rows belong to the same
            # family; preserve their facts and only add the grouping annotation.
            if (str(row.get('id','')).startswith('CN:mi_cn:') and row.get('brand') in (None,'小米') and row.get('category') == '笔记本'
                    and row.get('discontinued') is True
                    and re.match(r'小米笔记本\s*Air', row.get('name') or '', re.I)):
                row['category_review_source'] = 'mi-legacy-categories-v1'
                family(row)
            continue
        if entry and not row.get('source_url') and entry.get('reviewed_source_url'):
            row['source_url'] = entry['reviewed_source_url']
        category = entry['category'] if entry else category_of(row.get('name') or '')
        row.update(category=category or '待人工', categories=[category or '待人工'],
                   category_review_required=not bool(category), category_review_source='mi-legacy-categories-v1', discontinued=True, status='retired', is_historical=True)
        # Reclassification also invalidates previously projected source-bucket facets.
        if row.get('original_category') == '旧款机型':
            row.pop('original_category', None)
        row.pop('category_l1', None)
        row.pop('category_l2', None)
        if row.get('price') is None:
            row.update(price=None, price_missing='page_no_price')
        approved_image = (entry or {}).get('reviewed_image_fields')
        if (approved_image and approved_image.get('image_scope') == 'model'
                and not row.get('image') and row.get('image_status') != 'official_unavailable'):
            row.update(deepcopy(approved_image))
            if row.get('image_status') == 'missing':
                row.pop('image_status')
        # A family reference is useful evidence, but not this model's main image.
        if row.get('image') and row.get('image_scope') == 'series':
            keys = [k for k in row if k.startswith('image_') and k not in ('image_missing','image_status')]
            row['reference_image'] = dict(url=row['image'], **{k:row[k] for k in keys})
            for key in keys:
                row.pop(key, None)
            row.update(image=None, image_scope=None, image_status='missing')
        if not row.get('image') or row.get('image_status') == 'official_unavailable':
            row.update(image=None, image_missing='page_no_image')
        else:
            row.pop('image_missing', None)
        archived = entry.get('archived_at') if entry else None
        archived_url = entry.get('archived_source_url') if entry else None
        if not archived:
            match = re.search(r'web\.archive\.org/web/(\d{14})', str(row.get('source_url') or ''))
            if match:
                archived = datetime.strptime(match[1], '%Y%m%d%H%M%S').isoformat()+'Z'
                archived_url = row['source_url']
        if archived:
            row.update(archived_at=archived, archived_source_url=archived_url)
        captured = entry.get('captured_at') if entry else row.get('fetched_at')
        # A later real collection stays later; the snapshot is never a capture.
        current = row.get('captured_at')
        if current and current != archived and str(current)[:4] >= '2026':
            captured = current
        row.update(captured_at=captured, captured_at_unknown=not bool(captured),
                   captured_at_basis=(entry.get('captured_at_basis') if entry else 'source_record.fetched_at') if captured else 'unknown')
        family(row)
    return result
