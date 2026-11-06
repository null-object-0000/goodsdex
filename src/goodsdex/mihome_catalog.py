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
    result = restore_catalog_identity(rows, manifest)
    for row in result:
        e = entries.get(row['id'])
        if (not e or row.get('is_container') or row.get('brand') not in (None,'小米')
                or row.get('name') not in (e['expected_name'],e['name'])
                or not identity_matches(row,e)):
            continue
        row.update(mihome_model=e['model'],mihome_pd_id=e['pd_id'])
        row['mihome_catalog_evidence'] = {k:e[k] for k in ('method','source_url','source_sha256','category','classifications')}
        row['name_mihome'] = e['name']
        row['category_mihome'] = e.get('category')
        row.setdefault('miio_model', e['model'])
        icon = e.get('verified_icon')
        if icon:
            u = urlsplit(icon['url'])
            if (u.scheme != 'https' or not (u.hostname or '').endswith(('.mi-img.com', '.xiaomi.com'))
                    or not re.fullmatch('[a-f0-9]{64}', icon['sha256'])
                    or icon['width'] != 168 or icon['height'] != 168):
                raise ValueError('Invalid device icon evidence')
            public_url = icon.get('public_url', icon['url'])
            if icon.get('public_url') and public_url != u._replace(query='', fragment='').geturl():
                raise ValueError('Unverified public device icon URL')
            row['image_mihome'] = dict(icon, url=public_url, source_url=icon['url'], size='168x168', source='mihome_directory',
                                       scope='device_icon', note='168×168 设备图标，非商品主图')
        row['catalog_display'] = display_catalog(row, e)
        if row['catalog_display']['name_source'] == 'mihome_directory' or not row.get('name_source'):
            row['name_source'] = row['catalog_display']['name_source']
    return result


def display_catalog(row, entry=None):
    """Resolve display only; whitespace/case never qualifies as a name repair.

    Truncation requires frozen identity/capacity proof or explicit ellipsis.
    Categories use reviewed broad-to-leaf relationships, not string length.
    """
    official, other = row.get('name'), row.get('name_mihome')
    truncated = bool(official and other and (
        (entry and entry.get('method') == 'core_capacity' and identity_matches(row, entry))
        or (re.search(r'(?:\.\.\.|…)$', official) and
            norm(other).startswith(norm(re.sub(r'(?:\.\.\.|…)+$', '', official))))))
    use_name = bool(other and (not official or truncated))
    icon = row.get('image_mihome') or {}
    use_icon = not row.get('image') and bool(icon.get('url'))
    category = row.get('category')
    use_category = bool(row.get('category_mihome') and (not category or category in BROAD))
    return dict(name=other if use_name else official, name_original=official,
                name_source='mihome_directory' if use_name else 'xiaomi_store',
                name_reason='official_empty_or_verified_truncation' if use_name else 'official_sales_name',
                image=icon.get('url') if use_icon else row.get('image'),
                image_source='mihome_directory' if use_icon else row.get('image_source', 'xiaomi_store'),
                image_scope='device_icon' if use_icon else row.get('image_scope', 'product_image'),
                image_note=icon.get('note') if use_icon else None,
                image_width=icon.get('width') if use_icon else row.get('image_width'),
                image_height=icon.get('height') if use_icon else row.get('image_height'),
                category=row.get('category_mihome') if use_category else category,
                category_source='mihome_directory' if use_category else 'xiaomi_store')


def restore_catalog_identity(rows, manifest=None):
    """Undo legacy writes only with exact old value, identity and provenance.

    Restore absent keys too; preserve later unrelated edits and all date fields.
    """
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text())
    entries = {e['id']: e for e in manifest['items']}
    result = deepcopy(rows)
    for row in result:
        e = entries.get(row['id'])
        if not (e and row.get('mihome_model') == e['model']
                and row.get('mihome_pd_id') == e['pd_id'] and identity_matches(row, e)):
            continue
        originals = e.get('legacy_original_fields', {})
        def restore(fields):
            if 'legacy_original_fields' not in e:
                return
            for field in fields:
                if field in originals:
                    row[field] = deepcopy(originals[field])
                else:
                    row.pop(field, None)
        source = row.get('name_source')
        if (row.get('name') == e['name'] and row.get('name_raw') == e['expected_name']
                and isinstance(source, dict) and source.get('kind') == 'official_mihome_catalog'):
            row['name'] = e['expected_name']
            restore(('name', 'name_raw', 'name_source'))
        if (row.get('category_source') == 'mihome_catalog' and row.get('category') == e.get('category')
                and row.get('category_raw') in BROAD):
            row['category'] = row['category_raw']
            row['categories'] = deepcopy(row.get('categories_raw', [row['category_raw']]))
            restore(('category', 'categories', 'category_raw', 'categories_raw', 'category_source'))
        icon = e.get('verified_icon')
        if icon and row.get('image_source') == 'mihome_icon' and row.get('image') == icon['url']:
            restore(('image', 'image_missing', 'image_source', 'image_source_type', 'image_source_url',
                     'image_scope', 'image_width', 'image_height', 'image_sha256', 'image_note'))
    return result
