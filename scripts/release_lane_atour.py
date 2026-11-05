#!/usr/bin/env python3
"""L2: read anonymous official SPU details; never equate createTime with launch.

run(rows, output_dir, refresh=True) -> {lane, candidates, outcomes, summary}.
Set ATOUR_PLAYWRIGHT_MODULE to the installed playwright(-core) module path.
All absent dates are not_collected unless explicit evidence proves absence.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE = ROOT / 'docs/release-coverage/l2-atour/live-capture.json'


def run(rows, output_dir=None, refresh=True, capture_path=None, *, live=None):
    if live is not None:
        refresh = live
    out = Path(output_dir or ROOT / 'docs/release-coverage/l2-atour')
    out.mkdir(parents=True, exist_ok=True)
    capture = Path(capture_path) if capture_path else out / 'live-capture.json'
    capture_error = None
    if refresh:
        try:
            subprocess.run(['node', str(ROOT/'scripts/release_lane_atour_capture.cjs'), str(capture)],
                           check=True, capture_output=True, text=True, timeout=240)
        except (subprocess.SubprocessError, OSError) as exc:
            capture_error = str(exc)
    # A failed refresh never masquerades as a fresh successful capture.
    data = json.loads(capture.read_text()) if capture.exists() and not capture_error else {}
    details = {str(d['spuId']): d for d in data.get('details', [])}
    outcomes=[]
    for row in rows:
        if 'atour' not in row.get('id','').lower() and '亚朵' not in str(row.get('brand','')):
            continue
        source_url=row.get('source_url') or ''
        import re
        m=re.search(r'(?:[?&]id=|spu:)(\d+)', source_url+' '+row.get('id',''))
        spu = str(row.get('spu_id') or row.get('spuId') or (m.group(1) if m else ''))
        item=details.get(spu)
        detail=item.get('detail',{}) if item else {}
        reason=('transport_error' if capture_error else 'model_mismatch' if not item else
                'transport_error' if item.get('error') else
                'model_mismatch' if str(detail.get('id')) != spu else 'no_release_field')
        raw=json.dumps(detail,ensure_ascii=False,sort_keys=True)
        outcomes.append({'id':row['id'],'spu_id':spu,'name':row.get('name'),
            'reason':reason,'missing_reason':'not_collected','source_url':source_url,'url':source_url,
            'captured_at':data.get('captured_at'),'sha256':hashlib.sha256(raw.encode()).hexdigest() if item else None,
            'fields_observed':sorted(detail),
            'rejected_fields':{'createTime':detail.get('createTime'),'reason':'商城SPU记录创建时间无发布/上市语义，不作为发布日期'},
            'detail':item.get('error') if item and item.get('error') else capture_error or '未取得月级发布证据；仅该详情响应未给发布字段，不证明官方没有信息'})
    result={'schema':1,'lane':'L2','captured_at':data.get('captured_at'),'candidates':[],
            'outcomes':outcomes,'observations':outcomes,'summary':{'total':len(outcomes),'matched':0,'reasons':dict(Counter(o['reason'] for o in outcomes))},
            'capture_error':capture_error}
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--goods',required=True)
    parser.add_argument('--output-dir')
    parser.add_argument('--capture')
    parser.add_argument('--no-refresh',action='store_true')
    args=parser.parse_args()
    payload=json.loads(Path(args.goods).read_text())
    rows=payload if isinstance(payload,list) else payload.get('goods',payload.get('items',[]))
    result=run(rows,args.output_dir,not args.no_refresh,args.capture)
    target=ROOT/'data/official/atour-release-evidence.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['summary'],ensure_ascii=False))

if __name__=='__main__': main()
