"""「官方已下架」必须与「查错了」严格区分。

实测的官方返回码（不靠猜）：
  code=400480502  msg="该产品已下架"   -> DELISTED
  code=400480400  msg="请求参数非法"   -> NOT_FOUND（ID 无效/格式错）
  code=0          msg="ok"            -> 正常

为什么必须分开：
  DELISTED 是**有效结论** —— 商品存在过、官方已撤下，规格不可得。
    用户问"我这台该不该换"时，答案是"你这款已下架，官方规格已删除"。
  NOT_FOUND 说明**我们查错了**（ID 写错）。
  混为一谈会把"官方下架"说成"我们抓错了"，或把无效 ID
  当成"官方没有这个产品" —— 正是本项目最要避免的自欺。
"""
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.facts import CaptureStatus  # noqa: E402
from goodsdex.sources import mi_cn  # noqa: E402


def _resp(code, msg):
    import json
    return json.dumps({"code": code, "message": msg})


def test_delisted_distinguished_from_not_found():
    """下架 vs 参数非法 —— 两种返回都要各自归对"""
    with patch.object(mi_cn, "_mtop_call",
                      return_value=(_j(400480502, "该产品已下架"),
                                    '{"code":400480502}', 200, None)):
        caps, _ = mi_cn.fetch_mobile("13363")
    assert caps[0].status is CaptureStatus.DELISTED, caps[0].status

    with patch.object(mi_cn, "_mtop_call",
                      return_value=(_j(400480400, "请求参数非法"),
                                    '{"code":400480400}', 200, None)):
        caps, _ = mi_cn.fetch_mobile("bogus")
    assert caps[0].status is CaptureStatus.NOT_FOUND, caps[0].status


def test_delisted_is_valid_conclusion_not_error():
    """下架是结论，不该被当成普通业务错误"""
    with patch.object(mi_cn, "_mtop_call",
                      return_value=(_j(400480502, "该产品已下架"),
                                    '{"code":400480502}', 200, None)):
        caps, _ = mi_cn.fetch_mobile("13363")
    assert caps[0].status is not CaptureStatus.SOURCE_ERROR
    assert "已下架" in (caps[0].error or "")


def test_other_errors_stay_source_error():
    """未知业务码仍是 source_error —— 不能什么都往"下架"上靠"""
    with patch.object(mi_cn, "_mtop_call",
                      return_value=(_j(500, "服务器开小差"),
                                    '{"code":500}', 200, None)):
        caps, _ = mi_cn.fetch_mobile("9726")
    assert caps[0].status is CaptureStatus.SOURCE_ERROR


def test_transport_error_unchanged():
    """网络错误仍是 transport_error"""
    with patch.object(mi_cn, "_mtop_call",
                      return_value=({}, "", 0, "timeout")):
        caps, _ = mi_cn.fetch_mobile("9726")
    assert caps[0].status is CaptureStatus.TRANSPORT_ERROR


def test_real_delisted_product():
    """实测：全能扫拖机器人2（13363）官方确认为已下架"""
    try:
        caps, _ = mi_cn.fetch_mobile("13363")
    except Exception as e:
        print(f"    (跳过：{type(e).__name__})")
        return
    assert caps[0].status is CaptureStatus.DELISTED, \
        f"13363 应为 delisted，实际 {caps[0].status}"


def _j(code, msg):
    return {"code": code, "message": msg}


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
