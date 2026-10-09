"""数据可用率审计：区分「我们没抓到」和「官方真的没有」。

这是给后续所有分析定边界的报告 —— 不能拿"字段数"当质量指标。
"""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from goodsdex.resolve import guess_category

CATS = ROOT / "data" / "categories"
META = {"name", "gid", "commodity_id", "sku", "price", "market_price", "img_url",
        "carousel", "attrs", "colors", "evaluate_total", "evaluate_real",
        "review_tags", "buyer_imgs", "qa_total", "qa_items", "desc", "buy_options",
        "pc_price", "pc_market_price", "pc_tabs", "pc_imgs", "short_title",
        "sell_points", "_params_empty", "product_id"}


def param_count(rec: dict) -> int:
    vals = (rec.get("view") or {}).get("values") or {}
    return sum(1 for k in vals if k not in META and not k.startswith("_"))


def main() -> int:
    rows = []
    for f in sorted(CATS.glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            p = r.get("product") or {}
            rows.append({
                "category": f.stem,
                "name": p.get("name", ""),
                "kind": p.get("kind", "unknown"),
                "params": param_count(r),
                "params_empty": bool((r.get("view") or {}).get("values", {}).get("_params_empty")),
                "has_pc": any(c["source"] == "mi_cn_pc" and c["status"] == "success"
                              for c in (r.get("captures") or [])),
                "cat": guess_category(p.get("name", "")),
            })

    total = len(rows)
    # 统一口径：排除已被形态过滤、已拆父记录，并按 product_id 去重
    from goodsdex.entities import effective_machines
    machines = effective_machines(rows)
    with_params = [r for r in machines if r["params"] > 0]

    print("=" * 76)
    print(f"全库 {total} 款 | 整机 {len(machines)} 款")
    print("=" * 76)
    print(f"\n整机参数可用性：")
    print(f"  有结构化参数      {len(with_params):4d} / {len(machines)}"
          f"  ({len(with_params)/max(len(machines),1):.1%})")
    print(f"  官方接口参数为空  {len(machines)-len(with_params):4d}"
          f"  ({1-len(with_params)/max(len(machines),1):.1%})")
    print(f"  PC 源成功抓取     {sum(1 for r in machines if r['has_pc']):4d}")

    print(f"\n按品类（整机数 >= 3）：")
    bycat = defaultdict(lambda: {"total": 0, "ok": 0, "empty": 0})
    for r in machines:
        c = bycat[r["category"]]
        c["total"] += 1
        if r["params"] > 0:
            c["ok"] += 1
        else:
            c["empty"] += 1
    print(f"  {'品类':20s}{'整机':>6s}{'有参数':>8s}{'空':>6s}{'可用率':>9s}")
    for cat, c in sorted(bycat.items(), key=lambda x: -(x[1]["ok"] / max(x[1]["total"], 1))):
        if c["total"] < 3:
            continue
        print(f"  {cat[:18]:20s}{c['total']:>6d}{c['ok']:>8d}{c['empty']:>6d}"
              f"{c['ok']/c['total']:>8.0%}")

    print(f"\n参数最全的整机（前 12）：")
    for r in sorted(machines, key=lambda x: -x["params"])[:12]:
        print(f"  {r['params']:3d} 项  [{r['category'][:12]:14s}] {r['name'][:38]}")

    # 落盘
    out = ROOT / "data" / "_usability.json"
    out.write_text(json.dumps({
        "total": total, "machines": len(machines),
        "machines_with_params": len(with_params),
        "machines_params_empty": len(machines) - len(with_params),
        "per_category": {k: v for k, v in bycat.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
