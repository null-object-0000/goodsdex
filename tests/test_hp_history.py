import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from goodsdex.hp_history import apply_history, validate
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_hp_history import parse_capture


def capture():
    return json.loads((ROOT / 'tests/fixtures/hp/support-35L83PC.json').read_text())


def catalogue(parts=()):
    return dict(part_numbers=list(parts), urls=['https://www.hpstore.cn/sitemap-1-1.xml'],
                capture_id='test-snapshot', observed_at='2026-11-05T00:00:00Z')


def test_official_history_exact_identity_and_no_placeholder_image():
    c = capture()
    row = parse_capture(c, catalogue())
    assert row['part_number'] == '35L83PC'
    assert row['name'] == json.loads(c['body'])['data']['devices'][0]['productSpecs']['data']['productName']
    assert row['series'] == 'ProBook'
    assert row['generation'] == 'G8'
    assert row['status'] == 'retired'
    assert row['retired_at'] == catalogue()['observed_at']
    assert row['price'] is None
    assert row['params']['运行内存'] == '16GB'
    assert row['support_evidence']['product_number'] == row['part_number']
    # Unitless storage labels must not turn into an invented SSD capacity.
    assert '存储容量' not in row['params']
    if not row['image']:
        assert row['image_missing']
    assert 'fallback_product' not in (row['image'] or '')


@pytest.mark.parametrize('mutation', ['hash', 'sku', 'endpoint'])
def test_reject_corrupt_or_mismatched_support_observation(mutation):
    c = capture()
    if mutation == 'hash':
        c['body'] += ' '
    elif mutation == 'sku':
        c['payload']['devices'][0]['productNumber'] = 'WRONGPC'
    else:
        c['url'] = 'https://example.com/api'
    with pytest.raises(ValueError):
        parse_capture(c, catalogue())


def test_current_sku_is_not_retired():
    assert parse_capture(capture(), catalogue(['35L83PC']))['status'] == 'available'


def test_replay_preserves_newer_store_facts_and_other_brands(tmp_path):
    history = parse_capture(capture(), catalogue())
    path = tmp_path / 'history.json'
    path.write_text(json.dumps(dict(schema=1, rows=[history])))
    live = dict(history, name='新官方名称', price=4999, status='available',
                source_url='https://www.hpstore.cn/current.html')
    other = dict(id='another', brand='小米', price=99)
    rows = [other, live]
    original = deepcopy(rows)
    assert apply_history(rows, path) == original
    assert apply_history([], path) == [history]
    assert rows == original
    broken = dict(history, image='https://jd.com/image.jpg')
    with pytest.raises(ValueError, match='official'):
        validate(broken)


def test_duplicate_sku_history_is_rejected(tmp_path):
    row = parse_capture(capture(), catalogue())
    path = tmp_path / 'history.json'
    path.write_text(json.dumps(dict(schema=1, rows=[row, row])))
    with pytest.raises(ValueError, match='Duplicate'):
        apply_history([], path)


def test_generation_never_comes_from_cpu_screen_size_or_submodel():
    from goodsdex.hp_history import enrich_store_fields, literal_generation
    assert literal_generation('HP EliteBook 830 G7笔记本') == 'G7'
    assert literal_generation('HP 星Book g0004TU') is None
    row = enrich_store_fields(dict(id='x', source_name='惠普 暗影精灵 16英寸游戏本',
                                   name='第二代英特尔 处理器', part_number='SOMESKU'))
    assert row['generation'] is None
    assert row['generation_missing']
