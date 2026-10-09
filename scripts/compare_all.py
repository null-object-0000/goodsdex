"""跨商品参数对比（通用：接口参数 + 视觉参数）。

为什么需要它：实测发现**冰箱 17/23 台接口本来就有 12 项共同参数**
（制冷方式/冷藏室容积/能效等级/噪音值…），根本不用花钱做视觉提取。
所以先做免费的对比，再决定哪些商品真的需要视觉补。

用法:
  PYTHONPATH=src:scripts python3 scripts/compare_all.py 冰箱
  PYTHONPATH=src:scripts python3 scripts/compare_all.py 冰箱 --all
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from vision_params_lib import META_FIELDS, count_real_params
from goodsdex.vision_normalize import CATEGORY_KEY_ATTRS, canonical

CATS = ROOT / "data" / "categories"


def collect(rec: dict) -> dict:
    """取一条记录的全部参数（接口 + 视觉），归一化到规范名。

    同一规范名有多个来源值时，**保留全部**并标注来源 —— 不静默覆盖。

    **来源必须如实标注**：`view.values` 里可能混有视觉提取的值
    （build_view 时视觉断言也会进视图），不能一律记成"接口" ——
    否则同一份视觉值会被记两次（一次伪装成接口、一次是视觉），
    在对比表里显示为"双源一致"，形成**虚假佐证**。
    """
    # 先建立 capture_id -> 来源 的映射，用于判定视图值真实出处
    src_of_cap = {}
    for c in rec.get("captures") or []:
        src_of_cap[c.get("capture_id")] = c.get("source", "")

    out: dict[str, list[tuple[str, str]]] = {}
    # 视觉断言单独处理（它们的 attribute 是规范名）
    vision_values = {}
    for a in rec.get("assertions") or []:
        if a.get("source") != "mi_cn_pc_vision":
            continue
        canon, _ = canonical(a["attribute"])
        if canon:
            vision_values[canon] = str(a["raw_value"])

    # 视图值：按 selected_from 指向的断言，判断真实来源
    sel = (rec.get("view") or {}).get("selected_from") or {}
    assert_by_id = {a.get("assertion_id"): a for a in (rec.get("assertions") or [])}
    vals = (rec.get("view") or {}).get("values") or {}
    for k, v in vals.items():
        if k in META_FIELDS or k.startswith("_"):
            continue
        canon, _ = canonical(k)
        if not canon:
            continue
        # 该值选中的是哪条断言？据此判定来源
        aid = sel.get(k)
        a = assert_by_id.get(aid)
        if a and a.get("source") == "mi_cn_pc_vision":
            label = "视觉"
        elif a and a.get("source") == "mi_cn_mobile":
            label = "接口"
        elif a and a.get("source") == "mi_cn_pc":
            label = "接口"
        else:
            label = "接口"
        pair = (label, str(v))
        if pair not in out.setdefault(canon, []):
            out[canon].append(pair)

    # 视觉断言补漏（视图里没体现的）
    for canon, v in vision_values.items():
        pair = ("视觉", v)
        if pair not in out.setdefault(canon, []):
            out[canon].append(pair)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("category")
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    fp = CATS / f"{a.category}.json"
    if not fp.exists():
        print(f"分类文件不存在: {fp}")
        return 1
    recs = [r for r in json.loads(fp.read_text(encoding="utf-8"))
            if (r.get("product") or {}).get("kind") == "machine"]
    if not recs:
        print("该分类没有整机")
        return 1

    # 统计参数覆盖
    allnames = Counter()
    per = []
    for r in recs:
        p = collect(r)
        per.append((r, p))
        for k in p:
            allnames[k] += 1

    n = len(recs)
    print(f"分类「{a.category}」整机 {n} 台")
    have = sum(1 for r, _ in per if count_real_params(r) > 0)
    print(f"接口有参数 {have} 台，需视觉补 {n - have} 台")
    print(f"参数名共 {len(allnames)} 个\n")

    keys = None
    for cat, ka in CATEGORY_KEY_ATTRS.items():
        if cat in a.category:
            keys = [k for k in ka if k in allnames]
            break
    if keys is None:
        keys = [k for k, _ in allnames.most_common(24)]

    # 展示用标签：把内部属性 ID 换回中文（如 anc.depth -> 降噪深度）
    from goodsdex.resolve import CATEGORY_RULES
    labels = {}
    for rule in CATEGORY_RULES.values():
        for d in rule.get("attrs", []):
            labels[d.attr_id] = d.label

    if not a.all:
        # 默认：覆盖 >= 50% 的属性（可比性够）
        keys = [k for k in keys if allnames[k] >= n * 0.5]

    # 展示时优先参数最全的商品（否则默认顺序下前几列可能全是"—"）
    per.sort(key=lambda x: -count_real_params(x[0]))
    sel = per[:a.limit]
    names = [r["product"]["name"] for r, _ in sel]
    W = 20
    head = "属性".ljust(18) + "".join(nm[:W].ljust(W + 2) for nm in names)
    print(head)
    print("-" * len(head))
    for k in keys:
        cells = []
        for r, p in sel:
            got = p.get(k)
            if not got:
                cells.append("—".ljust(W + 2))
                continue
            # 多个来源 -> 标注冲突或一致
            uniq = {v for _, v in got}
            v = max((x for x in uniq), key=len) if len(uniq) == 1 else "/".join(sorted(uniq))
            srcs = {s for s, _ in got}
            mark = " ⚠" if len(uniq) > 1 else ""
            cells.append((v + mark)[:W].ljust(W + 2))
        show = labels.get(k, k)
        print(show[:16].ljust(18) + "".join(cells))

    print(f"\n显示 {len(keys)} 项（共 {len(allnames)}）。⚠ 表示多源值不一致")
    miss = [nm for (r, _), nm in zip(sel, names) if count_real_params(r) == 0]
    if miss:
        print(f"其中接口无参数、需视觉补的: {len(miss)} 台")
    return 0


if __name__ == "__main__":
    sys.exit(main())
