import copy
import json
import tempfile
import unittest
from pathlib import Path

from goodsdex.dedupe import analyze, dedupe_rows, finalize_public, group_by_id, validate_merge
from goodsdex.public_fields import (PROTECTED_IDS, assert_public_fields,
                                  normalize_params, normalize_public_row)
from goodsdex.publish import to_public


def row(**fields):
    return dict(id='CN:mi_cn:product:test', gid=123, name='米家 X100 Pro',
                category='家电', price=100, **fields)


class PublicFieldTests(unittest.TestCase):
    def test_alias_union_and_operational_noise(self):
        before = [row(params={'cpu': 'X100', 'evaluate_total': 1}),
                  row(params={'CPU型号': 'X100', '额定功率': '10W', 'qa_total': 2},
                      from_container=True)]
        snapshot = copy.deepcopy(before)
        output, audit = dedupe_rows(before)
        self.assertEqual(before, snapshot)
        self.assertEqual(output[0]['params'], {'CPU型号': 'X100', '额定功率': '10W'})
        self.assertTrue(output[0]['from_container'])
        self.assertEqual(audit['merged_groups'], 1)
        self.assertEqual(dedupe_rows(output)[0], output)
        self.assertEqual(audit['brands_before'], audit['brands_after'])

    def test_real_value_and_identity_conflicts_stay_original(self):
        for field, value in [('gid', 456), ('price', 200), ('brand', '其他'),
                             ('name', '米家 X200 Pro')]:
            before = [row(params={'cpu': 'A'}),
                      dict(row(params={'CPU型号': 'A'}), **{field: value})]
            self.assertEqual(dedupe_rows(before)[0], before)
        before = [row(params={'cpu': 'A'}), row(params={'CPU型号': 'B'})]
        self.assertEqual(dedupe_rows(before)[0], before)
        with self.assertRaises(ValueError):
            normalize_params({'cpu': 'A', 'CPU型号': 'B'})

    def test_protected_groups_are_byte_value_identical_even_if_compatible(self):
        for pid, kind in PROTECTED_IDS.items():
            before = [dict(row(params={'cpu': 'A', 'qa_total': 5}), id=pid)] * 2
            output, audit = dedupe_rows(before)
            self.assertEqual(output, before)
            self.assertEqual(audit['conflicts'][0]['type'], kind)
            assert_public_fields(output)

    def test_names_keep_model_tokens(self):
        for name, expected in [('REDMI K80 Pro 系列', 'REDMI K80 Pro'),
                               ('Xiaomi 17 Pro Max', 'Xiaomi 17 Pro Max'),
                               ('米家 X100 X100', '米家 X100 X100'),
                               ('米家净水器13号滤芯（PPC） 13号滤芯（PPC）',
                                '米家净水器13号滤芯（PPC）')]:
            self.assertEqual(normalize_public_row(dict(row(), name=name))['name'], expected)

    def test_publisher_and_guard(self):
        item = to_public({'product': {'product_id': row()['id'], 'name': '米家 X100'},
                          'view': {'values': {'cpu': 'A', 'evaluate_real': 9, '收藏数': 1}}})
        self.assertEqual(item['params'], {'CPU型号': 'A'})
        for key in ('qa_total', 'evaluate_real', '收藏数'):
            with self.assertRaises(ValueError):
                assert_public_fields([row(params={key: 1})])

    def test_union_key_corruption_rejected(self):
        before = [row(params={'cpu': 'A'}), row(params={'cpu': 'A', '功率': '10W'})]
        result = analyze(group_by_id(before), len(before))
        output, _ = dedupe_rows(before)
        del output[0]['params']['功率']
        with self.assertRaisesRegex(ValueError, 'Merged field loss'):
            validate_merge(before, output, result)

    def test_guard_failure_writes_nothing(self):
        # Unknown conflicting group stays raw, so its forbidden fields fail the gate.
        before = [row(params={'evaluate_real': 1, 'cpu': 'A'}),
                  row(params={'evaluate_real': 2, 'cpu': 'B'})]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'goods.json'
            path.write_text(json.dumps(before))
            raw = path.read_bytes()
            with self.assertRaises(ValueError):
                finalize_public(folder)
            self.assertEqual(path.read_bytes(), raw)
            self.assertFalse((Path(folder) / 'merge-audit.json').exists())
