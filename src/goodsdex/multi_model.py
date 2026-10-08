"""多型号条目拆分：一个 product_id 实际覆盖多个型号时，拆成多条记录。

实测问题（对比表暴露）：
  「米家冰箱 三门系列」的 tab 是
    256L(星锻银) / 271L(全域离子净化) / 215L / 风冷-216L / 直冷-216L
  覆盖 5 个不同型号，规格各异。当成一台对比会得到
  "103.1cm/216 L/256L/2..." 这种拼接垃圾值。

  「米家冰箱 两门系列」4 个 tab：直冷-185L / 直冷-186L / 风冷-186L / 直冷-186L(一级能效)
  而接口只给一份参数（总容量 186L）—— 接口参数**只对应其中一个型号**，
  其余型号的参数完全拿不到。

拆分的依据在数据里：
  每个 tab 的视觉参数里带 **产品型号**（MC-256WTMPN / BCD-216WMD …），
  tab 名本身也常是型号标识（"256L(星锻银)" / "直冷-186L"）。

原则：
  - 拆分只针对**多型号条目**（>=2 个非服务 tab 且 tab 名像型号）
  - 每条子记录的型号标识优先用视觉提取出的「产品型号」，退而用 tab 名
  - **接口参数归属**：接口参数是单份，无法自动确定属于哪个子型号 ——
    标为 ambiguous，不硬塞给任何一个（宁可缺失，不可错配）
  - 父记录保留，子记录用 parent 字段关联，可回溯
"""
from __future__ import annotations
import json
import re
from typing import Optional

# 非型号 tab（服务/详情类）
GENERIC_TAB = re.compile(
    r"售后|服务条款|安装须知|安装费用|保障|说明|政策|常见问题|推荐|评价|"
    r"商品详情|产品详情|详情$|参数$|规格参数|产品参数|商品参数|"
    r"参数配置|安装收费|包装清单|常见问题")

# tab 名像型号的特征：含容量/门体/规格词
MODEL_TAB = re.compile(
    r"\d+\s*[Ll]\b|\d+L|匹|门|嵌入式|风冷|直冷|净离子|离子|自动制冰|"
    r"\d+GB|\d+G\b|英寸|寸|核|代|款|Pro|Max|Plus|Ultra", re.I)


def is_model_tab(name: str) -> bool:
    """判断 tab 名是否是具体型号（而非"规格参数"这类通用名）"""
    if not name or GENERIC_TAB.search(name):
        return False
    return bool(MODEL_TAB.search(name))


def spec_tabs(rec: dict) -> list[dict]:
    """取该记录的所有规格 tab（含 tab_index / 名称 / 图片数）"""
    out = []
    for c in rec.get("captures") or []:
        if c.get("source") != "mi_cn_pc":
            continue
        try:
            j = json.loads(c.get("response_raw") or "")
        except Exception:
            continue
        tabs = ((j.get("data") or {}).get("extend_info") or {}).get("desc_tabs_view") or []
        for ti, t in enumerate(tabs):
            if not t.get("tab_content"):
                continue
            out.append({"tab_index": ti, "name": t.get("name") or "",
                        "img_count": len(t.get("tab_content") or [])})
    return out


def is_multi_model(rec: dict, min_tabs: int = 2) -> tuple[bool, list[dict]]:
    """判断是否是多型号条目，返回 (是否, 型号 tab 列表)"""
    tabs = [t for t in spec_tabs(rec) if is_model_tab(t["name"])]
    return (len(tabs) >= min_tabs), tabs


def split_record(rec: dict) -> tuple[list[dict], dict]:
    """把多型号条目拆成多条子记录。

    返回 (子记录列表, 统计)。若不需要拆，子记录为空。
    """
    ok, tabs = is_multi_model(rec)
    if not ok:
        return [], {"reason": "not_multi_model"}

    parent = rec.get("product") or {}
    parent_id = parent.get("product_id", "")
    model_tabs = {t["tab_index"]: t["name"] for t in tabs}

    # 视觉断言按 tab 分组
    by_tab: dict[int, list] = {}
    for a in rec.get("assertions") or []:
        if a.get("source") != "mi_cn_pc_vision":
            continue
        m = re.search(r"desc_tabs_view\[(\d+)\]", a.get("locator") or "")
        if not m:
            continue
        by_tab.setdefault(int(m.group(1)), []).append(a)

    children = []
    for ti, tname in sorted(model_tabs.items()):
        asserts = by_tab.get(ti, [])
        # 型号标识：优先用视觉提取的「产品型号」
        model_code = ""
        for a in asserts:
            if a.get("attribute") in ("产品型号", "型号", "规格型号"):
                model_code = str(a.get("raw_value") or "").strip()
                break
        label = model_code or tname
        child_id = f"{parent_id}#tab{ti}"
        children.append({
            "product": {
                **{k: v for k, v in parent.items() if k != "variants"},
                "product_id": child_id,
                "name": label,
                "parent_product_id": parent_id,
                "variant_tab": tname,
                "model_code": model_code,
                "is_model_child": True,
                "kind": "machine",
            },
            "assertions": asserts,
            "captures": [],          # 原响应属于父记录，不重复
            "view": {},              # 由调用方重建
            "market_prices": [],
            "discovery": rec.get("discovery") or {},
            "fetched_at": rec.get("fetched_at", ""),
        })

    stats = {
        "parent": parent_id,
        "parent_name": parent.get("name", ""),
        "model_tabs": len(model_tabs),
        "children": len(children),
        "interface_params": sum(
            1 for k in (rec.get("view") or {}).get("values", {})
            if not k.startswith("_")),
        "interface_params_ambiguous": True,   # 接口参数无法归属到具体子型号
    }
    return children, stats


def split_category(recs: list[dict]) -> tuple[list[dict], dict]:
    """对一个分类的记录做拆分。返回 (新记录列表, 统计)"""
    out, stats = [], {"total": 0, "split": 0, "children": 0, "details": []}
    for r in recs:
        stats["total"] += 1
        kids, st = split_record(r)
        if kids:
            stats["split"] += 1
            stats["children"] += len(kids)
            stats["details"].append(st)
            out.extend(kids)
        else:
            out.append(r)
    return out, stats


if __name__ == "__main__":
    import sys
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[2]
    cat = sys.argv[1] if len(sys.argv) > 1 else "冰箱"
    fp = ROOT / "data" / "categories" / f"{cat}.json"
    recs = json.loads(fp.read_text(encoding="utf-8"))
    machines = [r for r in recs if (r.get("product") or {}).get("kind") == "machine"]
    out, st = split_category(machines)
    print(f"分类「{cat}」整机 {st['total']} 台")
    print(f"  多型号条目 {st['split']} 台 -> 拆出 {st['children']} 条子记录")
    print(f"  拆分后共 {len(out)} 条\n")
    for d in st["details"][:6]:
        print(f"  {d['parent_name'][:30]:32s} {d['model_tabs']} 个型号 tab"
              f" -> {d['children']} 条")
