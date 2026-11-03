"""Replay the frozen 39 checks; no new model calls or edits to source assertions."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.release_crosschecks import delta_days, reconcile, verdict, traceable
from goodsdex.release_dates import apply_release_dates, digest


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--catalog', type=Path)
    args = ap.parse_args()
    out = Path(__file__).parent
    baseline = json.loads((ROOT/'docs/release-crosschecks-20261103/baseline-dates.json').read_text())
    checks = json.loads((ROOT/'data/llm/release-crosschecks.json').read_text())['checks']
    captures = {}
    for folder in ('release-dates-20261103', 'release-dates-round2-20261103'):
        for path in (ROOT/'docs'/folder/'evidence').glob('*.json'):
            v = json.loads(path.read_text())
            if isinstance(v, dict) and v.get('sha256') and v.get('text'):
                captures[v['sha256']] = (str(path.relative_to(ROOT)), v)
    rows, conflicts = [], []
    for item in baseline:
        r = item['release']
        if r['source'] != 'third_party':
            continue
        c = checks[item['family']]
        assert c['original_sha256'] == digest(r)
        result = reconcile(r, [c])
        raw = verdict(delta_days(r['date'], c['date'])) if c['date'] else 'unverified'
        detail = dict(id=item['ids'][0], model=item['name'], original_date=r['date'],
            original_evidence=r['evidence'], llm_date=c['date'], llm_evidence=c.get('evidence'),
            llm_has_traceable_evidence=traceable(c), llm_reason=c.get('reason'),
            response_sha256=c['response_sha256'], response_artifact=c['artifact'],
            raw_verdict=raw, effective_verdict=result['crosscheck_status'],
            final_date=result['date'], display_allowed=result.get('display_allowed', True),
            internal_only=result.get('internal_only', False),
            manual_review_required=result['manual_review_required'])
        rows.append(detail)
        if raw == 'conflict':
            path, capture = captures[r['evidence']['sha256']]
            text = capture['text']
            # Retain the full captured source, including timestamp and sale sentence.
            detail = deepcopy(detail)
            detail.update(source_capture=path, source_text=text,
                          decision='unsupported_model_dissent_ignored; original retained internal_only')
            assert detail['final_date'] == r['date'] and not detail['manual_review_required']
            conflicts.append(detail)
    assert len(rows) == 39 and len(conflicts) == 5
    summary = dict(total=39, replay='frozen independent responses; deterministic policy rerun, no new LLM calls',
        previous=dict(corroborated=14, disagreement=0, conflict=5, unverified=20, nulled=5),
        raw_comparisons=dict(Counter(r['raw_verdict'] for r in rows)),
        effective_decisions=dict(Counter(r['effective_verdict'] for r in rows)),
        nulled=sum(r['final_date'] is None for r in rows), restored_conflicts=len(conflicts))
    for name in ('raw_comparisons', 'effective_decisions'):
        for key in ('corroborated', 'disagreement', 'conflict', 'unverified'):
            summary[name].setdefault(key, 0)
    write(out/'comparison-39.json', rows)
    write(out/'conflicts-5.json', conflicts)
    if args.catalog:
        before = json.loads(args.catalog.read_text())
        after = apply_release_dates(before)
        assert apply_release_dates(after) == after, 'Full catalogue replay must be idempotent'
        assert [{k:v for k,v in r.items() if k != 'release'} for r in before] == [{k:v for k,v in r.items() if k != 'release'} for r in after]
        by_id = {r['id']:r for r in after}
        for detail in rows:
            actual = by_id[detail['id']]['release']
            assert actual['date'] == detail['final_date']
            assert actual['evidence'] == detail['original_evidence']
            assert actual['crosscheck_status'] == detail['effective_verdict']
        target = args.catalog.with_name('goods-after.json')
        write(target, after)
        summary['catalog'] = dict(count=len(after), non_release_unchanged=True, idempotent=True,
            changed=sum(a.get('release') != b.get('release') for a,b in zip(before,after)),
            input_sha256=hashlib.sha256(args.catalog.read_bytes()).hexdigest(),
            output=str(target))
    write(out/'summary.json', summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
