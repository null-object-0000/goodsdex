"""Replay the reviewed pilot offline; never publish or expand memberships."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.series_release import apply_series_releases, coverage, effective_release, is_accessory, DEFAULT_INPUT


def run(snapshot, out):
    raw = snapshot.read_bytes()
    if snapshot.suffix == '.gz':
        raw = gzip.decompress(raw)
    rows = json.loads(raw)
    enriched = apply_series_releases(rows)
    mi = [r for r in enriched if r['id'].startswith('CN:mi_cn:')]
    for before, r in zip(rows, enriched, strict=True):
        assert {k:v for k,v in r.items() if k not in ('series_release', 'release_series')} == {k:v for k,v in before.items() if k not in ('series_release', 'release_series')}
        assert not is_accessory(r) or 'release_series' not in r
    assert apply_series_releases(enriched) == enriched
    batches = []
    for batch in json.loads(DEFAULT_INPUT.read_text())['batches']:
        matched = [r for r in mi if r.get('release_series', {}).get('batch_id') == batch['id']]
        batches.append(dict(batch_id=batch['id'],series=batch['series'],generation=batch['generation'],
            date=batch['series_release']['date'],granularity=batch['series_release']['granularity'],
            source=batch['series_release']['source'],evidence=batch['series_release']['evidence'],
            members=len(matched),inherited_without_product=sum(not (r.get('release') or {}).get('date') for r in matched),
            product_retained=sum(bool((r.get('release') or {}).get('date')) for r in matched)))
    inherited = sorted([r for r in mi if r.get('release_series') and not (r.get('release') or {}).get('date')],key=lambda r:r['id'])
    # Deterministic 10 of 11, including every batch with newly inherited rows.
    samples = [dict(id=r['id'],name=r['name'],batch_id=r['release_series']['batch_id'],
        date=r['release_series']['date'],level='series',url=r['release_series']['evidence']['url'],
        identity_reason=next(m['identity_reason'] for b in json.loads(DEFAULT_INPUT.read_text())['batches'] for m in b['members'] if m['id']==r['id'])) for r in inherited[:10]]
    result = dict(snapshot_sha256=hashlib.sha256(raw).hexdigest(),requested_denominator=4008,
        denominator_matches_request=len(mi)==4008,coverage=coverage(mi),
        active_internal=Counter((effective_release(r) or {}).get('level','missing') for r in mi),
        disabled_product_assertions=sum(bool((r.get('release') or {}).get('date')) and r['release'].get('usage')=='disabled' for r in mi),
        batches=batches,samples=samples,accessory_kind_count=sum(r.get('kind')=='accessory' for r in mi),
        accessory_ids=[r['id'] for r in mi if is_accessory(r)],
        services=sum(r.get('kind')=='service' for r in mi),
        full_rollout=False,projection='Only audited pilot gain is known; no statistical extrapolation from selected series.',
        invariants=dict(product_release_unchanged=True,other_fields_unchanged=True,idempotent=True,accessory_series_dates=0))
    out.mkdir(parents=True,exist_ok=True)
    (out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (out/'pilot-rows.json').write_text(json.dumps([r for r in mi if r.get('release_series')],ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['coverage'],ensure_ascii=False))
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,default=Path('docs/series-release-pilot-20261103/baseline-goods.json.gz'))
    p.add_argument('--out',type=Path,default=Path('docs/series-release-pilot-20261103'))
    a=p.parse_args();run(a.snapshot,a.out)
