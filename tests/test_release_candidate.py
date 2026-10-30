"""Lost updates, independent brands, fail-closed conflicts, append-only history."""
import base64
import copy
import json
from pathlib import Path
import sys

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from release_candidate import merge_goods, merge_candidate, allowed_path


def row(key, source, price):
    return dict(id=key, source=source, name=key, price=price, params={'cpu': 'kept'})


def test_stale_collectors_keep_other_brand_and_unrelated_fields():
    base = [row('mi', 'mi_cn', 100), row('hp', 'hp_cn', 200)]
    price = copy.deepcopy(base)
    price[0]['price'] = 101
    hp = copy.deepcopy(base)
    hp[1]['price'] = 201
    hp[0]['params']['cpu'] = 'newer daily crawl'
    result = merge_goods(base, price, hp, 'prices')
    assert result[0]['price'] == 101
    assert result[0]['params']['cpu'] == 'newer daily crawl'
    assert result[1] == hp[1]
    assert merge_goods(base, price, result, 'prices') == result # publish-only re-run


def test_same_field_conflict_never_rolls_back_new_price():
    base = [row('hp', 'hp_cn', 100)]
    candidate = [dict(base[0], price=101)]
    latest = [dict(base[0], price=102)]
    with pytest.raises(ValueError, match='Concurrent change'):
        merge_goods(base, candidate, latest, 'hp')
    assert latest[0]['price'] == 102


def test_collector_cannot_edit_other_brand_or_drop_ids():
    base = [row('hp', 'hp_cn', 100)]
    with pytest.raises(ValueError, match='another responsibility'):
        merge_goods(base, [dict(base[0], price=101)], base, 'apple')
    with pytest.raises(ValueError, match='drop'):
        merge_goods(base, [], base, 'hp')


def encode(value):
    return base64.b64encode(value).decode() if value is not None else None


def bundle(tmp_path, files):
    p = tmp_path / 'candidate.json'
    p.write_text(json.dumps(dict(schema=1, scope='prices', base='test', files={
        k: dict(before=encode(b), after=encode(a)) for k, (b, a) in files.items()})))
    return p


def test_append_observations_preserves_newer_published_history(tmp_path):
    p = tmp_path / 'public/prices/month.jsonl'
    p.parent.mkdir(parents=True)
    lines = [(json.dumps(dict(fetched_at=f'2026-10-31T{h}:00:00+08:00', prices={}))+'\n').encode() for h in ('01','02','03')]
    p.write_bytes(lines[0]+lines[2])
    c = bundle(tmp_path, {'public/prices/month.jsonl': (lines[0], lines[0]+lines[1])})
    merge_candidate(tmp_path, c)
    assert p.read_bytes() == lines[0]+lines[2]+lines[1]
    merge_candidate(tmp_path, c)
    assert p.read_bytes() == lines[0]+lines[2]+lines[1]


def test_invalid_delta_does_not_partially_write(tmp_path):
    p = tmp_path / 'data/categories/a.json'
    p.parent.mkdir(parents=True)
    p.write_text('{"value": 3}')
    c = bundle(tmp_path, {'data/categories/new.json': (None, b'[]'), 'data/categories/a.json': (b'{"value": 1}', b'{"value": 2}')})
    with pytest.raises(ValueError, match='Concurrent change'):
        merge_candidate(tmp_path, c)
    assert not (p.parent/'new.json').exists()
    assert json.loads(p.read_text()) == {'value': 3}


@pytest.mark.parametrize('name', ['../public/goods.json', '/public/goods.json', 'public/meta.json', 'public/index/hp_cn.json', 'public/detail/00.json', '.github/workflows/evil.yml'])
def test_candidate_never_contains_generated_shards_or_unsafe_paths(name):
    assert not allowed_path(name)
