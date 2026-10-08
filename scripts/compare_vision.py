"""跨商品参数对比（视觉数据）。

产物示例：
  属性            巨省电1.5匹   柔风1.5匹   巨省电2匹
  匹数            1.5匹        1.5匹       2匹
  能效APF         5.27         5.30        5.00
  ...
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.vision_normalize import CATEGORY_KEY_ATTRS

CATS = ROOT / "data" / "categories"


def load_vision(category: str) -> list[dict]:
    fp = CATS / f"{category}.json"
    if not fp.exists():
        return []
    return [r for r in json.loads(fp.read_text(encoding="utf-8"))
            if (r.get("product") or {}).get("vision_extracted")]


def build_table(recs: list[dict], keys: list[str] | None = None,
                max_cols: int = 5):
    recs = recs[:max_cols]
    names = [r["product"]["name"] for r in recs]
    table: dict[str, dict] = {}
    for r in recs:
        nm = r["product"]["name"]
        for a in r["assertions"]:
            if a["source"] != "mi_cn_pc_vision":
                continue
            table.setdefault(a["attribute"], {})[nm] = a["raw_value"]
    if keys is None:
        # 按覆盖率排序（多少台有值）
        keys = sorted(table, key=lambda k: -len(table[k]))
    else:
        keys = [k for k in keys if k in table]
    return table, keys, names


def render(table: dict, keys: list[str], names: list[str],
           width: int = 22) -> str:
    lines = []
    head = "属性".ljust(20) + "".join(n[:width].ljust(width + 2) for n in names)
    lines.append(head)
    lines.append("-" * len(head))
    for k in keys:
        row = table[k]
        cells = []
        for n in names:
            v = str(row.get(n, "—"))
            cells.append(v[:width].ljust(width + 2))
        lines.append(k[:18].ljust(20) + "".join(cells))
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("category")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--all", action="store_true", help="显示全部属性")
    ap.add_argument("--key-only", action="store_true", help="只显示品类关键属性")
    a = ap.parse_args()

    recs = load_vision(a.category)
    if not recs:
        print(f"分类「{a.category}」没有已验证的视觉提取数据")
        return 1
    print(f"分类「{a.category}」整机 {len(recs)} 台已完成视觉提取\n")

    keys = None
    if a.key_only:
        for cat, ka in CATEGORY_KEY_ATTRS.items():
            if cat in a.category:
                keys = ka
                break
    table, keys, names = build_table(recs, keys, a.limit)

    if not a.all:
        # 默认只显示覆盖率 >= 80% 的属性（能对比的）
        n = min(len(recs), a.limit)
        keys = [k for k in keys if len(table[k]) >= n * 0.8]
    print(render(table, keys, names))

    # 统计
    n = min(len(recs), a.limit)
    full = [k for k in table if len(table[k]) == n]
    print(f"\n共有属性 {len(full)} 个 | 显示 {len(keys)} 个 | 总属性名 {len(table)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
