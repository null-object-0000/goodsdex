import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from goodsdex.hp_configurations import apply_configurations, parse_parts

ROOT = Path(__file__).resolve().parents[1]


def row(sku='7P2D5PC'):
    return next(r for r in json.loads((ROOT / 'data/official/hp-history.json').read_text())['rows']
                if r.get('part_number') == sku)


def capture():
    return json.loads((ROOT / 'tests/fixtures/hp/parts-7P2D5PC.json').read_text())


def test_parts_enrich_exact_sku_without_inventing_marketing_alias_or_hz():
    supplement = parse_parts(capture(), row())
    assert supplement['params'] == {'运行内存': '32GB', '屏幕规格': 'QHD', '存储容量': '1TB'}
    assert supplement['configuration_missing']['refresh_rate']
    assert supplement['configuration_missing']['marketing_identity']


@pytest.mark.parametrize('mutation', ['hash', 'sku', 'url'])
def test_parts_reject_corrupt_or_mismatched_capture(mutation):
    c = capture()
    if mutation == 'hash':
        c['body'] += ' '
    elif mutation == 'url':
        c['url'] = c['url'].replace('hpcloud.hp.com', 'example.com')
    else:
        data = json.loads(c['body'])
        data['Body'][0]['ProductNumber'] = '9T0Q0PC'
        c['body'] = json.dumps(data)
        c['sha256'] = hashlib.sha256(c['body'].encode()).hexdigest()
    with pytest.raises(ValueError):
        parse_parts(c, row())


def test_fhd_webcam_bezel_is_not_a_display_and_multiple_options_stay_unknown():
    c = capture()
    d = json.loads(c['body'])
    d['Body'].append(dict(d['Body'][0], EnhancedDescription='SPS-RAW PANEL 15.6 FHD AG'))
    c['body'] = json.dumps(d)
    c['sha256'] = hashlib.sha256(c['body'].encode()).hexdigest()
    s = parse_parts(c, row())
    assert '屏幕规格' not in s['params']
    assert s['configuration_missing']['display']


def test_apply_preserves_ids_official_names_other_brands_and_store_fields(tmp_path):
    r = row()
    supplement = parse_parts(capture(), r)
    p = tmp_path / 'configs.json'
    p.write_text(json.dumps(dict(schema=1, rows=[supplement])))
    r['params']['屏幕规格'] = 'newer live store description'
    other = dict(r, id='other', source='another')
    original = [r, other]
    frozen = deepcopy(original)
    actual = apply_configurations(original, p)
    assert original == frozen
    assert actual[1] == other
    assert actual[0]['name'] == r['name']
    assert actual[0]['series'] == 'ProBook' and actual[0]['generation'] == 'G10'
    assert actual[0]['params']['屏幕规格'] == 'newer live store description'
    assert actual[0]['params']['存储容量'] == '1TB'
    assert apply_configurations(actual, p) == actual


def test_repair_only_the_known_duplicated_memory_unit(tmp_path):
    r = row()
    r['params']['运行内存'] = '32GBGB'
    p = tmp_path / 'configs.json'
    p.write_text(json.dumps(dict(schema=1, rows=[parse_parts(capture(), r)])))
    assert apply_configurations([r], p)[0]['params']['运行内存'] == '32GB'
    r['params']['运行内存'] = '64GB'
    assert apply_configurations([r], p)[0]['params']['运行内存'] == '64GB'
