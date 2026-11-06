import copy
import json
import tempfile
import unittest
from pathlib import Path

from goodsdex.supplements import merge, publish


class SupplementPublicationTests(unittest.TestCase):
    def test_reviewed_deletions_in_supplements_and_replayed_brand_cache(self):
        import subprocess
        import sys
        from goodsdex.release_policy import ALLOWED_DELETIONS

        rebuilt = [dict(id="keep", name="商品")]
        tombstones = [dict(id=key) for key in ALLOWED_DELETIONS]
        previous = rebuilt + tombstones
        rows, audit = merge(rebuilt, tombstones, previous)
        self.assertEqual(rows, rebuilt)
        self.assertEqual(len(rows), len(rebuilt))
        self.assertEqual(set(audit["allowed_deletions"]), set(ALLOWED_DELETIONS))
        script = Path(__file__).resolve().parents[1] / "scripts/verify_goods_release.py"
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            (path / "previous.json").write_text(json.dumps(previous))
            (path / "extras.json").write_text(json.dumps(tombstones))
            (path / "merge-audit.json").write_text(json.dumps(audit))
            command = [sys.executable, str(script), "--public", str(path),
                       "--previous", str(path / "previous.json"),
                       "--supplements", str(path / "extras.json")]
            # Both already-clean input and a later publisher replaying old rows
            # must produce exactly the same final release.
            for current in (rebuilt, previous):
                (path / "goods.json").write_text(json.dumps(current))
                (path / "meta.json").write_text('{}')
                subprocess.run(command, check=True, capture_output=True)
                self.assertEqual(json.loads((path / "goods.json").read_text()), rebuilt)
            # A genuine absent supplement still blocks before removing anything.
            extras = tombstones + [dict(id="missing", source="s", catalog_identity="s")]
            (path / "extras.json").write_text(json.dumps(extras))
            (path / "goods.json").write_text(json.dumps(previous))
            original = (path / "goods.json").read_bytes()
            failed = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('missing', failed.stderr)
            self.assertEqual((path / "goods.json").read_bytes(), original)

    def test_crawler_wins_and_repeat_is_idempotent(self):
        current = [{"id": "same", "price": 200}]
        supplements = [dict(id=k, price=None, source="supplement", catalog_identity="supplement")
                       for k in ("same", "legacy")]
        before = copy.deepcopy(current)
        rows, audit = merge(current, supplements, current)
        self.assertEqual(rows[0], before[0])
        self.assertEqual(audit["count"], audit["rebuilt_count"] + audit["added_count"])
        self.assertEqual(audit["added_count"], 1)
        self.assertEqual(merge(rows, supplements, rows)[0], rows)
        self.assertEqual(current, before)

    def test_loss_fails_before_writes_even_if_total_grows(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            original = '[{"id":"lost"}]'
            (path / "goods.json").write_text(original)
            (path / "extra.json").write_text('[]')
            with self.assertRaisesRegex(ValueError, "lost"):
                publish([{"id": "new1"}, {"id": "new2"}], path,
                        json.loads(original), path / "extra.json")
            self.assertEqual((path / "goods.json").read_text(), original)
            self.assertFalse((path / "meta.json").exists())

    def test_duplicates_and_missing_provenance_fail(self):
        for current, extras in (([], [dict(id="x", source="s", catalog_identity="s")] * 2), ([], [{"id": "x"}])):
            with self.assertRaises(ValueError):
                merge(current, extras, [])

    def test_meta_recomputed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            extra = [dict(id="CN:mi_cn:product:1", name="测试商品", kind="machine", price=None,
                          source="supplement", catalog_identity="supplement")]
            (path / "extra.json").write_text(json.dumps(extra))
            (path / "meta.json").write_text('{"count":999,"brands":{"old":999}}')
            meta = publish([dict(id="apple", brand="Apple", kind="machine", price=1)], path, [], path / "extra.json")
            self.assertEqual(meta["count"], 2)
            self.assertEqual(meta["brands"], {"Apple": 1, "小米": 1})
            self.assertEqual(meta["with_price"], 1)
            self.assertEqual(meta["by_kind"], {"machine": 2})


class ExistingCategoryRowsTests(unittest.TestCase):
    def test_existing_same_id_category_rows_are_retained(self):
        rows = [dict(id="x", category="a"), dict(id="x", category="b")]
        result, audit = merge(rows, [], rows)
        self.assertEqual(result, rows)
        self.assertEqual(audit["count"], 2)


class SourceCarryForwardTests(unittest.TestCase):
    def test_uncovered_source_carries_whole_class_before_supplements(self):
        current = dict(id='current', source='crawler', name='updated')
        external = [dict(id=key, source='intake', name=key,
                         opaque={'evidence': [None, {'keep': True}]})
                    for key in ('external-1', 'external-2')]
        previous = [current] + external
        original = copy.deepcopy(previous)
        # A supplemental row does not mean the rebuild covered its source.
        extras = [dict(id='supplement', source='intake', catalog_identity='s')]
        rows, audit = merge([current], extras, previous, apply_backfills=False)
        self.assertEqual(rows, previous + extras)
        self.assertEqual(previous, original)
        self.assertEqual(audit['carried_ids'], ['external-1', 'external-2'])
        self.assertEqual(audit['carried_sources'], ['intake'])
        self.assertEqual(audit['missing_ids'], [])
        self.assertEqual(audit['count'], audit['rebuilt_count'] + audit['added_count'])

    def test_covered_source_missing_row_still_fails(self):
        present = dict(id='present', source='crawler')
        missing = dict(id='missing', source='crawler')
        with self.assertRaisesRegex(ValueError, 'Publication would drop 1 IDs.*missing'):
            merge([present], [], [present, missing], apply_backfills=False)

    def test_car_hp_and_atour_still_carry_when_source_is_covered(self):
        for missing in (dict(id='car', source='car_lane', product_type='car'),
                        dict(id='CN:byd:car:legacy', source='car_lane'),
                        dict(id='hp', source='hp_cn'), dict(id='atour', source='atour')):
            with self.subTest(missing=missing):
                current = dict(id='current', source=missing['source'])
                rows, audit = merge([current], [], [current, missing], apply_backfills=False)
                self.assertEqual(rows, [current, missing])
                self.assertEqual(audit['carried_ids'], [missing['id']])

    def test_missing_source_is_a_covered_bucket_when_present(self):
        current = dict(id='current')
        missing = dict(id='missing')
        with self.assertRaisesRegex(ValueError, 'Publication would drop 1 IDs.*missing'):
            merge([current], [], [current, missing], apply_backfills=False)
        rows, audit = merge([dict(id='other', source='crawler')], [], [missing], apply_backfills=False)
        self.assertIn(missing, rows)
        self.assertEqual(audit['carried_sources'], [None])

    def test_uncovered_source_does_not_resurrect_reviewed_deletions(self):
        from goodsdex.release_policy import ALLOWED_DELETIONS
        previous = [dict(id=key, source='uncovered') for key in ALLOWED_DELETIONS]
        rows, audit = merge([], [], previous, apply_backfills=False)
        self.assertEqual(rows, [])
        self.assertEqual(audit['carried_ids'], [])
        self.assertEqual(audit['allowed_deletions'], dict(ALLOWED_DELETIONS))


class RefreshEntryPointTests(unittest.TestCase):
    def test_offline_refresh_replays_price_and_preserves_models_and_supplements(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            public = root / "public"
            public.mkdir()
            latest = root / "data/prices"
            latest.mkdir(parents=True)
            previous = [dict(id="current", gid="1", price=3),
                        dict(id="legacy", gid="2", price=None, record_level="model_reference", discontinued=True)]
            (public / "goods.json").write_text(json.dumps(previous))
            extras = [dict(id="supplement", price=None, source="s", catalog_identity="s")]
            (root / "extra.json").write_text(json.dumps(extras))
            (latest / "latest.json").write_text(json.dumps(dict(prices={
                "1": dict(price=4, market_price=None), "2": dict(price=999)})))
            script = Path(__file__).resolve().parents[1] / "scripts/ci_refresh_prices.py"
            command = [sys.executable, str(script), "--public", str(public),
                       "--supplements", str(root / "extra.json"), "--offline"]
            subprocess.run(command, check=True, capture_output=True)
            result = json.loads((public / "goods.json").read_text())
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]["price"], 4)
            self.assertIsNone(result[0]["market_price"])
            self.assertIsNone(result[1]["price"])
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(json.loads((public / "goods.json").read_text()), result)


class RebuildEntryPointTests(unittest.TestCase):
    def test_rebuild_restores_external_rows_before_guard(self):
        from goodsdex.publish import build
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cats, public = root / "cats", root / "public"
            cats.mkdir()
            public.mkdir()
            (cats / "one.json").write_text(json.dumps([dict(
                product=dict(product_id="crawler", name="updated"), view=dict(values=dict(price=9)))]))
            previous = [dict(id=key) for key in ("crawler", "legacy", "category")]
            (public / "goods.json").write_text(json.dumps(previous))
            extra = [dict(id=key, source="s", catalog_identity="s", price=None)
                     for key in ("crawler", "legacy", "category")]
            (root / "extra.json").write_text(json.dumps(extra))
            meta = build(cats, public, root / "extra.json")
            result = json.loads((public / "goods.json").read_text())
            self.assertEqual(meta["count"], 3)
            self.assertEqual(result[0]["name"], "updated")
            self.assertEqual(result[0]["price"], 9)
            self.assertEqual({r["id"] for r in previous} - {r["id"] for r in result}, set())


class CarRefreshScopeTests(unittest.TestCase):
    def test_car_publication_does_not_replay_unrelated_supplements(self):
        import subprocess, sys
        root = Path(__file__).resolve().parents[1]
        car = json.loads((root/'data/official/car-catalog.json').read_text())['rows'][0]
        other = dict(id='other', name='其他商品', opaque={'keep': ['all', None]})
        previous = [other, car]
        extras = [dict(id='CN:mi_cn:product:unrelated', name='其他补充商品', source='supplement', catalog_identity='s')]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            extra = out/'extras.json'; extra.write_text(json.dumps(extras))
            prior = out/'previous.json'; prior.write_text(json.dumps(previous))
            publish(previous, out, previous, extra, apply_backfills=False, car_refresh=True)
            self.assertEqual(json.loads((out/'goods.json').read_text()), previous)
            subprocess.run([sys.executable, str(root/'scripts/verify_goods_release.py'), '--public', tmp,
                            '--previous', str(prior), '--supplements', str(extra), '--car-refresh'],
                           check=True, capture_output=True)
            self.assertEqual(json.loads((out/'goods.json').read_text()), previous)
            # The normal publisher still owns adding these supplemental products.
            self.assertEqual(len(merge(previous, extras, previous, apply_backfills=False)[0]), 3)
            before = (out/'goods.json').read_bytes()
            with self.assertRaisesRegex(ValueError, 'non-car objects'):
                publish([dict(other, name='越权更新'), car], out, previous, extra,
                        apply_backfills=False, car_refresh=True)
            self.assertEqual((out/'goods.json').read_bytes(), before)
