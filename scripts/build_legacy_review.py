"""Build the reviewed legacy inventory from the frozen online export; offline only."""
import json,re,hashlib
from pathlib import Path
from collections import Counter
import argparse
ROOT=Path(__file__).resolve().parents[1]

from goodsdex.legacy_catalog import category_of as category

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--before',type=Path,required=True);a=ap.parse_args()
    rows=json.loads(a.before.read_text())
    patches={r['id']:r for r in json.loads((ROOT/'data/supplements/verified-backfill-20261030.json').read_text()) if r.get('field')=='name'}
    entries=[]
    for r in rows:
        p=patches.get(r['id']); archived=p['captured_at'] if p else None
        captured=r.get('fetched_at')
        if not captured and r.get('captured_at','').startswith('2026-'):
            captured=r['captured_at']
        entries.append(dict(id=r['id'],reviewed_name=r['name'],category=category(r['name']),
          category_basis='reviewed_product_noun',archived_at=archived,archived_source_url=p['source_url'] if p else None,
          captured_at=captured,captured_at_basis='source_record.fetched_at' if r.get('fetched_at') else 'source_record.captured_at' if captured else 'unknown'))
    out=ROOT/'data/official/mi-legacy-categories.json'
    out.write_text(json.dumps(dict(schema=1,scope_count=223,baseline_sha256=hashlib.sha256(a.before.read_bytes()).hexdigest(),items=entries),ensure_ascii=False,indent=2)+'\n')
    print(Counter(e['category'] for e in entries));print('manual',[(e['id'],e['reviewed_name']) for e in entries if not e['category']])
if __name__=='__main__':main()
