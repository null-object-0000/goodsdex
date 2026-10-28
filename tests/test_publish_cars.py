"""Publication failure paths must leave both release files untouched."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import publish_cars as pub


def reviewed():
    return [r for filename, *_ in pub.SOURCES for r in json.loads((pub.INPUT / filename).read_text())]


def test_initial_and_repeat_publication_preserve_other_objects():
    other = [{'id': f'other:{b}', 'brand': b, 'nested': {'opaque': [None, 1]}}
             for b in ('小米', 'Apple', '大疆', '富士')]
    rows, audit = pub.prepare(other)
    assert audit == dict(old_total=4, added=34, updated=0, new_total=38)
    assert rows[:4] == other
    again, audit = pub.prepare(rows)
    assert audit == dict(old_total=38, added=0, updated=34, new_total=38)
    assert rows == again


def test_existing_duplicates_fail_without_writing(tmp_path, monkeypatch):
    goods = tmp_path / 'goods.json'; meta = tmp_path / 'meta.json'
    goods.write_text('[{"id":"legacy"},{"id":"legacy"}]'); meta.write_text('{"count":2}')
    before = (goods.read_bytes(), meta.read_bytes())
    monkeypatch.setattr(sys, 'argv', ['publish_cars', '--public', str(tmp_path)])
    assert pub.main() == 1
    assert (goods.read_bytes(), meta.read_bytes()) == before


@pytest.mark.parametrize('mutation', ['duplicate', 'missing-source', 'wrong-brand', 'missing-price', 'wrong-kind', 'gap'])
def test_bad_inputs_rejected(tmp_path, mutation):
    for filename in ('byd-verified.json', 'xiaomi-candidates.json', 'parameter-gaps.json'):
        (tmp_path / filename).write_bytes((pub.INPUT / filename).read_bytes())
    path = tmp_path / 'byd-verified.json'; rows = json.loads(path.read_text())
    if mutation == 'duplicate': rows[1] = deepcopy(rows[0])
    elif mutation == 'missing-source': rows[0]['source_url'] = ''
    elif mutation == 'wrong-brand': rows[0]['brand'] = '小米'
    elif mutation == 'missing-price': rows[0].pop('price')
    elif mutation == 'wrong-kind': rows[0]['price_kind'] = 'sku'
    elif mutation == 'gap': rows[0]['id'] = json.loads((tmp_path / 'parameter-gaps.json').read_text())[0]['id']
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError): pub.prepare([], tmp_path)


def test_null_price_is_explicit_none(tmp_path):
    for filename in ('byd-verified.json', 'xiaomi-candidates.json', 'parameter-gaps.json'):
        (tmp_path / filename).write_bytes((pub.INPUT / filename).read_bytes())
    path = tmp_path / 'byd-verified.json'; rows = json.loads(path.read_text())
    rows[0].update(price=None, price_kind='none'); path.write_text(json.dumps(rows))
    result, _ = pub.prepare([], tmp_path)
    assert result[0]['price'] is None and result[0]['price_kind'] == 'none'


def test_hourly_guard_checks_type_counts():
    from goodsdex.cars import assert_cars_unchanged
    row = {'id': 'CN:byd:car:test', 'product_type': 'car', 'params': {'x': 1}}
    with pytest.raises(ValueError): assert_cars_unchanged([row], [{**row, 'product_type': 'machine'}])
    with pytest.raises(ValueError): assert_cars_unchanged([row], [{**row, 'params': {}}])
