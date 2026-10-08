"""多型号拆分测试

依据全部来自实测（冰箱 / 洗衣机 / 显示器），不是推测：
  - 「米家冰箱 三门系列」一个 product_id 覆盖 5 个型号
  - 接口只给一份参数，无法自动归属到具体子型号
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.multi_model import (is_model_tab, is_multi_model, split_category,
                                  split_record)


# ---------- 型号 tab 识别 ----------

def test_model_tab_detected():
    """tab 名是具体型号（含容量/门体/规格词）"""
    assert is_model_tab("256L(星锻银)")
    assert is_model_tab("271L(全域离子净化)")
    assert is_model_tab("直冷-186L")
    assert is_model_tab("风冷-216L")
    assert is_model_tab("微冰鲜-十字门")
    assert is_model_tab("十字-513L")


def test_generic_tab_not_model():
    """通用名与服务类 tab 不是型号"""
    for n in ("规格参数", "产品参数", "商品详情", "售后服务", "安装须知",
              "服务条款", "包装清单", "常见问题", ""):
        assert not is_model_tab(n), f"{n} 不该被判为型号 tab"


def test_real_tab_names_from_data():
    """实测名字逐一对上"""
    real_models = ["256L(星锻银)", "271L(全域离子净化)", "215L", "风冷-216L",
                   "直冷-216L", "直冷-185L", "直冷-186L（一级能效）",
                   "十字-508L-冰羽白（金属）", "法式-508L-星缎银（玻璃）",
                   "610L", "501L", "430L 2026款", "只换不修服务条款"]
    for n in real_models:
        expected = n != "只换不修服务条款"
        assert is_model_tab(n) == expected, f"{n} 判定错误"


# ---------- 拆分 ----------

def _rec_with_tabs(tabs, vision_by_tab=None, iface_params=None):
    """构造一条最小记录（含 PC 原始响应 + 视觉断言）"""
    raw = json.dumps({"data": {"extend_info": {"desc_tabs_view": [
        {"name": n, "tab_content": [{"plain_view": {"img": f"http://x/{i}.jpg"}}]}
        for i, n in enumerate(tabs)]}}}, ensure_ascii=False)
    asserts = []
    for ti, items in (vision_by_tab or {}).items():
        for k, v in items.items():
            asserts.append({
                "assertion_id": f"a{ti}{k}", "subject_id": "p", "capture_id": "c",
                "source": "mi_cn_pc_vision", "attribute": k, "raw_value": v,
                "locator": f"$.data.extend_info.desc_tabs_view[{ti}].tab_content[0].plain_view.img",
                "ui_location": "规格参数", "page": "PC", "parser_version": "v1"})
    vals = dict(iface_params or {})
    return {
        "product": {"product_id": "CN:mi_cn:product:100", "name": "测试系列",
                    "kind": "machine", "variants": []},
        "captures": [{"source": "mi_cn_pc", "status": "success",
                      "response_raw": raw}],
        "assertions": asserts,
        "view": {"values": vals},
        "market_prices": [], "discovery": {}, "fetched_at": "2026-10-08",
    }


def test_single_model_not_split():
    """单型号条目不该被拆"""
    r = _rec_with_tabs(["商品详情", "规格参数"])
    ok, tabs = is_multi_model(r)
    assert not ok
    kids, st = split_record(r)
    assert kids == []


def test_multi_model_split():
    """多型号条目要拆成对应条数"""
    r = _rec_with_tabs(["商品详情", "256L(星锻银)", "271L(全域离子净化)", "215L"],
                       vision_by_tab={1: {"产品型号": "MC-256WTMPN", "总容积": "256L"},
                                      2: {"产品型号": "MC-271WTMPN", "总容积": "271L"}})
    ok, tabs = is_multi_model(r)
    assert ok and len(tabs) == 3
    kids, st = split_record(r)
    assert len(kids) == 3
    assert st["children"] == 3


def test_model_code_from_vision():
    """型号标识优先用视觉提取出的「产品型号」"""
    r = _rec_with_tabs(["256L(星锻银)", "271L(全域离子净化)"],
                       vision_by_tab={0: {"产品型号": "MC-256WTMPN"},
                                      1: {"产品型号": "MC-271WTMPN"}})
    kids, _ = split_record(r)
    codes = {k["product"]["model_code"] for k in kids}
    assert codes == {"MC-256WTMPN", "MC-271WTMPN"}


def test_model_code_fallback_to_tab():
    """没提取到型号时退回用 tab 名（不能留空）"""
    r = _rec_with_tabs(["256L(星锻银)", "271L(全域离子净化)"])
    kids, _ = split_record(r)
    names = {k["product"]["name"] for k in kids}
    assert "256L(星锻银)" in names and "271L(全域离子净化)" in names


def test_children_link_to_parent():
    """子记录必须能回溯到父记录"""
    r = _rec_with_tabs(["256L(星锻银)", "271L(全域离子净化)"])
    kids, _ = split_record(r)
    for k in kids:
        assert k["product"]["parent_product_id"] == "CN:mi_cn:product:100"
        assert k["product"]["is_model_child"] is True
        assert k["product"]["product_id"].startswith("CN:mi_cn:product:100#tab")


def test_assertions_stay_with_their_tab():
    """每个型号的断言必须留在自己的子记录里，不能串台"""
    r = _rec_with_tabs(["256L(星锻银)", "271L(全域离子净化)"],
                       vision_by_tab={0: {"总容积": "256L"}, 1: {"总容积": "271L"}})
    kids, _ = split_record(r)
    by = {k["product"]["model_code"] or k["product"]["name"]: k for k in kids}
    for k in kids:
        vals = [a["raw_value"] for a in k["assertions"] if a["attribute"] == "总容积"]
        if k["product"]["name"] == "256L(星锻银)":
            assert vals == ["256L"], "子记录只能有自己的断言"
        else:
            assert vals == ["271L"]


def test_interface_params_not_assigned():
    """接口参数不能硬塞给子记录（实测：接口只给一份，归属不明）"""
    r = _rec_with_tabs(["256L(星锻银)", "271L(全域离子净化)"],
                       iface_params={"总容量": "256L", "噪音值": "36dB"})
    kids, st = split_record(r)
    # 子记录里不应出现接口参数
    for k in kids:
        attrs = {a["attribute"] for a in k["assertions"]}
        assert "总容量" not in attrs, "接口参数不该被塞进子记录"
        assert "噪音值" not in attrs
    # 但统计里要标明存在未归属的接口参数
    assert st["interface_params_ambiguous"] is True


def test_split_category_counts():
    """整类拆分统计"""
    rs = [_rec_with_tabs(["规格参数"]),
          _rec_with_tabs(["256L(星锻银)", "271L(全域离子净化)"])]
    out, st = split_category(rs)
    assert st["total"] == 2
    assert st["split"] == 1
    assert st["children"] == 2
    assert len(out) == 3          # 1 条未拆 + 2 条子记录


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn(); print(f"  ✓ {fn.__name__}"); ok += 1
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(fns)} 通过")
