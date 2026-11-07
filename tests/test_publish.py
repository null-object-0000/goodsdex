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
            item = to_public({"product": {"product_id": "mi-123"}, "view": {"values": values}})
            assert item["image"] is None
            assert item["params"] == {}
        assert to_public({"product": {"product_id": "mi-123"}})["image"] is None


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


def test_iter_category_files_excludes_directory_discovery_and_review_queues(tmp_path):
    """dict 型目录/发现文件与 *-review-queue.json 等非商品快照必须被 iter_category_files 集中排除。"""
    import json
    from goodsdex.publish import collect_public, iter_category_files
    cats = tmp_path / 'categories'
    cats.mkdir()
    (cats / '电视.json').write_text(json.dumps([{'product': {'product_id': 'CN:mi_cn:product:1'}, 'source': 'mi_cn'}]), encoding='utf-8')
    (cats / 'mihome-directory.json').write_text(json.dumps({'schema': 1, 'items': [{'model': 'm1'}]}), encoding='utf-8')
    (cats / 'mihome-discovery.json').write_text(json.dumps({'schema': 1, 'items': []}), encoding='utf-8')
    (cats / 'earbuds-directory.json').write_text(json.dumps({'schema': 1, 'items': []}), encoding='utf-8')
    (cats / 'gap-review-queue.json').write_text(json.dumps([{'model': 'xiaomi.switch.scr2h', 'reason': '整机白名单以外，保留人工审核'}]), encoding='utf-8')
    (cats / 'arbitrary-dict.json').write_text(json.dumps({'not': 'a list'}), encoding='utf-8')

    files = [f.name for f, _ in iter_category_files(cats)]
    assert files == ['电视.json']
    rows = collect_public(cats)
    assert [r['id'] for r in rows] == ['CN:mi_cn:product:1']


def test_to_public_and_collect_public_reject_missing_id_rows(tmp_path):
    """to_public 契约：不允许产出 id=None 的行；collect_public 丢弃缺 id 的残缺行。"""
    import json
    import pytest
    from goodsdex.publish import collect_public, to_public
    from goodsdex.supplements import indexed

    for bad in ({}, {'product': {}}, {'product': {'name': '无ID'}}, {'model': 'x', 'reason': 'audit'}):
        with pytest.raises(ValueError, match='missing product.product_id/variant_id'):
            to_public(bad, source_file='gap-review-queue.json', row_index=0)

    cats = tmp_path / 'categories'
    cats.mkdir()
    (cats / 'mixed.json').write_text(json.dumps([
        {'product': {'product_id': 'CN:mi_cn:product:100', 'name': '正常商品'}},
        {'product': {'name': '缺id商品'}},
        {'model': 'xiaomi.switch.scr2h', 'reason': '整机白名单以外'},
    ]), encoding='utf-8')
    rows = collect_public(cats)
    assert [r['id'] for r in rows] == ['CN:mi_cn:product:100']

    with pytest.raises(ValueError, match=r'rebuilt \(gap-review-queue\.json#0\): missing/duplicate id: None'):
        indexed([{'id': None, '_source_file': 'gap-review-queue.json', '_source_row': 0}], 'rebuilt')
