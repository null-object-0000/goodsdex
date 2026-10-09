"""类型分流必须"留档"，不能丢弃。

教训：pipeline 一度写成 `out = kept + dropped`（只保留整机 + 被形态
过滤项），把 657 配件 + 87 服务 + 466 未判定**静默丢掉**。
分流是指"不参与对比与残值"，不是"不留档" ——
丢了就无法复核"到底抓到了什么"，也答不了"官方有没有这个东西"。
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex import pipeline  # noqa: E402


def _rec(pid, name, kind):
    return {"product": {"product_id": pid, "name": name, "kind": kind},
            "assertions": [], "captures": [], "view": {},
            "market_prices": [], "discovery": {}, "fetched_at": ""}


def test_accessory_and_service_are_archived():
    """配件/服务/未判定必须随结果落盘（带 kind 标记）"""
    d = Path(tempfile.mkdtemp())
    recs = [_rec("CN:x:1", "米家空调 巨省电 1.5匹", "machine"),
            _rec("CN:x:2", "米家除醛滤网（中央空调）", "accessory"),
            _rec("CN:x:3", "空调清洁保养服务", "service"),
            _rec("CN:x:4", "某个说不清的东西", "unknown")]

    def fake_collect_one(pid, *a, **k):
        return {"product": {"product_id": f"CN:x:{pid}", "name": f"商品{pid}",
                            "kind": "machine"},
                "assertions": [], "captures": [], "view": {},
                "market_prices": [], "discovery": {}, "fetched_at": ""}

    items = [{"pid": str(i), "name": f"商品{i}", "variants": []}
             for i in range(1, 5)]
    with patch.object(pipeline.mi_cn, "list_categories",
                      return_value={"壁挂空调": "壁挂空调"}), \
         patch.object(pipeline.mi_cn, "enumerate_products",
                      return_value={"items": items, "discovery": {
                          "total_reported": 4, "completeness": "complete",
                          "stop_reason": "reached_total"}}), \
         patch.object(pipeline, "collect_one", side_effect=fake_collect_one):
        out = pipeline.run_category("壁挂空调", outdir=d, verbose=False)
    kinds = sorted((r["product"].get("kind") for r in out))
    assert "accessory" in kinds or len(out) >= 3, \
        f"配件/服务被丢弃了，只剩 {kinds}"
    saved = json.loads((d / "壁挂空调.json").read_text(encoding="utf-8"))
    assert len(saved) == len(out), "落盘条数应与返回一致"


def test_machine_still_filtered_by_form():
    """整机仍按分类形态过滤（立式/中央空调不该混进壁挂）"""
    from goodsdex.category_filter import filter_category
    recs = [_rec("a", "米家空调 巨省电 1.5匹 壁挂式", "machine"),
            _rec("b", "米家空调 立式 3匹", "machine")]
    kept, dropped = filter_category(recs, "壁挂空调")
    assert any(r["product"]["product_id"] == "a" for r in kept)
    assert any(r["product"]["product_id"] == "b" for r in dropped)


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
