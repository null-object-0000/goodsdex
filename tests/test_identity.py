"""商品身份测试 —— 对应 Codex 评审第二优先级的验收标准。

验收：
  - 不同颜色、不同 SKU、不同地区和同名不同型号不会误合
  - 每份列表说明"从哪里发现、覆盖到哪里、是否完整"
  - 名称提示与标准名称分离
  - 两端报价对比指向同一已确认变体
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.identity import (build_identity, make_product_id, make_variant_id,
                               parse_variant_attrs, product_name, same_product,
                               Product)


# ---------- 变体属性解析 ----------

def test_color_full_phrase():
    """颜色要取完整词组，不能被单个字截断"""
    assert parse_variant_attrs("REDMI Buds 8 Pro 冰釉白")["color"] == "冰釉白"
    assert parse_variant_attrs("Xiaomi 耳夹式耳机 玄武岩黑")["color"] == "玄武岩黑"
    assert parse_variant_attrs("REDMI Buds 8S 暮黑")["color"] == "暮黑"


def test_capacity_split():
    """容量要拆成 ram / rom，不能当成一个字符串"""
    a = parse_variant_attrs("Xiaomi 18 Pro Max 12GB+256GB")
    assert a["ram"] == "12GB" and a["rom"] == "256GB"
    b = parse_variant_attrs("REDMI Note 17 8GB+128GB")
    assert b["ram"] == "8GB" and b["rom"] == "128GB"


def test_edition_flagged():
    """特别版必须单独标记，不能与普通版混为一谈"""
    a = parse_variant_attrs("Xiaomi 18 Pro Max 16GB+1TB 特别版")
    assert a.get("edition") == "特别版"


def test_product_name_strips_variant():
    """产品名要去掉变体后缀（颜色/容量）"""
    assert product_name("REDMI Buds 8 Pro 冰釉白").strip() == "REDMI Buds 8 Pro"
    n = product_name("Xiaomi 18 Pro Max 16GB+1TB")
    assert "GB" not in n and "TB" not in n


def test_edition_vs_color_not_confused():
    """回归：版本词不能被当成颜色剥掉

    实测：「REDMI Buds 6 青春版」的"青春版"含"青"字，
    被 _is_color_token 判成颜色剥离 -> 与「REDMI Buds 6」同名，
    对比时会把两个不同产品混为一谈。
    """
    # 产品名必须保留版本词
    assert product_name("REDMI Buds 6 青春版 子夜黑") == "REDMI Buds 6 青春版"
    assert product_name("REDMI Buds 6 子夜黑") == "REDMI Buds 6"
    assert product_name("REDMI Buds 8 活力版 海浪蓝") == "REDMI Buds 8 活力版"
    assert product_name("REDMI Buds 8 脂白") == "REDMI Buds 8"
    # 三者必须互不相同
    a = product_name("REDMI Buds 6 青春版 子夜黑")
    b = product_name("REDMI Buds 6 子夜黑")
    c = product_name("REDMI Buds 6 活力版 白色")
    assert len({a, b, c}) == 3, "青春版/标准版/活力版必须能区分"
    # 颜色要正确提取，不能把版本词当颜色
    assert parse_variant_attrs("REDMI Buds 6 青春版 子夜黑")["color"] == "子夜黑"
    assert parse_variant_attrs("REDMI Buds 6 青春版 子夜黑")["edition"] == "青春版"


def test_product_name_no_char_level_corruption():
    """回归：不能把"纯白色"打成"纯色"——全局替换单字会毁掉产品名"""
    assert product_name("米家便携吹风机H101 白色") == "米家便携吹风机H101"
    assert product_name("米家负离子速干吹风机 H300 纯白色") == "米家负离子速干吹风机 H300"
    assert product_name("米家高速吹风机 粉色") == "米家高速吹风机"
    # 产品名里的"白/黑"等字不能被误删
    assert "白" in product_name("小白智能摄像机 白色") or \
           product_name("小白智能摄像机 白色") == "小白智能摄像机"


# ---------- 身份层次 ----------

def test_product_variant_hierarchy():
    """product_id 是产品级，commodity_id 是变体级"""
    p = build_identity("22137", [
        {"commodity_id": 1230805246, "name": "REDMI Buds 8 Pro 冰釉白", "price": "369"},
        {"commodity_id": 1230805247, "name": "REDMI Buds 8 Pro 玄悟黑", "price": "369"},
        {"commodity_id": 1230805248, "name": "REDMI Buds 8 Pro 薄雾蓝", "price": "369"},
    ])
    assert p.product_id == "CN:mi_cn:product:22137"
    assert len(p.variants) == 3
    assert all(v.product_id == p.product_id for v in p.variants)
    assert len({v.variant_id for v in p.variants}) == 3


def test_different_market_not_merged():
    """不同地区不能合并（型号体系不同）"""
    cn = build_identity("22137", [{"commodity_id": 1, "name": "X"}], market="CN")
    hk = build_identity("22137", [{"commodity_id": 1, "name": "X"}], market="HK")
    assert cn.product_id != hk.product_id
    assert same_product(cn, hk) is False, "不同地区必须判为不同实体"


def test_same_name_not_proof_of_identity():
    """名称一致只是候选，不是同一性证明；无法判定时返回 None"""
    a = Product(product_id="CN:mi_cn:product:1", name="同名产品", market="CN")
    b = Product(product_id="CN:other:product:9", name="同名产品", market="CN")
    assert same_product(a, b) is None, "无型号/外部ID 时不能仅凭名称判同一"


def test_external_id_proves_identity():
    """外部 ID 命中可以确定同一"""
    a = Product(product_id="CN:mi_cn:product:1", market="CN",
                external_ids={"mi_cn.product_id": "1"})
    b = Product(product_id="CN:mi_cn:product:1", market="CN",
                external_ids={"mi_cn.product_id": "1"})
    assert same_product(a, b) is True


def test_market_in_product_id():
    """地区必须显式写入 ID（现在只做国行也要标明）"""
    assert make_product_id("CN", "mi_cn", "22137") == "CN:mi_cn:product:22137"
    assert make_variant_id("CN", "mi_cn", "1230805246") == "CN:mi_cn:commodity:1230805246"


def test_identity_evidence_recorded():
    """身份判定要有依据，供复核"""
    p = build_identity("22137", [{"commodity_id": 1, "name": "REDMI Buds 8 Pro 冰釉白"}])
    ev = p.identity_evidence
    assert ev["variant_count"] == 1
    assert "basis" in ev and "scope" in ev
    assert "CN" in ev["scope"]


def test_variants_dedup():
    """重复变体不重复计入"""
    p = build_identity("1", [
        {"commodity_id": 1, "name": "A 白色"},
        {"commodity_id": 1, "name": "A 白色"},
    ])
    assert len(p.variants) == 1


def test_serializable():
    p = build_identity("22137", [{"commodity_id": 1, "name": "REDMI Buds 8 Pro 冰釉白"}])
    s = json.dumps(p.to_dict(), ensure_ascii=False)
    back = json.loads(s)
    assert back["variants"][0]["attrs"]["color"] == "冰釉白"


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
