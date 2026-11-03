"""Import only complete, quoted model outputs and create a pending random review.

This command never marks a sample correct. Review the printed source quotations
and fill correct/correct_date/verification_quote/checked_at before publishing.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.release_dates import digest, validate


def assemble(bundle, results, evidence):
    existing = {c['family'] for c in bundle['candidates']}
    accepted, rejected = [], []
    for path in sorted(results.glob('batch-*.json')):
        batch = json.loads(path.read_text())
        inputs = json.loads((results/path.name.replace('batch-', 'input-')).read_text())
        families = {f['family']: f for f in inputs['families']}
        text = batch['response']['choices'][0]['message'].get('content') or ''
        text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip())
        try:
            candidates = json.loads(text)['candidates']
        except (json.JSONDecodeError, KeyError, TypeError):
            rejected.append(dict(batch=path.name, reason='no_complete_json_output'))
            continue
        for value in candidates:
            family = value.get('family')
            try:
                if family in existing:
                    rejected.append(dict(family=family, reason='true_source_or_prior_candidate_has_priority'))
                    continue
                if family not in families:
                    raise ValueError('unknown model family')
                ref = value.get('document', '')
                if not re.fullmatch('[a-f0-9]{16}', ref):
                    raise ValueError('unknown source capture')
                source_path = evidence/(ref+'.json')
                source = json.loads(source_path.read_text())
                quote = value.get('quote', '')
                if len(quote) < 15 or quote not in source.get('text', ''):
                    raise ValueError('model quotation not verbatim in captured source')
                header = re.search(r'20\d{2} 年 \d+ 月 \d+ 日', source['text'])
                if not header:
                    raise ValueError('no publication-year anchor')
                release = dict(date=value['date'], granularity='month', source='llm',
                    confidence=value['confidence'], event='availability', market='CN',
                    model=batch['model'], prompt_version='release-month-v1',
                    reasoning=value.get('reason', ''), evidence=dict(
                        url=source['url'], quote=header.group()+' | '+quote,
                        locator='Newsroom publication header + verbatim availability sentence',
                        source_type='official', sha256=source['sha256'],
                        captured_at=datetime.fromtimestamp(source_path.stat().st_mtime, timezone.utc).isoformat()))
                candidate = dict(family=family, ids=families[family]['ids'],
                                 method='llm_source_extraction_and_family_matching', release=release)
                validate(candidate)
                accepted.append(candidate)
                existing.add(family)
            except (ValueError, KeyError, OSError) as error:
                rejected.append(dict(family=family, batch=path.name, reason=str(error), output=value))
    return accepted, rejected


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, default=Path('data/official/release-dates.json'))
    ap.add_argument('--results', type=Path, required=True)
    ap.add_argument('--evidence', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=20261103)
    args = ap.parse_args()
    bundle = json.loads(args.input.read_text())
    accepted, rejected = assemble(bundle,args.results,args.evidence)
    bundle['candidates'] += accepted
    universe = [c for c in bundle['candidates'] if c['release']['source'] == 'llm']
    by_family = {c['family']: c for c in universe}
    chosen = random.Random(args.seed).sample(sorted(by_family), min(30,len(by_family)))
    bundle['review'] = dict(seed=args.seed, universe_sha256=digest(universe), samples=[dict(
        family=f, candidate_sha256=digest(by_family[f]),
        date=by_family[f]['release']['date'], verification_url=by_family[f]['release']['evidence']['url'],
        verification_quote='', correct=None, correct_date='', checked_at='') for f in chosen])
    args.out.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    (args.results/'rejected.json').write_text(json.dumps(rejected,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(accepted=len(accepted), rejected=len(rejected), sample_size=len(chosen))))


if __name__ == '__main__':
    main()
