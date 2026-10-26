"""分类解析测试（离线 fixture）

Codex 评审用离线反例证明正则解析会漏分类与污染关键词：
  - <dd class="nav"> 漏掉
  - <span class="text active"> 漏掉
  - keyword=耳机&amp;page=2 -> 关键词变成 "耳机&amp;page=2"
现改用 HTMLParser + parse_qs，并加健全性检查。
"""
import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.sources import mi_cn


def _html_with(nav_pairs, panel_pairs):
    parts = []
    for name, href in nav_pairs:
        parts.append(f'<dd><a href="{href}">{name}</a></dd>')
    for name, href in panel_pairs:
        parts.append(f'<a href="{href}"><span class="text">{name}</span></a>')
    return "".join(parts)


def _big_fixture():
    """构造足够大的 fixture 以通过健全性检查"""
    nav = [(n, f"/search?keyword={n}") for n in
           ["手机", "电视", "笔记本", "平板", "穿戴", "耳机", "家电", "路由器",
            "音箱", "配件"]]
    panel = [(f"类目{i}", f"/search?keyword=类目{i}") for i in range(80)]
    return _html_with(nav, panel)


def test_both_link_forms_parsed():
    """导航区（纯文本）与面板（带 span）都要解析"""
    html = _big_fixture()
    with patch.object(mi_cn, "_get", return_value=html):
        r = mi_cn.list_categories()
    for k in ("手机", "耳机", "电视", "笔记本", "平板"):
        assert k in r, f"{k} 未被解析"


def test_attributes_on_tags_tolerated():
    """标签带属性（dd class / span 多 class）不能导致漏解析"""
    html = ('<dd class="nav-main"><a href="/search?keyword=手机" '
            'class="link">手机</a></dd>'
            '<a href="/search?keyword=耳机"><span class="text active">耳机</span></a>'
            + _html_with([("电视", "/search?keyword=电视"),
                          ("笔记本", "/search?keyword=笔记本"),
                          ("平板", "/search?keyword=平板"),
                          ("穿戴", "/search?keyword=穿戴"),
                          ("家电", "/search?keyword=家电"),
                          ("路由器", "/search?keyword=路由器")], [])
            + _html_with([], [(f"项{i}", f"/search?keyword=项{i}") for i in range(80)]))
    with patch.object(mi_cn, "_get", return_value=html):
        r = mi_cn.list_categories()
    assert r.get("手机") == "手机", "带 class 的 dd 不应漏掉"
    assert r.get("耳机") == "耳机", "多 class 的 span 不应漏掉"


def test_keyword_not_polluted_by_extra_params():
    """keyword 参数不能把 &page=2 一起吃进去"""
    html = ('<dd><a href="/search?keyword=%E8%80%B3%E6%9C%BA&amp;page=2">耳机</a></dd>'
            + _html_with([("手机", "/search?keyword=手机&page=3"),
                          ("电视", "/search?keyword=电视"),
                          ("笔记本", "/search?keyword=笔记本"),
                          ("平板", "/search?keyword=平板"),
                          ("穿戴", "/search?keyword=穿戴"),
                          ("家电", "/search?keyword=家电"),
                          ("路由器", "/search?keyword=路由器")], [])
            + _html_with([], [(f"项{i}", f"/search?keyword=项{i}") for i in range(80)]))
    with patch.object(mi_cn, "_get", return_value=html):
        r = mi_cn.list_categories()
    assert r.get("耳机") == "耳机", f"关键词被污染: {r.get('耳机')!r}"
    assert r.get("手机") == "手机", f"关键词被污染: {r.get('手机')!r}"


def test_sanity_check_raises_on_small_result():
    """页面结构变化导致分类骤减时必须报错，不返回残缺短字典"""
    html = '<dd><a href="/search?keyword=耳机">耳机</a></dd>'
    with patch.object(mi_cn, "_get", return_value=html):
        try:
            mi_cn.list_categories()
            assert False, "应当抛 RuntimeError"
        except RuntimeError as e:
            assert "分类解析异常" in str(e)


def test_sanity_check_raises_on_missing_major():
    """大类缺失必须报错"""
    # 60 个小类目但没有手机/耳机等大类
    html = _html_with([], [(f"项{i}", f"/search?keyword=项{i}") for i in range(60)])
    with patch.object(mi_cn, "_get", return_value=html):
        try:
            mi_cn.list_categories()
            assert False, "缺少大类时应抛异常"
        except RuntimeError as e:
            assert "缺少" in str(e)


def test_real_page_has_major_categories():
    """复用审计快照，不在测试中绕过统一限速器请求网络。"""
    from pathlib import Path
    snapshot = Path(__file__).resolve().parents[1] / 'data/coverage-20261026/category.html'
    if not snapshot.exists():
        pytest.skip("本地没有只读审计快照")
    with patch.object(mi_cn, "_get", return_value=snapshot.read_text()):
        result = mi_cn.list_categories()
    assert len(result) >= 76
    assert {"手机", "电视", "笔记本", "平板", "穿戴", "耳机", "家电", "路由器"} <= set(result)


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


def test_sanity_check_rejects_drop_from_verified_baseline():
    nav = [(n, f"/search?keyword={n}") for n in
           ["手机", "电视", "笔记本", "平板", "穿戴", "耳机", "家电", "路由器"]]
    html = _html_with(nav, [(f"类{i}", f"/search?keyword=类{i}") for i in range(50)])
    with patch.object(mi_cn, "_get", return_value=html), pytest.raises(RuntimeError):
        mi_cn.list_categories()


@pytest.mark.parametrize("major", ["穿戴", "家电", "路由器"])
def test_sanity_check_requires_all_major_categories(major):
    html = _big_fixture().replace(f'<dd><a href="/search?keyword={major}">{major}</a></dd>', '')
    with patch.object(mi_cn, "_get", return_value=html), pytest.raises(RuntimeError):
        mi_cn.list_categories()
