"""把商品档案发布到产物目录（供 data 分支对外提供）。

档案是**累积的**（只增不减），包含已下架商品 —— 这是「从某刻起持续积累，
下架也留档」这一目标的对外体现。

用法：
  python3 scripts/ci_publish_archive.py --archive data/archive --out public/archive
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", default="data/archive")
    ap.add_argument("--out", default="public/archive")
    a = ap.parse_args()

    src = Path(a.archive)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        print(f"没有档案目录 {src}，跳过")
        return 0

    total = missing = cats = 0
    for f in sorted(src.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ⚠ 跳过 {f.name}: {type(e).__name__}")
            continue
        items = d.get("items") or {}
        total += len(items)
        missing += sum(1 for it in items.values() if it.get("missing_since"))
        cats += 1
        (out / f.name).write_text(
            json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    summary = {
        "categories": cats,
        "archived": total,
        "present": total - missing,
        "missing": missing,
        "note": ("商品档案：累积而非覆盖。missing 表示最近一次采集中"
                 "未出现（可能已下架），记录仍保留，并带 missing_since 时刻。"),
    }
    (out / "_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"档案已发布: {cats} 个分类，共 {total} 条（在场 {total-missing}，"
          f"缺席 {missing}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
