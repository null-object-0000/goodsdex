"""Frozen anonymous Mi Home identity evidence. Device icons retain their role/size."""
from copy import deepcopy
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from .mijia_baike import norm

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/mihome-catalog.json'
BROAD = {'旧款机型', '家电', '其他', '智能家居', '智能家庭'}


def identity_matches(row, entry):
    old, official = norm(entry['expected_name']), norm(entry['name'])
    if entry['method'] == 'exact_name':
        return old == official
    if entry['method'] == 'core_capacity':
        capacity = entry.get('capacity', '')
        return (bool(re.fullmatch(r'\d+(?:\.\d+)?kg', capacity))
                and official == old + capacity
                and norm(str((row.get('params') or {}).get('洗涤容量', ''))) == capacity)
    return False


def apply_catalog(rows, manifest=None):
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text())
    if manifest.get('schema') != 1:
        raise ValueError('Unsupported Mi Home catalog')
    entries = {}
    for entry in manifest['items']:
        url = urlsplit(entry['source_url'])
        if (entry['id'] in entries or not entry['id'].startswith('CN:mi_cn:product:')
                or not re.fullmatch(r'[a-z0-9_]+(?:\.[a-z0-9_]+){2}',entry['model'])
                or not isinstance(entry['pd_id'],int) or entry['pd_id'] <= 0
                or url.hostname != 'home.mi.com' or url.path != '/cgi-op/api/v1/brand/h5/list'
                or not re.fullmatch('[a-f0-9]{64}',entry['source_sha256'])):
            raise ValueError('Invalid Mi Home identity evidence')
        entries[entry['id']] = entry
    result = deepcopy(rows)
    for row in result:
        e = entries.get(row['id'])
        if (not e or row.get('is_container') or row.get('brand') not in (None,'小米')
                or row.get('name') not in (e['expected_name'],e['name'])
                or not identity_matches(row,e)):
            continue
        row.update(mihome_model=e['model'],mihome_pd_id=e['pd_id'])
        row['mihome_catalog_evidence'] = {k:e[k] for k in ('method','source_url','source_sha256','category','classifications')}
        if row['name'] != e['name']:
            row.setdefault('name_raw',row['name'])
            row['name'] = e['name']
            row['name_source'] = dict(kind='official_mihome_catalog',url=e['source_url'],sha256=e['source_sha256'])
        if row.get('category') in BROAD and e.get('category'):
            row.setdefault('category_raw',row.get('category'))
            row.setdefault('categories_raw',deepcopy(row.get('categories', [])))
            row['category'] = e['category']
            row['categories'] = [e['category']]
            row['category_source'] = 'mihome_catalog'
        icon=e.get('verified_icon')
        if icon and (not row.get('image') or (row.get('image_source') == 'mihome_icon' and row.get('image') == icon['url'])):
            u=urlsplit(icon['url'])
            if (u.scheme!='https' or not (u.hostname or '').endswith(('.mi-img.com','.xiaomi.com'))
                    or not re.fullmatch('[a-f0-9]{64}',icon['sha256'])
                    or min(icon['width'],icon['height'])<=0):
                raise ValueError('Invalid device icon evidence')
            row.update(image=icon['url'],image_missing=False,image_source='mihome_icon',
                       image_source_type='official',image_source_url=e['source_url'],
                       image_scope='device_icon',image_width=icon['width'],image_height=icon['height'],
                       image_sha256=icon['sha256'],
                       image_note=f"米家官方设备图标，{icon['width']}×{icon['height']} 像素；非商城商品高清主图")
    return result


def restore_catalog_identity(rows, manifest=None):
    """Give existing date validators their frozen identity on publication replay.

    Display repairs are applied again only after all date lanes. No date field
    is changed here; both the previous and repaired names must match our proof.
    """
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text())
    entries = {e['id']: e for e in manifest['items']}
    result = deepcopy(rows)
    for row in result:
        e = entries.get(row['id'])
        if (e and row.get('mihome_model') == e['model']
                and row.get('mihome_pd_id') == e['pd_id']
                and row.get('name') == e['name']
                and identity_matches(row, e)):
            if row.get('name_raw') == e['expected_name']:
                row['name'] = row['name_raw']
            if row.get('category_source') == 'mihome_catalog' and row.get('category_raw') in BROAD:
                row['category'] = row['category_raw']
                row['categories'] = deepcopy(row.get('categories_raw', [row['category_raw']]))
    return result
