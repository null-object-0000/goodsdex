"""Evidence dates for upgrade decisions: 14-day agreement, 45-day rejection.

Run last in every publication. Never infer membership from a shared brand/series.
"""
from copy import deepcopy
from datetime import date
import hashlib
import math
from urllib.parse import urlparse
from .release_crosschecks import delta_days

POLICY = 'upgrade-release-14-45-v1'
SOURCES = ('official', 'third_party', 'llm_crossed', 'series_inherit')


def captured(r):
    e = r.get('evidence') or {}
    u = urlparse(e.get('url') or '')
    return bool(u.scheme in ('http', 'https') and u.hostname and
                all(e.get(k) for k in ('quote', 'sha256', 'captured_at')) and
                e.get('capture_type') != 'model_output')


def deviation(r):
    deltas = [r[k] for k in ('release_delta_days', 'crosscheck_delta_days')
              if isinstance(r.get(k), (float, int))]
    for a in r.get('assertions', []):
        if (a.get('date') and a.get('event') == r.get('event') and
            a.get('market', r.get('market')) == r.get('market') and captured(a)):
            deltas.append(delta_days(r['date'], a['date']))
    for a in r.get('checks', []):
        if a.get('hard_conflict') is True and isinstance(a.get('delta_days'), (int,float)):
            deltas.append(a['delta_days'])
    return max(deltas, default=None)


def normalize(r):
    from .release_coverage import precision
    r = deepcopy(r)
    if not precision(r) or not captured(r):
        return None
    source = r.get('source')
    if source == 'official_hidden': source = 'official'
    if r.get('level') == 'series':
        source = 'series_inherit'
        r.update(date=r['date'][:7], granularity='month')
    if source == 'llm': return None
    if source not in SOURCES: return None
    delta = deviation(r)
    if delta is not None and (not math.isfinite(delta) or delta < 0 or delta > 45): return None
    if source == 'llm_crossed':
        proof = r.get('llm_crosscheck') or {}
        if (proof.get('independent') is not True or not proof.get('model') or
            not proof.get('date') or not proof.get('identity_verified') or
            not proof.get('event_verified') or
            delta_days(r['date'], proof['date']) > 14): return None
        delta = delta_days(r['date'], proof['date'])
    medium = delta is not None and delta > 14
    r.update(policy=POLICY, release_source=source, release_precision=r['granularity'],
             release_tolerance_days=14, release_delta_days=delta,
             usage='reference' if medium or source=='series_inherit' else 'fact',
             confidence='medium' if medium else r.get('confidence','high'),
             display_allowed=True, internal_only=False, manual_review_required=False)
    y,m = map(int,r['date'][:7].split('-'))
    r['display'] = ('约 ' + str(round(max(0,(date.today().year-y)*12+date.today().month-m)/6)/2) + ' 年前发布' if medium else
                    f'{y} 年 {m} 月前后' + ('系列发布' if source=='series_inherit' else '发布'))
    # Medium data supplies age only; it cannot establish a new generation.
    r['decision_usage'] = ['age'] if medium else ['age', 'generation']
    return r


def apply(rows):
    out = deepcopy(rows)
    for row in out:
        candidates=[]; conflicts=deepcopy(row.get('release_conflicts', []))
        for field in ('release', 'release_inherited', 'release_series', 'release_crossed'):
            raw = row.get(field) or {}
            if not raw.get('date'): continue
            r = normalize(raw)
            if r:
                candidates.append((field,r))
            else:
                delta = deviation(raw)
                if isinstance(delta,(int,float)) and delta>45:
                    entry=dict(field=field,assertion=deepcopy(raw),release_delta_days=delta,reason='delta_over_45_days')
                    if entry not in conflicts: conflicts.append(entry)
                    row[field]=dict(date=None,source=raw.get('source'),usage='disabled',manual_review_required=True)
        if conflicts:
            row['release_conflicts']=conflicts
            prior=row.get('release') or {}
            row['release']=dict(date=None, source=prior.get('source','third_party'), usage='disabled', manual_review_required=True)
            candidates=[]
            row.pop('release_effective',None)
            for key in ('release_inherited','release_series','release_crossed'):
                row.pop(key,None)
        if not candidates:
            for k in ('release_source','release_precision','release_evidence','release_quote','release_tolerance_days','release_delta_days','release_decision','release_effective'):
                row.pop(k,None)
            continue
        # Unknown deviation ranks after verified agreement. Then prefer precision.
        candidates.sort(key=lambda pair:(pair[1].get('release_delta_days') if pair[1].get('release_delta_days') is not None else 0 if pair[1]['release_source']=='official' else 46,
                                        pair[1]['granularity']!='day', SOURCES.index(pair[1]['release_source'])))
        field,r=candidates[0]
        alternatives = r.get('alternates', [])
        for _,alt in candidates[1:]:
            alt=deepcopy(alt);alt.pop('alternates',None)
            if alt not in alternatives: alternatives.append(alt)
        if alternatives:r['alternates']=alternatives
        row['release_effective']=deepcopy(r)
        e=r['evidence']
        row.update(release_source=r['release_source'],release_precision=r['granularity'],
                   release_evidence=e['url'],release_quote=e['quote'],release_tolerance_days=14,
                   release_delta_days=r['release_delta_days'])
        row['release_decision']=dict(date=r['date'][:7],precision='month',source=r['release_source'],
                                    display=r['display'],usage=r['decision_usage'],level=r.get('level','product'))
    return out


def expand(rows):
    """Only explicit, exact generation membership. All categories are eligible."""
    import re
    from pathlib import Path
    import json
    from .series_release import identity, is_accessory
    from .release_dates import digest
    root=Path(__file__).resolve().parents[2]
    out=deepcopy(rows)
    batches=json.loads((root/'data/official/series-releases.json').read_text())['batches']
    members={m['id']:(b,m) for b in batches for m in b['members']}
    hp=json.loads((root/'data/official/priority-series-release-evidence.json').read_text())
    # This captured announcement explicitly enumerates each of these G10 models.
    platforms=('EliteBook 630','EliteBook 640','EliteBook 650','EliteBook 645',
               'EliteBook 830','EliteBook 840','EliteBook 860','Elite x360 830',
               'ProBook 440','ProBook 450','ProBook 445','ProBook 455')
    hp_text = None
    hp_path = root / hp.get('evidence', {}).get('capture_file', '__missing__')
    if hp_path.is_file():
        from .release_structured import Page
        raw=hp_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != hp['evidence']['sha256']:
            raise ValueError('HP series capture hash mismatch')
        hp_text = Page(raw.decode('utf-8')).text
        if 'March 29, 2023' not in hp_text:
            raise ValueError('HP announcement dateline changed')
    crossed_path=root/'data/llm/release-crossed-verified.json'
    crossed=json.loads(crossed_path.read_text()).get('candidates',[]) if crossed_path.exists() else []
    by_id={key:c['release'] for c in crossed for key in c['ids']}
    expected_names={key:value for c in crossed for key,value in c.get('names',{}).items()}
    for row in out:
        if row['id'] in expected_names and expected_names[row['id']]!=row['name']:
            raise ValueError('Crossed release model identity changed')
    for candidate in crossed:
        r=candidate['release'];e=r.get('evidence') or {}
        path=(root/e.get('capture_file','__missing__')).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Crossed release requires a captured independent document')
        from .release_structured import Page, norm
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=e.get('sha256') or norm(e.get('quote','')) not in norm(Page(raw.decode('utf-8')).text):
            raise ValueError('Crossed independent source bytes/excerpt changed')
    for row in out:
        if row['id'] in by_id: row['release_crossed']=deepcopy(by_id[row['id']])
    donors = {}
    for row in out:
        r = normalize(row.get('release') or row.get('release_crossed') or {})
        if row.get('brand') == '大疆' and r and row.get('family_id'):
            items = (row.get('params') or {}).get('包装清单') or []
            if items and items[0].get('name'):
                donors.setdefault((row['family_id'],items[0]['name']), []).append((row,r))
    for row in out:
        if row['id'] in by_id:
            row['release_crossed']=deepcopy(by_id[row['id']])
        if is_accessory(row) or row.get('kind')=='service':continue
        b,m=members.get(row['id'],(None,None))
        if b and digest(identity(row)) in [m['identity_sha256'],*m.get('identity_sha256_alternates',[])]:
            r=normalize(b['series_release'])
            if r:
                r.update(series=b['series'],generation=b['generation'],batch_id=b['id'],
                         membership_evidence=deepcopy(m),source='series_inherit',level='series')
                row['release_inherited']=r
        if row.get('brand') == '大疆' and not normalize(row.get('release') or {}):
            items = (row.get('params') or {}).get('包装清单') or []
            main = items[0].get('name') if items else None
            matches = donors.get((row.get('family_id'),main), [])
            # Exact principal device in both packaging lists and same official family.
            # Different camera resolutions/generations cannot share this key.
            matches = [(d,r) for d,r in matches if main and re.search(r'\d',main)
                       and re.sub(r'\s','',row['name']).casefold().startswith(re.sub(r'\s','',main).casefold())]
            months = {r['date'][:7] for _,r in matches}
            if len(months) == 1:
                donor,r = matches[0]; r=deepcopy(r)
                r.update(date=r['date'][:7],granularity='month',source='series_inherit',
                         release_source='series_inherit',level='series',series=main,generation=main,
                         scope='Principal device generation; not this bundle first-sale date',
                         membership_evidence=dict(family_id=row['family_id'],principal_device=main,
                            field='params.包装清单[0].name',donor_id=donor['id'],url=row.get('source_url')))
                row['release_inherited']=r
        if row.get('brand')!='惠普':continue
        name=(row.get('params') or {}).get('source_specs',{}).get('productSeriesName','')
        model=next((p for p in platforms if re.search(r'\bHP '+re.escape(p)+r'\b.*\bG10\b',name,re.I)),None)
        if not model or not hp.get('evidence'):continue
        # Retain the original capture, quote only a sentence present in its bytes.
        e=deepcopy(hp['evidence'])
        if not hp_text:continue
        text=hp_text
        canonical=model+' G10'
        # The prose may contain "HP" before each model in the list.
        if canonical not in text:continue
        i=text.index(canonical); start=text.rfind('.',0,i)+1; end=text.find('.',i)
        e['quote']=text[start:end+1].strip()
        e['locator']='Press release dateline and explicit G10 platform statement'
        row['release_inherited']=dict(date='2023-03',granularity='month',source='series_inherit',
              release_source='series_inherit',level='series',event='announcement',market='GLOBAL',
              confidence='high',series='HP '+model,generation='G10',evidence=e,
              scope='Global generation announcement, not CN SKU first sale',
              membership_evidence=dict(field='params.source_specs.productSeriesName',value=name,
                                       url=row.get('source_url')))
    return out
