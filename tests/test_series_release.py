from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

import pytest

from goodsdex.release_dates import digest, validate
from goodsdex.series_release import (
    DEFAULT_INPUT, apply_series_releases, coverage, effective_release,
    identity, is_accessory, validate_batch,
)
from goodsdex.shards import build_shards

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/series-release-pilot-20261103'


@pytest.fixture
def bundle():
    return json.loads(DEFAULT_INPUT.read_text())


@pytest.fixture
def rows():
    return json.loads((DOC / 'pilot-rows.json').read_text())


def test_pilot_preserves_product_dates_and_is_idempotent(rows):
    before = deepcopy(rows)
    out = apply_series_releases(rows)
    assert rows == before
    assert [r.get('release') for r in out] == [r.get('release') for r in before]
    assert apply_series_releases(out) == out
    assert coverage(out) == dict(total=17, product=6, series=11, missing=0, accessories=0)


@pytest.mark.parametrize('source', ['official', 'third_party', 'official_hidden'])
def test_product_priority_even_when_series_is_official(rows, source):
    row = deepcopy(rows[0])
    row['release'] = dict(date='2020-01', source=source)
    row['series_release']['source'] = 'official'
    r = effective_release(row)
    assert r['date'] == '2020-01' and r['level'] == 'product'
    row['release']['source'] = 'llm'
    assert effective_release(row)['level'] == 'series'


@pytest.mark.parametrize('changed', ['name', 'params', 'market'])
def test_identity_or_generation_drift_fails_closed(rows, changed):
    row = deepcopy(rows[0])
    row[changed] = {'产品系列': '2022款'} if changed == 'params' else 'GLOBAL' if changed == 'market' else row['name'] + ' 2022款'
    with pytest.raises(ValueError, match='drift'):
        apply_series_releases([row])


def test_accessory_service_and_new_variants_never_inherit(rows):
    for kind in ('accessory', 'service'):
        row = dict(rows[0], kind=kind)
        with pytest.raises(ValueError, match='Accessory'):
            apply_series_releases([row])
    row = dict(rows[0], id='CN:mi_cn:product:unreviewed',name='同系列2024款')
    assert 'series_release' not in apply_series_releases([row])[0]
    assert is_accessory(dict(name='米家扫拖机器人 5 Pro 配件', kind='unknown'))
    assert not is_accessory(dict(name='Xiaomi Watch S4', kind='machine', category='穿戴配件'))


def test_conflicts_rollback_and_year_precision(tmp_path, rows, bundle):
    path = tmp_path / 'series.json'
    bundle['batches'].append(deepcopy(bundle['batches'][0]))
    path.write_text(json.dumps(bundle))
    with pytest.raises(ValueError, match='Duplicate'):
        apply_series_releases(rows, path)
    bundle['batches'].pop()
    bundle['enabled'] = False
    path.write_text(json.dumps(bundle))
    assert all('series_release' not in r for r in apply_series_releases(rows,path))
    bundle['enabled'] = True
    bundle['batches'][0]['series_release'].update(date='2025',granularity='year')
    path.write_text(json.dumps(bundle))
    out=apply_series_releases(rows,path)
    r=next(r['series_release'] for r in out if r['series_release']['batch_id']==bundle['batches'][0]['id'])
    assert r['display']=='该系列 2025 年发布'


def test_series_cannot_enter_product_release(bundle):
    c=dict(family='bad',ids=['bad'],release=bundle['batches'][0]['series_release'])
    with pytest.raises(ValueError,match='Series assertions'):
        validate(c)


def test_evidence_and_membership_are_frozen(bundle, rows):
    by_id={r['id']:r for r in rows}
    rollout = ROOT / 'docs/series-release-rollout-20261103/baseline-goods.json.gz'
    if rollout.exists():
        by_id.update({r['id']: r for r in json.loads(gzip.decompress(rollout.read_bytes()))})
    for b in bundle['batches']:
        validate_batch(b)
        e=b['series_release']['evidence']
        assert hashlib.sha256((ROOT/e['capture_file']).read_bytes()).hexdigest()==e['sha256']
        for m in b['members']:
            assert digest(identity(by_id[m['id']]))==m['identity_sha256']
    b=deepcopy(bundle['batches'][0]);b['series_release']['source']='official'
    with pytest.raises(ValueError):
        validate_batch(b)


def test_sharded_index_and_detail_keep_series_provenance(rows,tmp_path):
    (tmp_path/'goods.json').write_text(json.dumps(rows))
    build_shards(tmp_path)
    index=json.loads((tmp_path/'index/other.json').read_text())
    assert [r['series_release'] for r in index['items']]==[r['series_release'] for r in rows]
    detail={k:v for p in (tmp_path/'detail').glob('*.json') for k,v in json.loads(p.read_text()).items()}
    assert all(detail[r['id']]['series_release']==r['series_release'] for r in rows)
