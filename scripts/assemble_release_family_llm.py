"""Freeze raw proposals, usage and per-brand reproducible review queues."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'src'), str(Path(__file__).resolve().parent)]
from goodsdex.release_dates import brand_sample, digest, validate
from release_family_llm import BRANDS, SEED, write


def assemble(root):
    fs = json.loads((root / 'families.json').read_text())
    candidates, outcomes, usage = [], [], Counter()
    brand_usage = {b: Counter() for b in BRANDS}
    for f in fs:
        k = hashlib.sha256(f['family'].encode()).hexdigest()[:24]
        p = root / 'responses' / (k + '.json')
        sent = (root / 'sent' / (k + '.json')).exists()
        status = dict(family=f['family'], brand=f['brand'], requested=sent, result='pending')
        if sent:
            usage['calls'] += 1
            brand_usage[f['brand']]['calls'] += 1
        if not p.exists():
            if sent and (root / 'run-closed.json').exists():
                status['result'] = 'interrupted_usage_unknown'
            outcomes.append(status)
            continue
        o = json.loads(p.read_text())
        for key, value in o.get('response', {}).get('usage', {}).items():
            if isinstance(value, int):
                usage[key] += value
                brand_usage[f['brand']][key] += value
        try:
            choice = o['response']['choices'][0]
            raw = choice['message']['content']
            raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw.strip())
            result = json.loads(raw)
            status['proposal'] = result
            if not result.get('date'):
                status['result'] = 'abstention'
            else:
                evidence = result.get('evidence') or {}
                c = dict(family=f['family'], brand=f['brand'], category=f['category'],
                    ids=[v['id'] for v in f['variants']], method='model_family_generation_estimate',
                    release=dict(date=result['date'], source='llm', confidence='low',
                        granularity='month', event='announcement', market=result.get('market', 'unknown'),
                        model=o['response'].get('model', 'flowlet-flash'), scope='model_family_generation',
                        evidence=dict(url=evidence.get('url') or '', quote=evidence.get('quote') or '',
                            reason=evidence.get('reason') or '', capture_type='model_output',
                            locator='choices[0].message.content.evidence', source_type='third_party',
                            sha256=hashlib.sha256(p.read_bytes()).hexdigest(), captured_at=o['captured_at'],
                            artifact=str(p.relative_to(root)),
                            note='Hash and capture time identify the model response, not a fetched source page. Source citation is unverified except where sampled.')))
                validate(c)
                candidates.append(c)
                status['result'] = 'candidate'
        except Exception as exc:
            status.update(result='invalid_or_failed', error=str(exc), response_error=o.get('error'))
        outcomes.append(status)
    write(root / 'candidates.json', candidates)
    write(root / 'outcomes.json', outcomes)
    write(root / 'usage.json', dict(totals=dict(usage), brands={b: dict(v) for b, v in brand_usage.items()},
        caveat='Sent requests lacking a response have unknown usage; totals cover recorded responses only. No charged retries.'))
    queue = {}
    for b in BRANDS:
        cs = [c for c in candidates if c['brand'] == b]
        chosen = brand_sample([c['family'] for c in cs], SEED)
        queue[b] = dict(seed=SEED, universe_sha256=digest(cs), samples=[dict(
            family=f, candidate_sha256=digest(next(c for c in cs if c['family'] == f)),
            candidate=next(c for c in cs if c['family'] == f)) for f in chosen])
    write(root / 'review-queue.json', queue)
    print(json.dumps(dict(outcomes=Counter(o['result'] for o in outcomes), brands={b: dict(
        candidates=sum(c['brand'] == b for c in candidates), samples=len(queue[b]['samples'])) for b in BRANDS}), ensure_ascii=False))


if __name__ == '__main__':
    assemble(Path(sys.argv[1]))
