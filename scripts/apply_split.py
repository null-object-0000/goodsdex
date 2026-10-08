"""把多型号拆分应用到全库，并重建视图。

用法:
  PYTHONPATH=src:scripts python3 scripts/apply_split.py 冰箱 --write
  PYTHONPATH=src:scripts python3 scripts/apply_split.py --all --write
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from goodsdex.facts import Assertion
from goodsdex.multi_model import split_record
from goodsdex.resolve import build_view, guess_category
from vision_params_lib import META_FIELDS, count_real_params

CATS = ROOT / "data" / "categories"
A_KEYS = ("assertion_id", "subject_id", "capture_id", "source", "attribute",
          "raw_value", "locator", "ui_location", "page", "parser_version",
          "availability")


def rebuild_view(child: dict) -> dict:
    """重建子记录的视图（只用它自己的视觉断言）。

    接口参数**不塞进子记录** —— 实测接口只给一份参数、对应其中某一个
    型号，无法自动判定归属。宁缺勿错：标为父级 ambiguous 参数。
    """
    asserts = [Assertion(**{k: v for k, v in a.items() if k in A_KEYS})
               for a in child["assertions"]]
    name = child["product"].get("name", "")
    return build_view(asserts, category=guess_category(name) or "generic",
                      subject_id=child["product"]["product_id"]).to_dict()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("category", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    targets = ([f.stem for f in sorted(CATS.glob("*.json"))] if a.all
               else [a.category] if a.category else [])
    if not targets:
        ap.error("给一个分类名，或用 --all")

    grand = {"cats": 0, "before": 0, "after": 0, "split": 0, "children": 0}
    for cat in targets:
        fp = CATS / f"{cat}.json"
        if not fp.exists():
            continue
        recs = json.loads(fp.read_text(encoding="utf-8"))
        machines = [r for r in recs if (r.get("product") or {}).get("kind") == "machine"]
        others = [r for r in recs if (r.get("product") or {}).get("kind") != "machine"]

        new_machines, n_split, n_kids = [], 0, 0
        for r in machines:
            kids, st = split_record(r)
            if kids:
                n_split += 1
                n_kids += len(kids)
                for k in kids:
                    k["view"] = rebuild_view(k)
                # 父记录保留，标记已拆（可回溯，但不再参与对比）
                r["product"]["is_multi_model_parent"] = True
                r["product"]["split_children"] = [k["product"]["product_id"] for k in kids]
                new_machines.extend(kids)
            new_machines.append(r)

        before = len(machines)
        after = len(new_machines)
        grand["cats"] += 1
        grand["before"] += before
        grand["after"] += after
        grand["split"] += n_split
        grand["children"] += n_kids
        if n_split:
            print(f"  {cat[:18]:20s} 整机 {before:3d} -> {after:3d} "
                  f"（{n_split} 台拆分出 {n_kids} 条子记录）")
        if a.write:
            out = others + new_machines
            tmp = fp.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                           encoding="utf-8")
            tmp.replace(fp)

    print(f"\n{'(已写盘) ' if a.write else '(试运行) '}"
          f"{grand['cats']} 个分类：整机 {grand['before']} -> {grand['after']}，"
          f"拆分 {grand['split']} 台，子记录 {grand['children']} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
