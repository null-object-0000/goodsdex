"""只有完整枚举且实际采集完成，才能用缺席更新档案。"""
import json
from unittest.mock import patch

import pytest

from goodsdex import pipeline
from goodsdex.archive import merge_archive


def rec(pid):
    return {"product": {"product_id": pid, "name": pid, "kind": "unknown"},
            "view": {"values": {}}, "captures": [], "assertions": []}


def read_archive(tmp_path):
    return json.loads((tmp_path / "archive" / "测试.json").read_text())


@pytest.mark.parametrize("completeness,reason,limit,fail,expected_missing", [
    ("complete", "reached_total", 0, False, True),
    ("partial", "max_pages_reached", 0, False, False),
    ("no_sellable_items", "no_sellable_items", 0, False, False),
    ("failed", "api_error: code=500", 0, False, False),
    ("unknown", "empty_page", 0, False, False),
    ("complete", "reached_total", 1, False, False),
    ("complete", "reached_total", 0, True, False),
])
def test_pipeline_only_marks_missing_after_complete_collection(
        tmp_path, completeness, reason, limit, fail, expected_missing):
    merge_archive("测试", [rec("A"), rec("B")], archive_dir=tmp_path / "archive")
    items = [{"pid": p, "name": p} for p in ["A", "C"]]
    discovery = {"completeness": completeness, "stop_reason": reason,
                 "total_reported": 2, "found": 2}

    def collect(pid, *args):
        if fail and pid == "C":
            raise RuntimeError("详情采集失败")
        return rec(pid)

    with patch.object(pipeline.mi_cn, "list_categories", return_value={}), \
         patch.object(pipeline.mi_cn, "enumerate_products", return_value={
             "items": items, "discovery": discovery}), \
         patch.object(pipeline, "collect_one", side_effect=collect):
        pipeline.run_category("测试", limit=limit, outdir=tmp_path / "categories",
                              verbose=False)
    arch = read_archive(tmp_path)
    assert bool(arch["items"]["B"].get("missing_since")) == expected_missing
    if not expected_missing:
        assert arch["last_incomplete_at"]
        assert arch["last_incomplete_reason"]
        assert arch["missing"] == 0


@pytest.mark.parametrize("discovery", [
    None,
    {"completeness": "complete", "stop_reason": "no_new_items", "total_reported": 2, "found": 2},
    {"completeness": "complete", "stop_reason": "max_pages_reached", "total_reported": 2, "found": 2},
    {"completeness": "complete", "stop_reason": "no_sellable_items", "total_reported": 2, "found": 2},
    {"completeness": "complete", "stop_reason": "reached_total", "total_reported": 2, "found": 1},
    {"completeness": "complete", "stop_reason": "reached_total", "found": 1},
])
def test_archive_requires_positive_coverage_evidence(tmp_path, discovery):
    d = tmp_path / "archive"
    merge_archive("测试", [rec("A"), rec("B")], archive_dir=d)
    st = merge_archive("测试", [rec("A")], archive_dir=d, discovery=discovery)
    arch = read_archive(tmp_path)
    assert "missing_since" not in arch["items"]["B"]
    assert st["went_missing"] == 0
    assert arch["present"] == 2 and arch["missing"] == 0
    assert arch["last_incomplete_at"]


def test_partial_updates_seen_preserves_unseen_and_revives(tmp_path):
    d = tmp_path / "archive"
    merge_archive("测试", [rec("A"), rec("B"), rec("C")], archive_dir=d)
    merge_archive("测试", [], archive_dir=d, discovery={
        "completeness": "complete", "stop_reason": "empty_page", "total_reported": 0, "found": 0})
    before = read_archive(tmp_path)
    r = rec("A")
    r["view"]["values"]["price"] = 88
    st = merge_archive("测试", [r], archive_dir=d, now_iso="2026-10-15T12:00:00+08:00",
                       discovery={"completeness": "partial", "stop_reason": "max_pages_reached"})
    arch = read_archive(tmp_path)
    assert arch["items"]["B"] == before["items"]["B"]
    assert arch["items"]["C"] == before["items"]["C"]
    assert "missing_since" not in arch["items"]["A"]
    assert arch["items"]["A"]["price"] == 88
    assert st["revived"] == 1 and st["went_missing"] == 0
    assert arch["missing"] == 2 and arch["present"] == 1
    merge_archive("测试", [r], archive_dir=d, discovery={
        "completeness": "complete", "stop_reason": "reached_total", "total_reported": 1, "found": 1})
    assert read_archive(tmp_path)["last_incomplete_at"] == "2026-10-15T12:00:00+08:00"


@pytest.mark.parametrize("completeness,reason,total", [
    ("failed", "api_error: code=500", None),
    ("unknown", "empty_page", None),
    ("no_sellable_items", "no_sellable_items", 55),
    ("complete", "empty_page", 0),
])
def test_empty_observation_records_coverage_even_when_snapshot_preserved(
        tmp_path, completeness, reason, total):
    merge_archive("测试", [rec("A")], archive_dir=tmp_path / "archive")
    cats = tmp_path / "categories"
    cats.mkdir()
    fp = cats / "测试.json"
    fp.write_text(json.dumps([rec("A")]))
    old = fp.read_text()
    with patch.object(pipeline.mi_cn, "list_categories", return_value={}), \
         patch.object(pipeline.mi_cn, "enumerate_products", return_value={
             "items": [], "discovery": {"completeness": completeness, "stop_reason": reason,
                                        "total_reported": total, "found": 0}}):
        pipeline.run_category("测试", outdir=cats, verbose=False)
    arch = read_archive(tmp_path)
    assert bool(arch["items"]["A"].get("missing_since")) == (completeness == "complete")
    if completeness != "complete":
        assert arch["last_incomplete_reason"] == reason
    if completeness in ("failed", "unknown"):
        assert fp.read_text() == old


def test_failed_container_child_cannot_mark_missing(tmp_path):
    pid = "CN:mi_cn:product:child"
    merge_archive("测试", [rec(pid)], archive_dir=tmp_path / "archive")

    def collect(product_id, *args):
        if product_id == "child":
            raise RuntimeError("子商品采集失败")
        r = rec("container")
        r["product"].update(is_container=True, container_children=["child"])
        return r

    with patch.object(pipeline.mi_cn, "list_categories", return_value={}), \
         patch.object(pipeline.mi_cn, "enumerate_products", return_value={
             "items": [{"pid": "container", "name": "container"}], "discovery": {
                 "completeness": "complete", "stop_reason": "reached_total",
                 "total_reported": 1, "found": 1}}), \
         patch.object(pipeline, "collect_one", side_effect=collect):
        pipeline.run_category("测试", outdir=tmp_path / "categories", verbose=False)
    arch = read_archive(tmp_path)
    assert "missing_since" not in arch["items"][pid]
    assert arch["last_incomplete_reason"] == "collection_failed"
