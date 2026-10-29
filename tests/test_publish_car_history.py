"""Historical publication preserves all old objects and rejects unsupported evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import publish_cars as pub


def test_history_append_repeat_and_all_old_records_unchanged():
    old = [{'id': 'CN:mi_cn:legacy', 'brand': '小米', 'opaque': [v]} for v in (1, 2)]
    old += [{'id': 'other:byd', 'brand': '比亚迪', 'params': {'keep': True}}]
    result, audit = pub.prepare_history(old)
    assert result[:len(old)] == old
    assert audit == dict(old_total=3, added=5, updated=0, new_total=8)
    again, audit = pub.prepare_history(result)
    assert again == result and audit['added'] == audit['updated'] == 0
    assert sum('121KM' in r.get('name', '') for r in result) == 4
    assert sum('242KM' in r.get('name', '') for r in result) == 1


def test_history_id_conflict_rejected():
    row = json.loads(pub.HISTORY.read_text())[0]
    row['params'] = {'conflict': True}
    with pytest.raises(ValueError, match='conflict'):
        pub.prepare_history([row])


def test_unreviewed_history_rejected(tmp_path):
    rows = json.loads(pub.HISTORY.read_text())
    rows[0]['params']['电池容量(kWh)'] = '999'
    (tmp_path / 'byd-verified.json').write_text(json.dumps(rows))
    with pytest.raises(ValueError, match='reviewed'):
        pub.prepare_history([], tmp_path)


@pytest.mark.parametrize('mutation', ['third-party-price', 'missing-provenance', 'third-party-image'])
def test_history_provenance_guards(tmp_path, monkeypatch, mutation):
    rows = json.loads(pub.HISTORY.read_text())
    if mutation == 'third-party-price': rows[0]['price_source_type'] = 'third_party'
    elif mutation == 'missing-provenance': rows[0]['parameter_sources'].pop('电池容量(kWh)')
    elif mutation == 'third-party-image': rows[0]['image'] = 'https://example.com/car.jpg'
    bundle = tmp_path / 'reviewed.json'; bundle.write_text(json.dumps(rows))
    monkeypatch.setattr(pub, 'HISTORY', bundle)
    with pytest.raises(ValueError): pub.prepare_history([])
