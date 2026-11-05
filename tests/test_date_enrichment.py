from copy import deepcopy
import gzip
import json
from pathlib import Path
import subprocess
import sys

import pytest
from goodsdex.date_enrichment import DEFAULT_INPUT, apply_date_enrichment, confidence_for, load_assertions

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('accuracy,expected', [(None,None),(.899999,None),(.90,'medium'),(.96999,'medium'),(.97,'high'),(1,'high')])
def test_confidence_boundaries(accuracy, expected):
    assert confidence_for(accuracy) == expected


def test_real_inputs_gate_and_preserve_dates():
    before = json.loads(gzip.decompress((ROOT/'docs/independent-dates-20261103/baseline-goods.json.gz').read_bytes()))
    original = deepcopy(before)
    result = apply_date_enrichment(before)
    assert before == original
    assert [{k:v for k,v in r.items() if k not in ('page_first_archived','release_llm')} for r in result] == before
    assert apply_date_enrichment(result) == result
    assert {r['brand'] for r in result if r.get('release_llm')} == {'Apple','富士'}
    assert any(r.get('release_llm') and (r.get('release') or {}).get('date') for r in result)
    for r in result:
        if r.get('release_llm'):
            assert r['release_llm']['confidence'] == ('high' if r['brand']=='Apple' else 'medium')


def test_failed_or_absent_pages_and_ineligible_models_clear_stale_fields(tmp_path):
    b = json.loads(gzip.decompress(DEFAULT_INPUT.read_bytes()))
    jobs = {j['job_id']:j for j in b['wayback_manifest']['jobs']}
    archived = next(r for r in b['wayback_results'] if r['status']=='archived')
    key = jobs[archived['id']]['record_ids'][0]
    row = dict(id=key,brand=jobs[archived['id']]['brand'],release={'date':'2000-01'},release_series={'date':'1999-01'},
               page_first_archived={'date':'stale'},release_llm={'date':'stale'})
    for status in ('error','not_archived'):
        archived['status'] = status
        b['llm_accuracy'] = {brand:{**a,'date_accuracy':None} for brand,a in b['llm_accuracy'].items()}
        p=tmp_path/'inputs.gz';p.write_bytes(gzip.compress(json.dumps(b).encode()))
        result=apply_date_enrichment([row],p)[0]
        assert 'page_first_archived' not in result and 'release_llm' not in result
        assert result['release']==row['release'] and result['release_series']==row['release_series']


def test_finalizer_replays_and_details_only(tmp_path):
    from goodsdex.shards import shard_for
    baseline=gzip.decompress((ROOT/'docs/independent-dates-20261103/baseline-goods.json.gz').read_bytes())
    (tmp_path/'goods.json').write_bytes(baseline)
    (tmp_path/'meta.json').write_text('{}')
    (tmp_path/'prices.json').write_text('{}')
    command=[sys.executable,str(ROOT/'scripts/finalize_public.py'),'--public',str(tmp_path)]
    subprocess.run(command,check=True,capture_output=True)
    result=json.loads((tmp_path/'goods.json').read_bytes())
    from goodsdex.series_release import apply_series_releases
    from goodsdex.release_dates import apply_release_dates
    # The ordinary finalizer also replays reviewed product dates, which may
    # legitimately grow after this historical snapshot was frozen.
    from goodsdex.mi_names import apply_page_names
    from goodsdex.retirement import reconcile
    history = reconcile([], json.loads(baseline))
    expected=apply_date_enrichment(apply_series_releases(apply_release_dates(apply_page_names(history))))
    from goodsdex.release_coverage import apply_priority_dates
    expected=apply_priority_dates(expected)
    from goodsdex.source_urls import apply_source_urls
    expected=apply_source_urls(expected)
    from goodsdex.variant_attributes import apply_variant_attributes
    expected, _ = apply_variant_attributes(expected)
    # Independently frozen expected exclusions include the title repair.
    # Enrichment and every retained field must still be identical.
    archived=json.loads((tmp_path/'archive/accessories.json').read_text())
    excluded={r['id'] for r in archived}
    reviewed=json.loads((ROOT/'docs/name-fidelity-20261104/historical-exclusion-expectations.json').read_text())['docs/independent-dates-20261103/baseline-goods.json.gz']
    assert excluded == {r['id'] for r in reviewed}
    assert all(not r.get('release') for r in archived)
    excluded.update(r['id'] for r in json.loads((tmp_path/'archive/services.json').read_text()))
    assert [{k:v for k,v in r.items() if k not in ('brand','brand_source')} for r in result] == [
        {k:v for k,v in r.items() if k not in ('brand','brand_source')} for r in expected if r['id'] not in excluded]
    for field in ('page_first_archived','release_llm','release_series'):
        sample=next(r for r in result if r.get(field))
        detail=json.loads((tmp_path/f"detail/{shard_for(sample['id']):02x}.json").read_bytes())
        assert detail[sample['id']][field]==sample[field]
        for p in (tmp_path/'index').glob('*.json'):
            assert all(field not in r for r in json.loads(p.read_bytes())['items'])
    # Collectors can discard enrichments; every ordinary finalize restores them.
    (tmp_path/'goods.json').write_text(json.dumps([{k:v for k,v in r.items() if k not in ('release_llm','page_first_archived')} for r in result]))
    subprocess.run(command,check=True,capture_output=True)
    assert json.loads((tmp_path/'goods.json').read_bytes())==result
