"""Read-only whole-catalogue review queue: category median is a triage signal only."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.price_semantics import candidates
if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--goods',type=Path,required=True);ap.add_argument('--excluded',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    raw=a.goods.read_bytes();rows=json.loads(raw)
    by_id={r['id']:r for r in rows}
    archive=[]
    if a.excluded:
        archive=json.loads(a.excluded.read_bytes())['items']
    extra=[r for r in archive if r['id'] not in by_id]
    hit=candidates(rows);archived=candidates(extra)
    result=dict(published_count=len(rows),published_unique_count=len(by_id),goods_sha256=hashlib.sha256(raw).hexdigest(),
        rule='name contains 定金/订金/补差/差价/加购/仅升级 OR positive price < 10% of primary-category median; no minimum cohort size; exclude null/zero/negative from median; independent published/archive cohorts',
        candidate_count=len(hit),candidates=hit,excluded_archive_count=len(extra),excluded_candidate_count=len(archived),excluded_candidates=archived)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('candidates','excluded_candidates')},ensure_ascii=False))
