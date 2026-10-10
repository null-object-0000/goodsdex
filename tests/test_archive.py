"""档案累积：下架不丢、复活可辨、并入幂等。

这是"持续积累"的核心保障 —— 原实现整分类覆盖，下架商品会被永久丢失。
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.archive import archive_stats, merge_archive  # noqa: E402


def _rec(pid, name, price=100):
    return {"product": {"product_id": pid, "name": name, "kind": "machine"},
            "view": {"values": {"price": price, "gid": "1", "总容量": "501L"}},
            "assertions": [], "captures": []}


def test_delisted_product_is_kept():
    """下架商品必须留在档案里 —— 这是核心目标"""
    d = Path(tempfile.mkdtemp())
    merge_archive("测试", [_rec("A", "商品A"), _rec("B", "商品B")],
                  archive_dir=d, now_iso="2026-10-01T00:00:00+08:00")
    # B 下架：下次采集只有 A
    st = merge_archive("测试", [_rec("A", "商品A")],
                       archive_dir=d, now_iso="2026-10-02T00:00:00+08:00")
    arch = json.loads((d / "测试.json").read_text(encoding="utf-8"))
    assert "B" in arch["items"], "下架商品被丢弃了"
    assert arch["items"]["B"]["missing_since"], "应标记缺席时刻"
    assert st["went_missing"] == 1
    assert st["present"] == 1 and st["total"] == 2


def test_price_updates_on_reseen():
    """重新见到要刷新最新值，且累积见到次数"""
    d = Path(tempfile.mkdtemp())
    merge_archive("测试", [_rec("A", "商品A", 100)], archive_dir=d,
                  now_iso="2026-10-01T00:00:00+08:00")
    merge_archive("测试", [_rec("A", "商品A", 88)], archive_dir=d,
                  now_iso="2026-10-02T00:00:00+08:00")
    arch = json.loads((d / "测试.json").read_text(encoding="utf-8"))
    a = arch["items"]["A"]
    assert a["price"] == 88, "价格应更新为最新"
    assert a["times_seen"] == 2
    assert a["first_seen_at"].startswith("2026-10-01")
    assert a["last_seen_at"].startswith("2026-10-02")


def test_revived_product_clears_missing():
    """曾缺席又出现 = 复活，要清掉缺席标记"""
    d = Path(tempfile.mkdtemp())
    merge_archive("测试", [_rec("A", "A")], archive_dir=d,
                  now_iso="2026-10-01T00:00:00+08:00")
    merge_archive("测试", [], archive_dir=d,
                  now_iso="2026-10-02T00:00:00+08:00")     # A 消失
    st = merge_archive("测试", [_rec("A", "A")], archive_dir=d,
                       now_iso="2026-10-03T00:00:00+08:00")  # A 回来
    arch = json.loads((d / "测试.json").read_text(encoding="utf-8"))
    assert not arch["items"]["A"].get("missing_since"), "复活后不该还标缺席"
    assert st["revived"] == 1


def test_merge_is_idempotent_for_same_batch():
    """同一批重复并入不改变商品数（时间戳除外）"""
    d = Path(tempfile.mkdtemp())
    merge_archive("测试", [_rec("A", "A"), _rec("B", "B")], archive_dir=d,
                  now_iso="2026-10-01T00:00:00+08:00")
    merge_archive("测试", [_rec("A", "A"), _rec("B", "B")], archive_dir=d,
                  now_iso="2026-10-01T00:00:00+08:00")
    st = archive_stats(d)
    assert st["total"] == 2, f"重复并入导致 {st['total']} 条"


def test_archive_never_shrinks():
    """档案只增不减 —— 这是"持续积累"的定义"""
    d = Path(tempfile.mkdtemp())
    counts = []
    for i in range(5):
        recs = [_rec(f"P{j}", f"商品{j}") for j in range(i + 1)]
        merge_archive("测试", recs, archive_dir=d,
                      now_iso=f"2026-10-0{i+1}T00:00:00+08:00")
        counts.append(archive_stats(d)["total"])
    assert counts == sorted(counts), f"档案数量出现缩减: {counts}"
    assert counts[-1] == 5


def test_archive_is_slim():
    """档案不含原始证据（体量大、可重采），只留可对比字段"""
    d = Path(tempfile.mkdtemp())
    r = _rec("A", "A")
    r["captures"] = [{"capture_id": "x", "response_raw": "y" * 10000}]
    r["view"]["values"]["carousel"] = ["img1", "img2"]
    merge_archive("测试", [r], archive_dir=d, now_iso="2026-10-01T00:00:00+08:00")
    arch = json.loads((d / "测试.json").read_text(encoding="utf-8"))
    a = arch["items"]["A"]
    assert "captures" not in a
    assert "carousel" not in a["params"], "展示素材不该进档案"
    assert a["params"].get("总容量") == "501L", "商品属性要保留"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
    print(f"\n{ok}/{len(fns)} 通过")
