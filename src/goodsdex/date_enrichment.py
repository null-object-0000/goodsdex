"""Independent, replayable page-existence and model-month assertions.

Date precedence: release (official/third_party product) > release_series >
release_llm. page_first_archived is independent and never joins that ordering:
it means only that the page existed by that date, NEVER a release date.
"""
from collections import Counter
from copy import deepcopy
from datetime import date
import gzip
import json
from pathlib import Path
import re

DEFAULT_INPUT = Path(__file__).resolve().parents[2] / 'data/enrichment/date-inputs.json.gz'


def confidence_for(accuracy):
    if accuracy is None or not 0 <= accuracy <= 1:
        return None
    return 'high' if accuracy >= .97 else 'medium' if accuracy >= .90 else None


def load_assertions(path=DEFAULT_INPUT):
    bundle = json.loads(gzip.decompress(Path(path).read_bytes()))
    if bundle['schema'] != 1:
        raise ValueError('Unknown date enrichment schema')
    jobs = {j['job_id']: j for j in bundle['wayback_manifest']['jobs']}
    pages = {}
    for result in bundle['wayback_results']:
        if result['status'] != 'archived':
            continue  # not_archived = no observed 200; error = query failed, not absence.
        date.fromisoformat(result['first_archived'])
        if not result['first_archived_url'].startswith('https://web.archive.org/web/'):
            raise ValueError('Missing Wayback evidence URL')
        assertion = dict(date=result['first_archived'], evidence_url=result['first_archived_url'],
                         count_200=result['count_200'], captured_at=bundle['captured_at'])
        job = jobs[result['id']]
        for key in job['record_ids']:
            value = (job['brand'], assertion)
            if key in pages and pages[key] != value:
                raise ValueError(f'Conflicting Wayback id: {key}')
            pages[key] = value
    models = {}
    for candidate in bundle['llm_candidates']:
        brand = candidate['brand']
        accuracy = bundle['llm_accuracy'][brand]['date_accuracy']
        confidence = confidence_for(accuracy)
        if confidence is None:
            continue  # Fail closed on <90% or unmeasured brands; ignore model self-rating.
        proposal = candidate['proposal']
        month = proposal['date']
        if not re.fullmatch(r'\d{4}-\d{2}', month):
            raise ValueError('LLM date must be YYYY-MM')
        date.fromisoformat(month + '-01')
        response = bundle['llm_responses'][candidate['family']]
        evidence = deepcopy(proposal['evidence']) or {}
        # Preserve the original URL/quote/reason, including null or wrong citations.
        # Exact response provenance remains inspectable in the archived staging artifacts.
        evidence.update(capture_type='model_output', family=candidate['family'],
                        response_file=response['path'], response_sha256=response['sha256'],
                        captured_at=response['captured_at'])
        assertion = dict(date=month, granularity='month', source='llm', model=candidate['actual_model'],
                         confidence=confidence, evidence=evidence, brand_accuracy=accuracy)
        for variant in candidate['variants']:
            key = variant['id']
            value = (brand, assertion)
            if key in models and models[key] != value:
                raise ValueError(f'Conflicting LLM id: {key}')
            models[key] = value
    return pages, models


def brand_of(row):
    # Legacy Xiaomi rows omit brand; their stable ID namespace supplies it.
    return row.get('brand') or ('小米' if row['id'].startswith('CN:mi_cn:') else '其他')


def apply_date_enrichment(rows, path=DEFAULT_INPUT):
    pages, models = load_assertions(path)
    output = deepcopy(rows)
    for row in output:
        # Rebuild owned fields so failed/removed evidence cannot survive a later publish.
        # Neither release nor release_series is ever modified here.
        for field, assertions in [('page_first_archived', pages), ('release_llm', models)]:
            row.pop(field, None)
            match = assertions.get(row['id'])
            if match and brand_of(row) == match[0]:
                row[field] = deepcopy(match[1])
    return output


def coverage(rows):
    return {field: dict(count=sum(bool(r.get(field)) for r in rows),
                        by_brand=dict(Counter(brand_of(r) for r in rows if r.get(field))))
            for field in ('page_first_archived', 'release_llm')}
