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
    elif mutation == 'third-party-image': rows[0].update(image='https://example.com/car.jpg', image_source_type='third_party', image_source='third_party')
    bundle = tmp_path / 'reviewed.json'; bundle.write_text(json.dumps(rows))
    monkeypatch.setattr(pub, 'HISTORY', bundle)
    with pytest.raises(ValueError): pub.prepare_history([])


@pytest.mark.parametrize('source,url,accepted', [
    ('official_archive', 'https://web.archive.org/web/20220516034632id_/https://www.bydauto.com.cn/image.jpg', True),
    ('official_archive', None, False),
    ('official_archive', '', False),
    ('official_archive', 'https://www.bydauto.com.cn/image.jpg', False),
    ('official_archive', 'https://web.archive.org.evil.example/image.jpg', False),
    ('official_archive', 'https://web.archive.org@evil.example/image.jpg', False),
    ('official_archive', 'http://web.archive.org/image.jpg', False),
    ('third_party', 'https://web.archive.org/image.jpg', False),
    ('user_upload', 'https://web.archive.org/image.jpg', False),
    ('official', 'https://www.bydauto.com.cn/image.jpg', True),
])
def test_history_archive_image_gate(tmp_path, monkeypatch, source, url, accepted):
    rows = json.loads(pub.HISTORY.read_text())
    rows[0].update(image='https://spend-good.oss-cn-shanghai.aliyuncs.com/goods/test.jpg',
                   image_source_type=source, image_source=source)
    rows[0].pop('image_source_url', None)
    if url is not None:
        rows[0]['image_source_url'] = url
    bundle = tmp_path / 'reviewed.json'
    bundle.write_text(json.dumps(rows))
    monkeypatch.setattr(pub, 'HISTORY', bundle)
    if accepted:
        result, _ = pub.prepare_history([])
        assert result[0] == rows[0]
    else:
        with pytest.raises(ValueError, match='Historical.*image'):
            pub.prepare_history([])
