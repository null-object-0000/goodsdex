"""Freeze existing Wayback/LLM artifacts for offline replay; never recollect."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path


def freeze(wayback, llm, output):
    inputs = {}
    def read(path):
        raw = path.read_bytes()
        inputs[str(path)] = hashlib.sha256(raw).hexdigest()
        return raw
    manifest = json.loads(read(wayback / 'data/full/manifest.json'))
    results = [json.loads(line) for line in read(wayback / 'data/full/results_final.jsonl').splitlines() if line]
    accuracy = json.loads(read(llm / 'accuracy.json'))
    outcomes = json.loads(read(llm / 'outcomes.json'))
    candidates = [r for r in outcomes if r['result'] == 'date']
    responses = {}
    for row in candidates:
        path = llm / row['response_file']
        raw = read(path)
        responses[row['family']] = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(),
                                       captured_at=json.loads(raw)['captured_at'])
    bundle = dict(schema=1, captured_at=datetime.now(timezone.utc).isoformat(),
                  captured_at_basis='snapshot_import_time; source Wayback rows have no per-query timestamp',
                  source_sha256=inputs, wayback_manifest=manifest, wayback_results=results,
                  llm_accuracy=accuracy, llm_candidates=candidates, llm_responses=responses)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(gzip.compress((json.dumps(bundle, ensure_ascii=False, sort_keys=True) + '\n').encode(), mtime=0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wayback', type=Path, required=True)
    ap.add_argument('--llm', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=Path('data/enrichment/date-inputs.json.gz'))
    a = ap.parse_args()
    freeze(a.wayback, a.llm, a.output)
