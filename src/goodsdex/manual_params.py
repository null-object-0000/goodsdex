"""Conservative, text-only Mi Home manual evidence and replay. Never OCR.

Only complete, same-line label/value cells in bounded specification sections
are accepted. Multiple model columns and contradictory repeated fields are rejected.
Units and value typography are preserved verbatim (no conversion).
"""
from copy import deepcopy
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

DEFAULT = Path(__file__).resolve().parents[2] / 'data/enrichment/manual-params.json'
HEADING = re.compile(r'^\s*(?:基本参数(?:信息)?|技术参数|产品参数|规格参数|参数信息|产品规格|技术规格)\s*$')
STOP = re.compile(r'^\s*(?:保修|注意事项|技术参数说明|产品中有害物质|食品接触|故障|使用说明|注[：:1一]|\*|警告)')
# Closed labels and full-cell value shapes: an unknown suffix invalidates the cell.
RULES = {
    '能效等级': r'[1-5一二三四五]\s*级',
    **{k: r'(?:Φ|φ|Ø)?\d+(?:\.\d+)?\s*[×xX*]\s*\d+(?:\.\d+)?(?:\s*[×xX*]\s*\d+(?:\.\d+)?)?\s*mm' for k in ('尺寸','产品尺寸','外形尺寸')},
    '电池容量': r'\d+\s*mAh(?:[（(]额定容量[）)]\s*[，,、]\s*\d+\s*mAh[（(]标称容量[）)])?',
    '电池': r'(?:\d+(?:\.\d+)?V[/／])?\d+\s*mAh(?:\s*锂电池)?',
    '综合耗电量': r'\d+(?:\.\d+)?\s*kW[·•]?h/24h',
    '年耗电量': r'\d+(?:\.\d+)?\s*kW[·•]?h/a',
    '冷冻能力': r'\d+(?:\.\d+)?\s*kg/(?:12|24)h',
    '冷却能力': r'\d+(?:\.\d+)?\s*kg/(?:12|24)h',
    '额定输入': r'\d+\s*V[~～]?\s*\d+\s*Hz',
    '电源规格': r'\d+\s*V[~～]?\s*[/／]\s*\d+\s*Hz',
}
# Per-label dimensions prevent accepting a unit from the wrong physical quantity.
for _keys, _shape in (
    (('额定电压','充电电压'), r'\d+(?:\.\d+)?\s*V[~～]?'),
    (('额定功率','额定输入功率','微波输出功率','额定洗涤功率','额定脱水功率'), r'\d+(?:\.\d+)?\s*(?:W|kW)'),
    (('额定频率','额定微波频率'), r'\d+(?:\.\d+)?\s*(?:Hz|MHz)'),
    (('额定电流',), r'\d+(?:\.\d+)?\s*A'),
    (('产品净重','主机净重','净重','毛重','额定洗涤容量','洗涤容量','额定脱水容量','脱水容量'), r'\d+(?:\.\d+)?\s*kg'),
    (('额定容积','总容积','冷藏室容积','冷冻室容积','变温室容积','额定容量'), r'\d+(?:\.\d+)?\s*(?:L|mL)'),
    (('噪音值','噪声','噪声（声功率级）'), r'\d+(?:\.\d+)?\s*dB\s*[（(]A[）)]'),
    (('充电时间',), r'(?:约)?\d+(?:\.\d+)?\s*(?:小时|分钟|min|h)'),
    (('额定水压',), r'\d+(?:\.\d+)?(?:\s*[-~～]\s*\d+(?:\.\d+)?)?\s*MPa'),
):
    for _key in _keys: RULES[_key] = _shape
RULES.update({
    '额定容量': r'\d+(?:\.\d+)?\s*(?:kg|L)',
    '洗涤筒额定容积': r'\d+(?:\.\d+)?\s*L',
    '烘干容量': r'\d+(?:\.\d+)?\s*kg',
    '烘干功率': r'\d+(?:\.\d+)?\s*W',
    '产品毛重': r'\d+(?:\.\d+)?\s*kg',
    '包装尺寸': RULES['产品尺寸'],
    '额定电压/额定频率': r'\d+\s*V[~～]?/\d+\s*Hz',
    '最大电流': r'\d+(?:\.\d+)?\s*A',
    '工作水压': r'\d+(?:\.\d+)?MPa-\d+(?:\.\d+)?MPa',
    '洗涤噪音（声功率级）': RULES['噪音值'],
    '脱水噪音（声功率级）': RULES['噪音值'],
})
LABELS = sorted(RULES, key=len, reverse=True)

def _label_pattern(label):
    return r'\s*'.join(map(re.escape, label))

LABEL = re.compile(r'(?<!\S)(' + '|'.join(_label_pattern(k) for k in LABELS) + r')\s*[:：]?\s+')
MODELS = re.compile(r'^\s*(?:' + '|'.join(_label_pattern(k) for k in ('产品型号','整机型号','型号')) + r')\s*[:：]?\s+(.+)$')


def parse_manual(text, model, pdf_url):
    found = {}; rejected = []; sections = 0
    for pn, page in enumerate(text.split('\f'), 1):
        lines = page.splitlines(); active = False; block = []; blocks = []
        for line in lines:
            # Adjacent unrelated page columns may follow the heading.
            if HEADING.fullmatch(re.split(r'\s{3,}', line.strip())[0]):
                if block: blocks.append(block)
                active = True; block = []; sections += 1
                continue
            if active and STOP.match(line):
                blocks.append(block); block = []; active = False
            if active: block.append(line)
        if block: blocks.append(block)
        for block in blocks:
            # Explicit parallel component headers define a safe host-only column.
            boundary = next((m.start() for line in block
                             if re.search(r'主\s*机', line)
                             and (m := re.search(r'全能基座|充电座|集尘座|自清洁基座|基站', line))), None)
            scoped = [line[:boundary] if boundary is not None else line for line in block]
            multi = any((m := MODELS.match(line)) and len(re.split(r'\s{2,}', m[1].strip())) > 1 for line in scoped)
            if multi:
                rejected.append(dict(page=pn, reason='multiple_model_columns')); continue
            # Side-by-side robot/station tables: only the explicitly labelled host column.
            for raw in block:
                line = raw[:boundary] if boundary is not None else raw
                matches = list(LABEL.finditer(line))
                if not matches: continue
                prefix = line[:matches[0].start()].strip()
                if prefix:
                    cells = re.split(r'\s{2,}', prefix)
                    if len(cells) % 2 or any(not re.fullmatch(r'[\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z（）() /-]*', cells[j]) for j in range(0,len(cells),2)):
                        continue
                for i, m in enumerate(matches):
                    key = re.sub(r'\s+', '', m[1]); value = line[m.end(): matches[i+1].start() if i+1<len(matches) else len(line)].strip()
                    # An unknown neighbouring label may delimit a complete cell.
                    # Numeric tails (two model values) never qualify as a label.
                    cells = re.split(r'\s{2,}', value)
                    if len(cells) >= 3 and len(cells) % 2 == 1 and all(
                        re.fullmatch(r'[\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z（）() /-]*', cells[j])
                        for j in range(1, len(cells), 2)):
                        value = cells[0]
                    if not re.fullmatch(RULES[key], value):
                        rejected.append(dict(page=pn, reason='ambiguous_cell', quote=raw, key=key)); continue
                    proof = dict(value=value, source='manual_pdf', source_type='official', model=model, pdf_url=pdf_url, page=pn, quote=raw)
                    found.setdefault(key, []).append(proof)
    result = {}
    for key, candidates in found.items():
        if len({re.sub(r'\s+', '', v['value']) for v in candidates}) == 1:
            result[key] = candidates[0]
        else: rejected.append(dict(key=key, reason='conflicting_values'))
    return dict(params=result, sections=sections, rejected=rejected,
                status='parsed' if result else ('parse_failed' if sections else 'table_not_found'))


def apply_manual_params(rows, manifest=None):
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text()) if DEFAULT.exists() else {'schema': 1, 'items': []}
    if manifest.get('schema') != 1: raise ValueError('Invalid manual schema')
    if not manifest['items']: return deepcopy(rows)
    from .homeappliance_params import DEFAULT as prior, named_capacities
    baseline = {e['id']: e for e in json.loads(prior.read_text())['items']} if prior.exists() else {}
    deferred = {key for key,e in baseline.items() if e.get('deferred_reason')}
    # Existing date evidence fingerprints include params; preserve those identities.
    from .release_l7 import INPUT as date_input
    if date_input.exists():
        deferred |= {e['id'] for e in json.loads(date_input.read_text()).get('entries', [])}
    from .series_release import DEFAULT_INPUT as series_input
    if series_input.exists():
        deferred |= {m['id'] for b in json.loads(series_input.read_text()).get('batches', []) for m in b['members']}
    entries = {}
    for e in manifest['items']:
        if e['id'] in entries or not re.fullmatch(r'[\w.-]+', e['model']): raise ValueError('Invalid manual identity')
        for key, v in e['params'].items():
            host = urlsplit(v['pdf_url']).hostname or ''
            if (v['source'] != 'manual_pdf' or v['model'] != e['model'] or not host.endswith('.mi-img.com')
                or urlsplit(v['pdf_url']).scheme != 'https' or type(v['page']) is not int or v['page'] < 1
                or key not in RULES or not re.fullmatch(RULES[key], v['value'])
                or not v['quote'] or v['value'] not in v['quote'] or not re.search(_label_pattern(key), v['quote']) or not re.fullmatch('[0-9a-f]{64}',v['pdf_sha256'])):
                raise ValueError('Invalid manual evidence')
        entries[e['id']] = e
    result = deepcopy(rows)
    for row in result:
        e = entries.get(row['id'])
        if not e or row['id'] in deferred or row.get('is_container') or row.get('name') != e['expected_name']: continue
        model = row.get('miio_model') or row.get('mihome_model')
        if model and model != e['model']: continue
        # Missing device identity requires the frozen, audited exact name/ID bridge.
        if not model:
            audited = baseline.get(row['id'], {})
            if audited.get('expected_name') != row['name'] or audited.get('model') != e['model']: continue
        if row.get('category') == '冰箱' and len(named_capacities(row['name'])) > 1: continue
        params = row.setdefault('params', {}); sources = row.setdefault('params_sources', {})
        added = False
        for key, v in e['params'].items():
            if key not in params:
                added = True
                params[key] = v['value']; sources[key] = {k:deepcopy(x) for k,x in v.items() if k != 'value'}
        if params: row.pop('params_missing', None)
        if sources and added:
            kinds = {v.get('source_type', 'unknown') for v in sources.values()}
            row['params_source_type'] = next(iter(kinds)) if len(kinds) == 1 else 'mixed'
        if not sources: row.pop('params_sources', None)
    return result
