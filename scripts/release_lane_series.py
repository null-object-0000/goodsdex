#!/usr/bin/env python3
"""L4: exact-evidence platform inheritance, always month, never a SKU launch."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import requests

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE=ROOT/'data/official/priority-series-release-evidence.json'
URL='https://www.hp.com/us-en/newsroom/press-releases/2023/hp-unleashes-future-ready-portfolio.html'


def priority(row):
    from goodsdex.release_coverage import priority_group
    return priority_group(row) is not None


def run(goods, output=ROOT/'docs/release-coverage/l4-series', *, live=True):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    captured_at=datetime.now(timezone.utc).isoformat()
    bundle=json.loads(DEFAULT_EVIDENCE.read_text()) if DEFAULT_EVIDENCE.exists() else {'evidence':None}
    errors=[]
    if live:
        try:
            response=requests.get(URL,timeout=30);response.raise_for_status()
            from bs4 import BeautifulSoup
            text=BeautifulSoup(response.text,'html.parser').get_text(' ',strip=True)
            required=['March 29, 2023','The HP ProBook 440 G10 and HP ProBook 450 G10 are available at hp.com starting at $929.',
                      'The HP ProBook 445 G10 and HP ProBook 455 G10 are available at hp.com starting at $799.']
            if not all(s in text for s in required):
                raise ValueError('Official publication date/platform statement changed; review needed')
            raw=output/'hp-probook-g10-newsroom.html';raw.write_bytes(response.content)
            bundle={'captured_at':captured_at,'evidence':{'url':URL,'sha256':hashlib.sha256(response.content).hexdigest(),
                'captured_at':captured_at,'quote':' '.join(required),
                'locator':'Press release heading date and Pricing and Availability paragraphs',
                'source_type':'official','capture_file':str(raw.relative_to(ROOT)) if raw.is_relative_to(ROOT) else str(raw)},
                'date':'2023-03','event':'announcement','market':'GLOBAL',
                'platforms':['440','450','445','455'],
                'scope':'Global ProBook G10 platform announcement. Does not establish China configuration first-sale date.'}
        except (requests.RequestException,ValueError) as exc:
            errors.append({'reason':'source_fetch_failed','url':URL,'detail':str(exc)})
    inherited=[]; observations=[]
    for row in goods:
        if not priority(row):continue
        old=row.get('release_series')
        from goodsdex.release_coverage import usable
        if old and usable(old) and (old.get('source') != 'third_party' or old.get('crosscheck_status') == 'corroborated') and re.fullmatch(r'\d{4}-(?:0[1-9]|1[0-2])(?:-\d{2})?',old.get('date','')) and old.get('granularity') in ('day','month') and old.get('evidence',{}).get('url') and old.get('evidence',{}).get('quote'):
            release=deepcopy(old)
            release.update(date=old['date'][:7],granularity='month',source='series_inherit',release_source='series_inherit',
                level='series',inherited=True,scope='Existing reviewed series assertion, exact published member id only; not configuration launch.')
            release['parent_granularity']=old['granularity']
            inherited.append({'ids':[row['id']],'release':release})
            observations.append({'id':row['id'],'reason':'existing_exact_series_member','url':old['evidence']['url']})
            continue
        if row.get('source')!='hp_cn' and not row['id'].startswith('CN:hp_cn:'):continue
        name=row.get('params',{}).get('source_specs',{}).get('productSeriesName','')
        match=re.search(r'\bHP ProBook (440|450|445|455)\b.*\bG10\b',name,re.I)
        if not match or not bundle.get('evidence'):continue
        release={'date':'2023-03','granularity':'month','source':'series_inherit','release_source':'series_inherit',
                 'level':'series','market':'GLOBAL','event':'announcement','confidence':'high','inherited':True,
                 'series':f'HP ProBook {match[1]} G10','generation':'G10',
                 'scope':bundle['scope'],'evidence':deepcopy(bundle['evidence']),
                 'membership_evidence':{'field':'params.source_specs.productSeriesName','value':name,
                     'url':row.get('source_url'),'part_number':row.get('part_number')}}
        inherited.append({'ids':[row['id']],'release':release})
        observations.append({'id':row['id'],'reason':'exact_official_platform_match','url':URL})
    result={'summary':{'eligible':sum(priority(r) for r in goods),'inherited':sum(len(c['ids']) for c in inherited),'errors':len(errors)},'lane':'L4','captured_at':captured_at,'candidates':[],'inherited_candidates':inherited,
            'observations':observations,'errors':errors,'hits':sum(len(c['ids']) for c in inherited),
            'policy':'Only exact official platform or existing reviewed series members; month ceiling; global announcement distinct from CN SKU launch.'}
    result.update({key:deepcopy(bundle[key]) for key in ('evidence','scope','date','event','market','platforms') if key in bundle})
    (output/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--goods',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'docs/release-coverage/l4-series');p.add_argument('--offline',action='store_true')
    a=p.parse_args();r=run(json.loads(a.goods.read_text()),a.output,live=not a.offline)
    print(json.dumps({k:v for k,v in r.items() if k not in ('observations','inherited_candidates')},ensure_ascii=False))
