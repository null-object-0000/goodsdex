"""分类内过滤：搜索是模糊匹配，同义词会互相污染。

实测问题：搜「壁挂空调」「立式空调」「中央空调」各返回 92/92/91 条，
高度重叠 —— 官方搜索是模糊匹配，没有真正的分类过滤参数
（category_id / cate_id 传了无效，filter_tag 只能粗略筛）。

对策：每个分类定义「必须匹配」的形态词，采集后按名称过滤。
不匹配的**不丢弃**，标记为 excluded 并记录原因，便于复核。
"""
from __future__ import annotations
import re

# 形态词：分类名 -> (必须命中的任一词, 明确排除的词)
# 未列出的分类不过滤。
FORM_RULES: dict[str, dict] = {
    "壁挂空调": {"include": ["挂机", "壁挂", "1.5匹", "1匹", "2匹", "大1.5匹", "大1匹", "超1.5匹"],
                 "exclude": ["立式", "柜机", "中央空调", "风管机", "3匹", "5匹", "4匹", "超3匹"]},
    "立式空调": {"include": ["立式", "柜机"],
                 "exclude": ["挂机", "壁挂", "中央空调", "风管机"]},
    "中央空调Pro": {"include": ["中央空调", "风管机"],
                    "exclude": ["挂机", "壁挂", "立式", "柜机"]},
    "滚筒洗衣机": {"include": ["滚筒"], "exclude": ["波轮"]},
    "波轮洗衣机": {"include": ["波轮"], "exclude": ["滚筒"]},
    "米家跑步机": {"include": ["跑步机"], "exclude": ["走步机"]},
    "走步机": {"include": ["走步机"], "exclude": ["跑步机"]},
    "体重秤": {"include": ["体重秤", "体重"], "exclude": ["体脂"]},
    "体脂秤": {"include": ["体脂"], "exclude": []},
    "游戏电竞显示器": {"include": ["电竞", "游戏"], "exclude": ["办公"]},
    "办公娱乐显示器": {"include": ["办公", "显示器"], "exclude": ["电竞"]},
    "小米路由器": {"include": ["小米路由器", "Xiaomi路由器"], "exclude": ["REDMI路由器", "红米路由器"]},
    "REDMI路由器": {"include": ["REDMI路由器", "红米路由器", "Redmi路由器"],
                    "exclude": ["小米路由器"]},
    "Xiaomi 数字旗舰": {"include": ["Xiaomi", "小米"], "exclude": ["MIX", "Civi", "REDMI", "Redmi"]},
    "Xiaomi MIX系列": {"include": ["MIX", "Mix"], "exclude": []},
    "Xiaomi Civi系列": {"include": ["Civi", "civi"], "exclude": []},
    "REDMI K系列": {"include": ["K"], "exclude": ["Note", "Turbo", "数字"]},
    "REDMI Turbo系列": {"include": ["Turbo"], "exclude": ["Note", "K"]},
    "REDMI Note系列": {"include": ["Note"], "exclude": ["Turbo", "K"]},
}


def matches_category(name: str, category: str) -> tuple[bool, str]:
    """判断商品名是否属于该分类。返回 (是否保留, 原因)"""
    rule = FORM_RULES.get(category)
    if not rule:
        return True, "no_rule"
    n = name or ""
    for w in rule.get("exclude", []):
        if w in n:
            return False, f"excluded_by:{w}"
    inc = rule.get("include", [])
    if not inc:
        return True, "include_empty"
    for w in inc:
        if w in n:
            return True, f"matched:{w}"
    return False, "no_include_match"


def filter_category(records: list[dict], category: str) -> tuple[list[dict], list[dict]]:
    """按分类形态过滤，返回 (保留, 被排除)"""
    kept, dropped = [], []
    for r in records:
        nm = (r.get("product") or {}).get("name", "")
        ok, reason = matches_category(nm, category)
        if ok:
            r.setdefault("product", {})["category_match"] = reason
            kept.append(r)
        else:
            r.setdefault("product", {})["category_match"] = reason
            r["product"]["excluded_reason"] = reason
            dropped.append(r)
    return kept, dropped


def report(kept: list, dropped: list, category: str) -> str:
    if not dropped:
        return f"  {category}: {len(kept)} 款全部符合形态"
    return (f"  {category}: 保留 {len(kept)}，排除 {len(dropped)}"
            f"（{'/'.join(sorted({d['product'].get('excluded_reason','?') for d in dropped}))}）")
