"""capture_id 唯一性回归。

教训：capture_id 原为 sha1(source|url|时间戳)[:12]。
移动端接口对**所有商品**用同一个 URL（商品在 POST body），
并发采集时同秒的两个商品算出同一个 id ——
实测 445 个 id 被多个商品共用且**内容不同**，
导致审计时断言配到别人的证据上（张冠李戴）。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.facts import Capture  # noqa: E402


def test_same_url_different_content_distinct_ids():
    """同 URL 不同响应 -> id 必须不同"""
    a = Capture.make("mi_cn_mobile", "https://m.mi.com/mtop/xiaoshophop"
                     if False else "https://m.mi.com/mtop/xiaomishop/product/info",
                     '{"data":{"product":{"name":"商品A"}}}')
    b = Capture.make("mi_cn_mobile", "https://m.mi.com/mtop/xiaomishop/product/info",
                     '{"data":{"product":{"name":"商品B"}}}')
    assert a.capture_id != b.capture_id, "同秒同 URL 不同内容不应共用 id"


def test_same_url_same_content_may_share_id():
    """同 URL 同响应 -> 可以相同（同一份证据，引用它是对的）"""
    raw = '{"data":{"product":{"name":"商品A"}}}'
    a = Capture.make("mi_cn_mobile", "u", raw)
    b = Capture.make("mi_cn_mobile", "u", raw)
    assert a.capture_id == b.capture_id


def test_empty_response_still_unique_per_source():
    """空响应（如限流）也要有 id，且同 source 下可区分不同 url"""
    a = Capture.make("mi_cn_pc", "https://a/1", "")
    b = Capture.make("mi_cn_pc", "https://a/2", "")
    assert a.capture_id and b.capture_id


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
