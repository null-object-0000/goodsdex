import json
import pytest
from copy import deepcopy
from goodsdex.variant_attributes import apply_variant_attributes, DEFAULT_SOURCE, SOURCE


def test_reviewed_members_verbatim_and_additive(tmp_path):
    doc = json.loads(DEFAULT_SOURCE.read_text())
    for group in doc['groups']:
        group['members'] = [m for m in group['members'] if m['id'] != 'CN:mi_cn:product:20425']
    source = tmp_path / 'reviewed.json'
    source.write_text(json.dumps(doc))
    rows = [{'id': m['id'], 'name': 'original', 'price': 123} for g in doc['groups'] for m in g['members']]
    before = deepcopy(rows)
    output, stats = apply_variant_attributes(rows, source)
    assert rows == before
    assert stats['groups'] == 98
    assert stats['members_tagged'] == 665
    for old, new, (group, member) in zip(before, output, [(g, m) for g in doc['groups'] for m in g['members']]):
        assert {k: new[k] for k in old} == old
        if group['verdict'] == 'unknown':
            assert new == old
        else:
            assert new['attrs'] == member['attrs']
            assert new['attrs_confidence'] == group['confidence']
            assert new['attrs_source'] == SOURCE
    assert apply_variant_attributes(output, source)[0] == output


def test_unrelated_records_and_empty_attrs(tmp_path):
    source = tmp_path / 'source.json'
    source.write_text(json.dumps({'groups': [{'verdict': 'color', 'confidence': 'high', 'members': [{'id': 'empty', 'attrs': {}}]}]}))
    rows = [{'id': 'other'}, {'id': 'empty'}]
    output, stats = apply_variant_attributes(rows, source)
    assert output == rows
    assert stats['members_tagged'] == 0


def test_source_conflict_blocks_annotation(tmp_path):
    doc = json.loads(DEFAULT_SOURCE.read_text())
    for group in doc['groups']:
        for member in group['members']:
            if member.get('withheld_attrs'):
                member['attrs'] = member.pop('withheld_attrs')
    source = tmp_path / 'conflicting.json'
    source.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="Conflicting variant conclusions: CN:mi_cn:product:20425"):
        apply_variant_attributes([], source)


def test_approved_source_withholds_conflict_and_counts_actual_rows():
    doc = json.loads(DEFAULT_SOURCE.read_text())
    rows = [{'id': key} for key in dict.fromkeys(
        m['id'] for g in doc['groups'] for m in g['members'])]
    output, stats = apply_variant_attributes(rows)
    assert stats['groups'] == 98
    assert stats['members_tagged'] == sum(bool(r.get('attrs')) for r in output) == 665
    assert next(r for r in output if r['id'] == 'CN:mi_cn:product:20425') == {'id': 'CN:mi_cn:product:20425'}
    assert apply_variant_attributes(output)[0] == output


def test_finalizer_and_detail_shards_publish_reviewed_attrs(tmp_path):
    from goodsdex.dedupe import finalize_public
    from goodsdex.shards import build_shards, shard_for
    key = 'CN:mi_cn:product:10050230'
    conflict = 'CN:mi_cn:product:20425'
    rows = [dict(id=k, name='商品', category='手机', price=100) for k in (key, conflict)]
    (tmp_path / 'goods.json').write_text(json.dumps(rows))
    finalize_public(tmp_path)
    meta = build_shards(tmp_path)
    output = json.loads((tmp_path / 'goods.json').read_text())
    assert meta['variant_attrs']['members_tagged'] == 1
    assert 'attrs' not in output[1]
    detail = json.loads((tmp_path / f'detail/{shard_for(key):02x}.json').read_text())[key]
    assert detail['attrs'] == output[0]['attrs']
    assert detail['attrs']['variant'] == '单机'
    assert detail['attrs_confidence'] == 'medium'
    finalize_public(tmp_path)
    assert json.loads((tmp_path / 'goods.json').read_text()) == output
