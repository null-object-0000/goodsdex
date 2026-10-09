"""价格刷新与发布集测试。

关键教训：价格接口的**调用参数**是从官方 shop JS 里挖出来的，
不是猜的；回灌时的**类型统一**曾导致"全部商品价格变化"的假象。
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex import prices, publish  # noqa: E402


# --------------------------------------------------------------- 接口

def test_fetch_prices_parses_nested_shape():
    """接口返回是嵌套的 {gid: {first: {price: {price: {...}}}}}"""
    fake = {"code": 200, "data": {"123": {"first": {"price": {"price": {
        "price": 1299, "market_price": 1499}}}}}}
    with patch.object(prices.urllib.request, "urlopen") as m:
        m.return_value.__enter__.return_value.read.return_value = \
            json.dumps(fake).encode()
        out = prices.fetch_prices(["123"])
    assert out["123"]["price"] == 1299
    assert out["123"]["market_price"] == 1499


def test_failures_reported_not_silently_empty():
    """请求失败必须显式报错，不能伪装成"没有价格" """
    fake = {"code": 500, "msg": "boom", "data": None}
    with patch.object(prices.urllib.request, "urlopen") as m:
        m.return_value.__enter__.return_value.read.return_value = \
            json.dumps(fake).encode()
        out = prices.fetch_prices(["123"])
    assert "__error__" in out, "失败必须留痕"
    assert "123" not in out


# --------------------------------------------------------------- 发布集

def _rec(pid, name, price, kind="machine", gid="1"):
    return {"product": {"product_id": pid, "name": name, "kind": kind,
                        "category": "测试"},
            "view": {"values": {"price": price, "gid": gid, "总容量": "501L",
                                "carousel": ["x"], "attrs": {"a": 1}}},
            "assertions": [], "captures": [], "fetched_at": "2026-10-09T00:00:00"}


def test_public_view_excludes_display_material():
    """发布集不含展示素材，也不重复顶层字段"""
    d = Path(tempfile.mkdtemp())
    (d / "cats").mkdir()
    (d / "cats" / "t.json").write_text(
        json.dumps([_rec("CN:x:1", "商品A", 100)]), encoding="utf-8")
    meta = publish.build(d / "cats", d / "out")
    items = json.loads((d / "out" / "goods.json").read_text(encoding="utf-8"))
    p = items[0]["params"]
    assert "carousel" not in p and "attrs" not in p, "展示素材不该进发布集"
    assert "price" not in p and "gid" not in p, "顶层已有字段不该在 params 重复"
    assert p.get("总容量") == "501L", "商品属性要保留"
    assert meta["count"] == 1


def test_public_view_keeps_traceability():
    """发布集必须保留可回指证据的字段"""
    d = Path(tempfile.mkdtemp())
    (d / "cats").mkdir()
    (d / "cats" / "t.json").write_text(
        json.dumps([_rec("CN:x:1", "商品A", 100)]), encoding="utf-8")
    publish.build(d / "cats", d / "out")
    it = json.loads((d / "out" / "goods.json").read_text(encoding="utf-8"))[0]
    for k in ("id", "gid", "fetched_at"):
        assert it.get(k), f"发布集缺 {k}，将无法回指证据"


def test_internal_marks_excluded_from_params():
    """下划线开头的内部标记不该出现在 params"""
    d = Path(tempfile.mkdtemp())
    (d / "cats").mkdir()
    r = _rec("CN:x:1", "商品A", 100)
    r["view"]["values"]["_params_empty"] = {}
    (d / "cats" / "t.json").write_text(json.dumps([r]), encoding="utf-8")
    publish.build(d / "cats", d / "out")
    it = json.loads((d / "out" / "goods.json").read_text(encoding="utf-8"))[0]
    assert "_params_empty" not in it["params"]


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
