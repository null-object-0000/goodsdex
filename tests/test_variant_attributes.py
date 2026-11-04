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


def test_source_conflict_blocks_annotation():
    with pytest.raises(ValueError, match="Conflicting variant conclusions: CN:mi_cn:product:20425"):
        apply_variant_attributes([])
