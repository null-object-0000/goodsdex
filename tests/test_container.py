"""容器展开：系列页里的多个独立商品必须各自成记录。

背景：官方对一个"系列"productId（如「米家冰箱 对开门系列」）返回的
goodsList 装着若干**独立商品**（不同容量的冰箱），各自可独立采集、
参数完整。原实现只解析 goodsList[0]，导致：

  ① 容器记录名实不符 —— 名字是系列名，price/参数却来自 goodsList[0]
     （那是**另一个商品**的数据）
  ② 其余型号全部漏采 —— 实测 54 个容器（冰箱14/显示器6/吹风机…）

判据（实测 724 个整机抽样）：
  自指  goodsList[0].productId == 自己 -> 列表是自己的 SKU 变体
        （如手机的不同存储/颜色），[0] 用法正确 —— 666 个
  非自指 goodsList[0].productId != 自己 -> 容器，需展开 —— 54 个
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.sources import mi_cn  # noqa: E402


def _children_of(pid):
    caps, ass = mi_cn.fetch_mobile(pid)
    for a in ass:
        if a.attribute == "_container_children":
            return list(a.raw_value)
    return []


def test_series_container_detected():
    """系列容器必须被识别出子商品列表"""
    kids = _children_of("10050151")     # 米家冰箱 对开门系列
    assert kids, "对开门系列应识别为容器"
    assert all(str(k).isdigit() for k in kids)


def test_selfref_product_not_container():
    """自指商品不得误判为容器"""
    kids = _children_of("19432")        # Redmi K70（自指，goodsList 是自己的SKU）
    assert not kids, f"Redmi K70 不该被判为容器，得到 {kids}"


def test_container_child_is_selfref():
    """容器的子商品应当自指（自己有名字、参数完整）"""
    for cid in _children_of("10050151")[:3]:
        caps, ass = mi_cn.fetch_mobile(cid)
        assert caps[0].status.value == "success", f"{cid} 采集失败"
        names = [a.raw_value for a in ass if a.attribute == "name"]
        assert names and names[0], f"{cid} 应有自己的名字"
        params = [a for a in ass
                  if "classParameters.list[" in (a.locator or "")]
        assert params, f"{cid} 应有参数"
        # 子商品不应再是容器
        assert not _children_of(cid), f"{cid} 不该又是容器"


def test_child_name_matches_expected():
    """具体型号名要与容器里的名字一致（不是系列名）"""
    caps, ass = mi_cn.fetch_mobile("15948")
    nm = next((a.raw_value for a in ass if a.attribute == "name"), "")
    assert "610L" in str(nm), f"15948 应为 610L 型号，实际 {nm}"


def test_container_price_belongs_to_first_child():
    """容器的 price 确实来自 goodsList[0]（记录名实不符的证据）"""
    caps, ass = mi_cn.fetch_mobile("10050151")
    cid = next(a.raw_value for a in ass if a.attribute == "commodity_id")
    kids = _children_of("10050151")
    # goodsList[0] 是第一个子商品
    caps2, ass2 = mi_cn.fetch_mobile(kids[0])
    cid2 = next(a.raw_value for a in ass2 if a.attribute == "commodity_id")
    assert str(cid) == str(cid2), "容器的价格/商品码应等于第一个子商品"


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
