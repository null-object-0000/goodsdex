"""Exact-identity appliance spec backfill, independent of release policy.

Values come from structured official fields or text-bearing manuals. Image-only
pages are evidence of absence of structured specs, never input to OCR extraction.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

DEFAULT = Path(__file__).resolve().parents[2] / 'data/enrichment/homeappliance-params.json'
CATEGORIES = frozenset({'微波炉', '空调', '扫地机器人', '冰箱'})
OFFICIAL_HOSTS = ('home.mi.com', 'mi.com', 'mi-img.com', 'xiaomi.com', 'roborock.com', 'joyami.com')


def parse_attribute_list(items, allowed_fields):
    """No guessed aliases or units: retain the source's label and entire value."""
    result = {}
    conflicts = set()
    for i, item in enumerate(items):
        key, values = item.get('attributeName'), item.get('attributeValue')
        if key not in allowed_fields or not isinstance(values, list) or not values:
            continue
        if not all(isinstance(v, str) and v.strip() for v in values):
            continue
        value = ' / '.join(v + (item.get('unit') or '') for v in values)
        if key in result and result[key]['value'] != value:
            conflicts.add(key)
        result[key] = dict(value=value, source_field=key, raw_value=deepcopy(values),
                           locator=f'$.data.list[{i}]', method='structured_attribute')
    return {k: v for k, v in result.items() if k not in conflicts}


def parse_robot_battery(text):
    """Only a labelled battery row in a spec section; no base-station power.

    Reject contradictory capacities, multi-model tables and unlabelled numbers.
    Keep nominal/rated qualifiers instead of silently selecting the larger value.
    """
    candidates = []
    for page_number, page in enumerate(text.split('\f'), 1):
        if not re.search(r'(?:基本参数|技术参数|产品参数|规格参数)', page):
            continue
        for line in page.splitlines():
            match = re.match(r'^\s*(电\s*池(?:\s*容\s*量)?)\s*[:：]?\s*(.+)', line)
            if not match:
                continue
            value = re.split(r'\s{3,}', match[2].strip())[0]
            if not re.search(r'\d\s*m[Aa][Hh]', value):
                continue
            # Full battery descriptions, e.g. 14.4V/5200mAh 锂电池, are kept.
            if len(value) > 100 or re.search(r'型号|充电座|基座| / ', value):
                continue
            if len(re.findall(r'\d+\s*m[Aa][Hh]', value)) > 1 and not all(
                    word in value for word in ('额定', '标称')):
                continue
            candidates.append(dict(value=value, source_field=match[1].strip(), raw_value=line.strip(),
                quote=line.strip(), locator=f'PDF page {page_number}: battery row',
                page=page_number, method='pdf_text'))
    values = {re.sub(r'\s+', '', c['value']) for c in candidates}
    return {'电池容量': candidates[0]} if len(values) == 1 else {}


def apply_params(rows, manifest=None):
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text()) if DEFAULT.exists() else {'schema': 1, 'items': []}
    if manifest.get('schema') != 1:
        raise ValueError('Unsupported appliance parameter evidence')
    entries = {}
    for entry in manifest['items']:
        if entry['id'] in entries or entry['category'] not in CATEGORIES or not entry['expected_name']:
            raise ValueError('Invalid appliance identity')
        if not entry.get('model') and entry.get('params'):
            raise ValueError('Parameter evidence requires exact model identity')
        if entry.get('identity_method') == 'audited_product_id':
            proof = entry.get('identity_evidence') or {}
            if (not entry['id'].startswith('CN:mi_cn:product:') or
                    proof != dict(id=entry['id'], name=entry['expected_name'], model=entry.get('model'))):
                raise ValueError('Invalid exact product ID evidence')
        for key, proof in entry.get('params', {}).items():
            host = urlsplit(proof['url']).hostname or ''
            official = proof['source_type'] == 'official' and any(host == h or host.endswith('.' + h) for h in OFFICIAL_HOSTS)
            third_party = proof['source_type'] == 'third_party' and host == 'detail.zol.com.cn' and proof.get('reviewed_model') == entry.get('model')
            if (not (official or third_party)
                    or not re.fullmatch('[0-9a-f]{64}', proof['sha256'])
                    or proof['method'] not in ('structured_attribute', 'pdf_text', 'official_html', 'third_party_html')
                    or not proof['locator'] or not proof['source_field'] or proof['value'] in (None, '', [], {})):
                raise ValueError('Invalid structured/manual spec evidence')
        entries[entry['id']] = entry
    result = deepcopy(rows)
    for row in result:
        entry = entries.get(row['id'])
        if not entry or row.get('name') != entry['expected_name']:
            continue
        if row.get('is_container'):
            if not row.get('params'):
                row['params_missing'] = 'container_scope_unverified'
                row['params_missing_evidence'] = deepcopy(entry.get('attempts', []))
            continue
        model = row.get('miio_model') or row.get('mihome_model')
        if model and model != entry.get('model'):
            continue
        if entry.get('identity_method') == 'existing_model' and model != entry.get('model'):
            continue
        if entry.get('deferred_reason'):
            if not row.get('params'):
                row['params_missing'] = entry['deferred_reason']
                row['params_missing_evidence'] = deepcopy(entry.get('attempts', []))
            continue
        params = row.setdefault('params', {})
        sources = row.setdefault('params_sources', {})
        conflicts = {}
        for key, proof in entry.get('params', {}).items():
            if key in params and params[key] != proof['value']:
                conflicts[key] = deepcopy(proof)
            elif key not in params:
                params[key] = deepcopy(proof['value'])
                sources[key] = {k: deepcopy(v) for k, v in proof.items() if k != 'value'}
        if conflicts:
            row['params_conflicts'] = conflicts
        if not sources:
            row.pop('params_sources', None)
        if sources:
            kinds = {v.get('source_type', 'unknown') for v in sources.values()}
            row['params_source_type'] = next(iter(kinds)) if len(kinds) == 1 else 'mixed'
        if params:
            row.pop('params_missing', None)
        else:
            row['params_missing'] = entry.get('params_missing', 'page_no_spec')
            row['params_missing_evidence'] = deepcopy(entry.get('attempts', []))
    return result


def parse_manual_scalars(text, category):
    """Read bounded label/value cells in actual spec sections, never prose/OCR.

    Only unambiguous scalar cells are accepted. Conflicting repetitions (including
    model columns, indoor/outdoor units and charging bases) remain unselected.
    """
    rules = {
        '微波炉': {
            '容量': (r'额定容积', r'\d+(?:\.\d+)?\s*L'),
            '额定功率': (r'额定输入功率', r'\d+(?:\.\d+)?\s*W'),
            '能效等级': (r'能效等级', r'[1-5一二三四五]\s*级'),
            '噪音值': (r'噪\s*音\s*值', r'\d+(?:\.\d+)?\s*dB\s*\(A\)'),
            '产品尺寸': (r'产品尺寸', r'\d+\s*[×x*]\s*\d+\s*[×x*]\s*\d+\s*mm'),
            '产品型号': (r'产品型号', r'[A-Z][A-Za-z0-9-]{3,25}'),
        },
        '冰箱': {
            '总容量': (r'(?:额定)?总容积', r'\d+(?:\.\d+)?\s*L'),
            '能效等级': (r'能效等级', r'[1-5一二三四五]\s*级'),
            '噪音值': (r'噪声(?:值)?|噪音值', r'\d+(?:\.\d+)?\s*dB\s*\(A\)'),
        },
        '空调': {
            '能效等级': (r'能效等级', r'[1-5一二三四五]\s*级'),
            '额定频率': (r'额定频率', r'\d+\s*Hz'),
            '额定电压': (r'额定电压', r'\d+\s*V\s*[~～]?'),
        },
    }.get(category, {})
    found = {key: [] for key in rules}
    for pn, page in enumerate(text.split('\f'), 1):
        if not re.search(r'(?:基本参数|技术参数|产品参数|规格参数|性能参数|技术性能)', page):
            continue
        for key, (label, value) in rules.items():
            # Columns must terminate with a cell gap, a newline, or end of page.
            pattern = rf'(?<!\S)({label})\s*[:：]?\s+({value})(?=\s{{2,}}|\n|$)'
            for match in re.finditer(pattern, page):
                # Reject a second numeric model column following the selected cell.
                tail = page[match.end():].split('\n', 1)[0]
                if re.match(r'\s+\d', tail):
                    continue
                line = page[page.rfind('\n',0,match.start())+1:page.find('\n',match.end()) if '\n' in page[match.end():] else len(page)]
                found[key].append(dict(value=match[2], source_field=match[1], raw_value=match[2],
                    quote=line.strip(), locator=f'PDF page {pn}: {match[1]}', page=pn, method='pdf_text'))
    return {key: values[0] for key, values in found.items() if values and
            len({re.sub(r'\s+', '', v['value']) for v in values}) == 1}


def parse_aircon_table(text):
    """Select scalar whole-unit tables or cells identical in every model column.

    Differing model columns and indoor/outdoor dimensions stay unselected.
    """
    results = {}
    conflicting = set()
    for pn,page in enumerate(text.split('\f'),1):
        if '基本参数' not in page:
            continue
        model_lines=re.findall(r'^\s*(?:整机型号|产品型号)\s+([^\n]+)',page,re.M)
        if len(model_lines)!=1:
            continue
        models=re.split(r'\s+', model_lines[0].strip())
        if not 1 <= len(models) <= 5 or not all(re.fullmatch(r'[A-Za-z0-9_/().-]+',m) for m in models):
            continue
        rules={
            '能效等级': (r'能效等级', r'[1-5](?:级)?', ''),
            '适用面积': (r'适用面积[（(](?:㎡|m²|m2)[）)]', r'\d+(?:\s*[-~～]\s*\d+)?', '㎡'),
            '制冷量（整机）': (r'额定制冷量[（(]W[）)]', r'\d+(?:[（(][0-9~～-]+[）)])?', 'W'),
            '制热量（整机）': (r'额定制热量[（(]W[）)]', r'\d+(?:[（(][0-9~～-]+[）)])?(?:\s*\+\s*\d+)?', 'W'),
        }
        for key,(label,value,unit) in rules.items():
            for match in re.finditer(rf'^[ \t]*({label})[ \t]+([^\n]+)$',page,re.M):
                cells=re.split(r'\s{2,}',match[2].strip())
                if (len(cells)!=len(models) or len(set(cells))!=1
                        or not re.fullmatch(value,cells[0])):
                    continue
                raw=cells[0];v=raw+unit
                if key=='能效等级' and not v.endswith('级'):v+='级'
                proof=dict(value=v,source_field=match[1],raw_value=raw,quote=match[0].strip(),
                           locator=f'PDF page {pn}: {match[1]}',page=pn,method='pdf_text',hardware_models=models,selection='single_model' if len(models)==1 else 'all_columns_explicitly_equal')
                if key in results and results[key]['value']!=v:conflicting.add(key)
                results[key]=proof
    return {k:v for k,v in results.items() if k not in conflicting}


def named_capacities(name):
    """Retain both sides of 521L/523L and 610/636L device-profile names."""
    values=set(re.findall(r'(\d+(?:\.\d+)?)\s*L', name, re.I))
    values.update(re.findall(r'(\d+(?:\.\d+)?)\s*[/／]\s*\d+(?:\.\d+)?\s*L',name,re.I))
    return {v+'L' for v in values}


def parse_fridge_table(text, expected_name):
    """A shared manual can prove only cells identical for every named capacity.

    In particular, a 521L-only manual cannot fill a 521L/523L device profile.
    """
    results={};conflicting=set();required=named_capacities(expected_name)
    for pn,page in enumerate(text.split('\f'),1):
        if not re.search('基本参数|参数信息|技术参数',page):continue
        model=re.search(r'^[ \t]*产品型号[ \t]+([^\n]+)$',page,re.M)
        capacity=re.search(r'^[ \t]*总容积[ \t]+([^\n]+)$',page,re.M)
        if not model or not capacity:continue
        models=re.split(r'\s+',model[1].strip());capacities=re.split(r'\s{2,}',capacity[1].strip())
        if (not 1<=len(models)<=5 or len(models)!=len(capacities)
                or not all(re.fullmatch(r'BCD-[A-Za-z0-9-]+',m) for m in models)
                or not all(re.fullmatch(r'\d+(?:\.\d+)?L',v) for v in capacities)
                or not required.issubset(set(capacities))):continue
        rules={'总容量':('总容积',r'\d+(?:\.\d+)?L'),
               '冷冻室容积':('冷冻室容积',r'\d+(?:\.\d+)?L'),
               '冷藏室容积':('冷藏室容积',r'\d+(?:\.\d+)?L'),
               '变温室容积':('变温室容积',r'\d+(?:\.\d+)?L'),
               '能效等级':('能效等级',r'[1-5]级'),
               '噪音值':(r'噪声（声功率级）',r'\d+(?:\.\d+)?dB\(A\)')}
        for key,(label,value) in rules.items():
            for match in re.finditer(rf'^[ \t]*({label})[ \t]+([^\n]+)$',page,re.M):
                cells=re.split(r'\s{2,}',match[2].strip())
                if len(cells)!=len(models) or len(set(cells))!=1 or not re.fullmatch(value,cells[0]):continue
                v=cells[0];proof=dict(value=v,source_field=match[1],raw_value=v,quote=match[0].strip(),
                    locator=f'PDF page {pn}: {match[1]}',page=pn,method='pdf_text',hardware_models=models,
                    covered_capacities=capacities,scope_quote=model[0].strip()+'\n'+capacity[0].strip(),
                    selection='single_model' if len(models)==1 else 'all_columns_explicitly_equal')
                if key in results and results[key]['value']!=v:conflicting.add(key)
                results[key]=proof
    return {k:v for k,v in results.items() if k not in conflicting}
