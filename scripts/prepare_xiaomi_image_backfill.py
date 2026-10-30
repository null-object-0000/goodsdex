"""Resolve only existing local image evidence, without any source requests."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]

def resolve(candidate, history):
    if candidate['source'] != 'live_official_page':
        # A timestamp alone does not establish the exact archived request URL.
        return None, 'archive_request_url_not_preserved'
    specs = history.get('official_specs_url')
    if not specs:
        return None, 'missing_official_page_mapping'
    checked = candidate.get('checked_at')
    if not checked:
        return None, 'missing_captured_at'
    datetime.fromisoformat(checked)
    parts = urlsplit(specs)
    if parts.hostname != 'www.mi.com' or not parts.path.rstrip('/').endswith('/specs'):
        return None, 'unresolved_official_page_mapping'
    # The reviewed report describes deriving the official landing page from this
    # exact per-product specs mapping. Do not claim we retained a page capture.
    page = urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip('/')[:-5], '', ''))
    return dict(candidate, source_url=page, captured_at=checked,
        captured_at_kind='image_get_observed_at',
        provenance_basis=dict(history_file=f"data/archive-history/{candidate['pid']}.json",
            official_specs_url=specs, report='data/research/xiaomi-images-20261030/report.md',
            source_url_derivation='official product landing page derived from verified specs URL; original page/CSS capture URL not retained',
            timestamp_derivation='existing candidate.checked_at; image GET observation, not page capture or archive time')) , None

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    candidates=json.loads((ROOT/'data/research/xiaomi-images-20261030/candidates.json').read_text())
    rows=json.loads(a.baseline.read_text());ready=[];skipped=[]
    for c in candidates:
        key='CN:mi_cn:product:'+c['pid'];matches=[r for r in rows if r['id']==key]
        if not matches: skipped.append(dict(candidate=c,reason='target_absent'));continue
        if any(r.get('image') for r in matches): skipped.append(dict(candidate=c,reason='existing_image'));continue
        history=json.loads((ROOT/f"data/archive-history/{c['pid']}.json").read_text())
        item,reason=resolve(c,history)
        if reason:skipped.append(dict(candidate=c,reason=reason));continue
        item['id']=key;item['image_scope']='series' if c.get('shared_with') else 'model'
        ext={'image/jpeg':'jpg','image/png':'png'}.get(c['content_type'])
        if not ext:skipped.append(dict(candidate=c,reason='unsupported_format'));continue
        item['key']='goods/'+hashlib.sha1(c['image_url'].encode()).hexdigest()+'.'+ext
        ready.append(item)
    a.out.mkdir(parents=True,exist_ok=True)
    for name,obj in [('resolved.json',ready),('skipped-provenance.json',skipped)]:
        (a.out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(dict(candidates=len(candidates),resolved=len(ready),skipped=len(skipped)))
if __name__=='__main__':main()
