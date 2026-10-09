"""选图策略测试

背景（真实踩过的坑）：
  用"排除服务类 tab"的排除法选规格图，导致全库 23197 张候选里
  16516 张（71%）来自 tab='商品详情' —— 营销图。
  后果：把「全面升级」「10年免费包修」当成产品参数提取。
  这是"数据错误比数据缺失更危险"的直接案例。
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from vision_params import GENERIC_TAB, NON_SPEC_TAB, SPEC_TAB, find_spec_images


def _rec(tabs):
    """构造含 PC 原始响应的记录"""
    raw = json.dumps({"data": {"extend_info": {"desc_tabs_view": [
        {"name": n, "tab_content": [{"plain_view": {"img": f"http://x/{i}.jpg"}}]}
        for i, n in enumerate(tabs)]}}}, ensure_ascii=False)
    return {"captures": [{"source": "mi_cn_pc", "status": "success",
                          "response_raw": raw}]}


# ---------- 营销 tab 必须排除 ----------

def test_marketing_tabs_excluded():
    """商品详情等营销 tab 不能选（曾经的主要错误来源）"""
    for t in ("商品详情", "产品详情", "图文介绍", "用户评价", "售后服务",
              "安装须知", "包装清单"):
        assert NON_SPEC_TAB.search(t), f"{t} 应被排除"
        r = _rec([t])
        assert find_spec_images(r) == [], f"{t} 不该产出候选图"


def test_marketing_not_selected_in_mix():
    """混有营销 tab 时，只取参数 tab"""
    r = _rec(["商品详情", "规格参数", "售后服务"])
    got = find_spec_images(r)
    assert len(got) == 1
    assert got[0]["tab_name"] == "规格参数"


# ---------- 参数 tab 白名单 ----------

def test_spec_tabs_tier1():
    """名副其实的参数 tab 是第一优先"""
    for t in ("产品参数", "商品参数", "规格参数", "参数页", "参数"):
        assert SPEC_TAB.search(t), f"{t} 应被识别为参数 tab"
        got = find_spec_images(_rec([t]))
        assert len(got) == 1 and got[0]["tier"] == 1


def test_model_tabs_tier2():
    """型号命名 tab 是第二优先（家电按型号分栏）"""
    for t in ("256L(星锻银)", "直冷-186L", "微冰鲜-十字门", "十字-513L",
              "DD直驱款 米家洗衣机滚筒10kg"):
        got = find_spec_images(_rec([t]))
        assert len(got) == 1, f"{t} 应被选中"
        assert got[0]["tier"] == 2, f"{t} 应是 tier2"


def test_display_spec_not_model():
    """回归：显示器的规格描述不能被当成型号名

    Codex 评审指认：tier2 用"非通用名即为型号"的排除法，
    把 "27英寸 4K Type-C接口" / "1080P 144Hz" / "4K 60Hz Type-C版"
    当成型号 —— 而且同一款有多种表述，会导致重复条目。
    """
    for t in ("27英寸 4K  Type-C接口", "1080P 144Hz", "4K 60Hz Type-C版",
              "32英寸 4K Type-C接口", "4K 双模刷新率", "1080P 100Hz"):
        got = find_spec_images(_rec([t]))
        assert got == [], f"{t} 是规格描述，不该被当作型号 tab"


def test_real_model_tabs_still_match():
    """真型号 tab 仍要能识别（白名单不能太窄）"""
    for t in ("法式-508L-冰羽白（金属）", "DD直驱款 米家洗衣机滚筒10kg",
              "256L(星锻银)", "直冷-186L", "微冰鲜-法式门", "十字508L",
              "标准款DD直驱变频 洗烘10kg银灰"):
        got = find_spec_images(_rec([t]))
        assert len(got) == 1, f"{t} 应被识别为型号 tab"
        assert got[0]["tier"] == 2


def test_generic_tab_not_model():
    """通用 tab 名不该被当成型号 tab"""
    for t in ("详情", "介绍", "商品详情", "包装清单"):
        assert GENERIC_TAB.search(t), f"{t} 应被识别为通用 tab"


# ---------- 无名字的 tab ----------

def test_empty_name_tab_skipped():
    """无名字 tab 不取（实测多为 banner，不是参数表）"""
    got = find_spec_images(_rec([""]))
    assert got == []


# ---------- 分层结果 ----------

def test_tier_ordering():
    """同时有参数 tab 和型号 tab 时，两者都取且分层正确"""
    r = _rec(["商品详情", "规格参数", "256L(星锻银)"])
    got = find_spec_images(r)
    tiers = sorted(g["tier"] for g in got)
    assert tiers == [1, 2], "参数 tab 与型号 tab 都要保留"
    names = {g["tab_name"] for g in got}
    assert names == {"规格参数", "256L(星锻银)"}


def test_no_pc_capture():
    """没有 PC 原始响应时返回空，不报错"""
    assert find_spec_images({}) == []
    assert find_spec_images({"captures": []}) == []


def test_reported_counts():
    """回归：修正后全库候选图应大幅减少（薄荷 71% 的营销图）"""
    import glob
    root = os.path.join(os.path.dirname(__file__), "..")
    catdir = os.path.join(root, "data", "categories")
    if not os.path.isdir(catdir):
        return                      # 数据不在时跳过
    total = tier1 = tier2 = 0
    for f in glob.glob(os.path.join(catdir, "*.json")):
        try:
            recs = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for r in recs:
            if (r.get("product") or {}).get("kind") != "machine":
                continue
            for im in find_spec_images(r):
                total += 1
                if im["tier"] == 1:
                    tier1 += 1
                else:
                    tier2 += 1
    if total:
        # 修正前是 23197；关键在于营销图占比应接近 0
        assert total < 12000, f"候选图仍过多({total})，疑似混入营销 tab"
        assert tier1 > 0 and tier2 > 0


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
