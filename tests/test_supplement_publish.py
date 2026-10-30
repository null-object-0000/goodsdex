import copy
import json
import tempfile
import unittest
from pathlib import Path

from goodsdex.supplements import merge, publish


class SupplementPublicationTests(unittest.TestCase):
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
