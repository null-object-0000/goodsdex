"""采集失败语义测试（离线，用 mock）

Codex 评审指认的三处"失败装成成功"：
  1. 搜索业务错误 {code:500,data:{total:57}} 被判为 no_sellable_items
     —— 即"接口报错"装成"官方没有在售"
  2. 熔断阈值实际是"累计 5 次"而非"连续 5 次"（成功后不清零）
  3. 响应缺字段（schema 变化）被当成正常空结果

本项目核心承诺是"区分没抓到和官方没有"，这些测试守住它。
"""
import os
import sys
import urllib.error
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.sources import mi_cn


def test_success_code_200_accepted():
    """小米接口成功码是 200（不是 0）—— 曾把成功当失败

    这个 bug 导致全库重采返回 0 款。测试必须覆盖**真实契约**，
    而不是我臆想的约定。
    """
    payload = 'cb({"code":200,"msg":"success","data":{"total":21,"pc_list":[]}})'
    with patch.object(mi_cn, "_get", return_value=payload):
        d = mi_cn.enumerate_products("x", pause=0)["discovery"]
    assert d["completeness"] == "no_sellable_items", \
        f"code=200 是成功，应识别为无在售商品而非失败（实际 {d['completeness']}）"
    assert d["total_reported"] == 21


def test_api_error_not_reported_as_empty():
    """接口业务错误必须报 failed，不能装成"没有在售" """
    payload = 'cb({"code":500,"data":{"total":57}})'
    with patch.object(mi_cn, "_get", return_value=payload):
        d = mi_cn.enumerate_products("x", pause=0)["discovery"]
    assert d["completeness"] == "failed", \
        f"接口报错应为 failed，实际 {d['completeness']}"
    assert d["stop_reason"].startswith("api_error")


def test_schema_error_detected():
    """响应缺少 pc_list 字段（官方改版）必须报 failed"""
    with patch.object(mi_cn, "_get", return_value='cb({"code":0,"data":{}})'):
        d = mi_cn.enumerate_products("x", pause=0)["discovery"]
    assert d["completeness"] == "failed"
    assert "schema_error" in d["stop_reason"]


def test_unparseable_response_detected():
    """非 JSONP 响应必须报 failed，不能静默当成空结果"""
    with patch.object(mi_cn, "_get", return_value="<html>502 Bad Gateway</html>"):
        d = mi_cn.enumerate_products("x", pause=0)["discovery"]
    assert d["completeness"] == "failed"


def test_genuine_empty_still_distinguished():
    """真正的空结果（能返回 total 与空 pc_list）仍标 no_sellable_items"""
    with patch.object(mi_cn, "_get",
                      return_value='cb({"code":0,"data":{"total":57,"pc_list":[]}})'):
        d = mi_cn.enumerate_products("x", pause=0)["discovery"]
    assert d["completeness"] == "no_sellable_items", \
        "真·无在售与接口失败必须区分"
    assert d["total_reported"] == 57


def test_breaker_counts_consecutive_not_cumulative():
    """熔断判据是"连续"失败，成功后应清零"""
    mi_cn.reset_breaker()
    err = urllib.error.HTTPError("u", 429, "too many", None, None)
    with patch.object(mi_cn, "_get", side_effect=err):
        for _ in range(3):
            mi_cn.fetch_pc("1")
    assert mi_cn.breaker_status()["fails"] == 3
    assert not mi_cn.breaker_status()["tripped"], "3 次未达阈值不应开路"
    # 成功一次 -> 清零
    with patch.object(mi_cn, "_get", return_value='{"code":200,"data":{}}'):
        mi_cn.fetch_pc("1")
    st = mi_cn.breaker_status()
    assert st["fails"] == 0, "成功后必须清零（否则是累计而非连续）"
    assert not st["tripped"]
    mi_cn.reset_breaker()


def test_breaker_trips_on_consecutive():
    """连续 429 达阈值应开路"""
    mi_cn.reset_breaker()
    err = urllib.error.HTTPError("u", 429, "too many", None, None)
    with patch.object(mi_cn, "_get", side_effect=err):
        for _ in range(mi_cn.PC_BREAKER_THRESHOLD):
            mi_cn.fetch_pc("1")
    assert mi_cn.breaker_status()["tripped"], "达阈值应开路"
    # 开路后不再尝试请求
    caps, _ = mi_cn.fetch_pc("1")
    assert any(c.status.value == "rate_limited" for c in caps)
    mi_cn.reset_breaker()


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
