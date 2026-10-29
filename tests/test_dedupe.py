import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from goodsdex.dedupe import analyze, dedupe_rows, finalize_public, group_by_id, validate_merge

ROOT = Path(__file__).resolve().parents[1]


def row(pid='safe', category='家电', **fields):
    return dict(id=pid, category=category, price=100, gid='1', name='商品', **fields)


class DedupeTests(unittest.TestCase):
    def test_conservative_merge_and_idempotence(self):
        rows = [row(fetched_at='2026-10-28T00:00:00Z'), row(category='电饭煲', fetched_at='2026-10-29T00:00:00Z'),
                row('conflict'), dict(row('conflict', '电饭煲'), price=200)]
        snapshot = copy.deepcopy(rows)
        output, audit = dedupe_rows(rows)
        self.assertEqual(rows, snapshot)
        self.assertEqual(len(output), 3)
        self.assertEqual(set(output[0]['categories']), {'家电', '电饭煲'})
        self.assertEqual(output[0]['fetched_at'], '2026-10-29T00:00:00Z')
        self.assertEqual(output[1:], rows[2:])
        self.assertEqual(audit['conflicts'][0]['fields'], ['price'])
        self.assertEqual(audit['facets_before'], audit['facets_after'])
        self.assertEqual(dedupe_rows(output)[0], output)

    def test_every_substantive_difference_retained(self):
        for field, value in [('price',200), ('gid','2'), ('name','别的商品'), ('params',{'x':1})]:
            rows = [row(), dict(row(category='电饭煲'), **{field:value})]
            self.assertEqual(dedupe_rows(rows)[0], rows)

    def test_validation_rejects_corruption(self):
        rows = [row(), row(category='电饭煲'), row('conflict'), dict(row('conflict'), price=200)]
        result = analyze(group_by_id(rows), len(rows))
        output, _ = dedupe_rows(rows)
        candidates = [output[1:], output + [output[0]]]
        for field, value in [('categories',['家电']), ('id','missing')]:
            corrupt = copy.deepcopy(output)
            corrupt[0][field] = value
            candidates.append(corrupt)
        corrupt = copy.deepcopy(output)
        corrupt[-1]['price'] = 100
        candidates.append(corrupt)
        for candidate in candidates:
            with self.assertRaises(ValueError):
                validate_merge(rows, candidate, result)

    def test_invalid_membership_fails_before_write(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'goods.json'
            path.write_text(json.dumps([row(category=None)]))
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                finalize_public(folder)
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse((Path(folder)/'meta.json').exists())

    def test_cli_dry_run_and_hourly_conflict_prices(self):
        with tempfile.TemporaryDirectory() as folder:
            public = Path(folder)/'public'
            public.mkdir()
            rows = [row('conflict'), dict(row('conflict'), price=200), row('normal')]
            path = public/'goods.json'
            path.write_text(json.dumps(rows))
            before = path.read_bytes()
            subprocess.run([sys.executable, str(ROOT/'scripts/dedupe_by_id.py'), '--input', str(path)], check=True, capture_output=True)
            self.assertEqual(before, path.read_bytes())
            prices = Path(folder)/'data/prices'
            prices.mkdir(parents=True)
            (prices/'latest.json').write_text(json.dumps({'prices':{'1':{'price':300}}}))
            supplements = Path(folder)/'supplements.json'
            supplements.write_text('[]')
            subprocess.run([sys.executable, str(ROOT/'scripts/ci_refresh_prices.py'), '--public', str(public), '--supplements', str(supplements), '--offline'], check=True, capture_output=True)
            refreshed = json.loads(path.read_text())
            self.assertEqual(refreshed[:2], rows[:2])
            self.assertEqual(refreshed[-1]['price'],300)
            audit = finalize_public(public)
            self.assertEqual(audit['conflict_groups'],1)
