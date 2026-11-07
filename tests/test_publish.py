"""发布集主图契约：只增加顶层链接，不泄漏整组展示素材。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.publish import to_public


class PublishTests(unittest.TestCase):
    def test_image_is_top_level_and_existing_fields_are_preserved(self):
        rec = {
            "product": {
                "product_id": "mi-123", "name": "商品", "kind": "device",
                "category": "手机", "from_container": True,
            },
            "fetched_at": "2026-10-09T12:00:00+08:00",
            "view": {"values": {
                "price": 1999, "market_price": 2299, "gid": "123",
                "img_url": "https://example.com/main.jpg",
                "carousel": ["https://example.com/other.jpg"] * 100,
                "pc_imgs": ["https://example.com/detail.jpg"] * 100,
                "容量": "256GB", "_internal": True,
            }},
        }
        assert to_public(rec) == {
            "id": "mi-123", "name": "商品", "kind": "device",
            "category": "手机", "price": 1999, "market_price": 2299,
            "gid": "123", "image": "https://example.com/main.jpg",
            "fetched_at": "2026-10-09T12:00:00+08:00",
            "params": {"容量": "256GB"}, "from_container": True,
        }


    def test_missing_image_is_null_without_carousel_fallback(self):
        for values in ({}, {"img_url": None}, {"img_url": ""},
                       {"carousel": ["https://example.com/other.jpg"]}):
            item = to_public({"view": {"values": values}})
            assert item["image"] is None
            assert item["params"] == {}
        assert to_public({})["image"] is None


if __name__ == "__main__":
    unittest.main()


def test_collect_public_ignores_audit_reports(tmp_path):
    """Audit reports beside category snapshots must not become products."""
    import json
    from goodsdex.publish import collect_public
    cats = tmp_path / 'categories'
    cats.mkdir()
    (cats / 'phones.json').write_text(json.dumps([{'product': {'product_id': 'p1'}, 'source': 'mi_cn'}]), encoding='utf-8')
    (cats / 'image-refresh-report.json').write_text(json.dumps([{'id': 'x', 'status': 'added'}]), encoding='utf-8')
    (cats / 'weird.json').write_text(json.dumps(['raw', 3]), encoding='utf-8')
    ids = [r.get('id') for r in collect_public(cats)]
    assert all(isinstance(i, str) and i for i in ids), ids
    assert len(ids) == 1
