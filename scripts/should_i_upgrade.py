"""该不该换：端到端。

输入：手上这台（型号 + 购入价 + 购入日期 + 当前残值），和想换的那台。
输出：纯数字 + 依据，不做主观断言。

数据来源分级（都标注出来）：
  - 官方（官方条款/官方接口）: 一手、可信
  - 平台（转转等）: 需凭证
  - 用户输入: 明确标注为用户提供，非事实采集

用法:
  PYTHONPATH=src python3 scripts/should_i_upgrade.py --device "Xiaomi 15 Pro" \\
      --price 5299 --bought 2026-01-15 --residual 2400-2800 --new-price 5999
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.compare import compare, render_text
from goodsdex.economics import (OwnedDevice, ResidualQuote, advise, load_terms, render)
from goodsdex.identity import parse_variant_attrs
from goodsdex.resolve import guess_category

CATS = ROOT / "data" / "categories"


def find_products(keyword: str, limit: int = 8) -> list[dict]:
    """在全库中按关键词找整机"""
    hits = []
    for f in CATS.glob("*.json"):
        try:
            recs = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in recs:
            p = r.get("product") or {}
            if p.get("excluded") or p.get("kind") != "machine":
                continue
            nm = p.get("name") or ""
            if keyword.lower() in nm.lower():
                hits.append({"category": f.stem, "record": r, "name": nm})
    return hits[:limit]


def current_price(rec: dict):
    v = (rec.get("view") or {}).get("values") or {}
    for k in ("price", "pc_price"):
        if v.get(k):
            try:
                return float(v[k])
            except (TypeError, ValueError):
                pass
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", required=True, help="手上的机型")
    ap.add_argument("--price", type=float, required=True, help="购入价（原零售价）")
    ap.add_argument("--bought", help="购入日期 YYYY-MM-DD")
    ap.add_argument("--residual", help="当前残值，如 2400-2800 或 2400")
    ap.add_argument("--residual-later", type=float, default=None,
                    help="一年后预估残值；不给则按年化 30%% 估算并标注")
    ap.add_argument("--new-price", type=float, required=True, help="新机价")
    ap.add_argument("--trade-in", action="store_true", help="买过官方保值换新服务")
    ap.add_argument("--horizon", type=int, default=365)
    ap.add_argument("--plan", type=int, default=730, help="换新后打算用多少天")
    a = ap.parse_args()

    print("=" * 72)
    print(f"该不该换：{a.device}")
    print("=" * 72)

    # 1. 残值
    if a.residual:
        parts = a.residual.split("-")
        lo = float(parts[0]); hi = float(parts[1]) if len(parts) > 1 else lo
        src = "用户输入"
        conf = "medium"
    else:
        print("\n缺少当前残值 —— 无法判断。")
        print("  获取方式：转转开放平台 market_price（需凭证），或手动输入 --residual")
        return 1
    res = ResidualQuote(low=lo, high=hi, kind="user_input", source=src,
                        observed_at=date.today().isoformat(), confidence=conf,
                        note="用户提供，非采集值")

    # 2. 一年后残值
    if a.residual_later:
        later = a.residual_later
        later_src = "用户输入"
    else:
        later = round(res.low * 0.7)
        later_src = "按年化 30% 估算（未提供实际值）"

    dev = OwnedDevice(name=a.device, purchase_price=a.price,
                      purchase_date=a.bought or "", residual=res,
                      trade_in_eligible=a.trade_in)
    adv = advise(dev, new_price=a.new_price, residual_later=later,
                 horizon_days=a.horizon, planned_use_days=a.plan)
    print()
    print(render(adv))
    print(f"\n  一年后残值      ¥{later:.0f}   （{later_src}）")

    # 3. 新机信息（如果库里有）
    print("\n" + "-" * 72)
    print("想换的那台，官方数据：")
    # 新机匹配：优先同品类（手机换手机），并给序列关键词
    series = " ".join(a.device.split()[:2])   # 如 "Xiaomi 15"
    hits = find_products(series, limit=8)
    if not hits:
        hits = find_products(a.device.split()[0], limit=8)
    # 同品类（phone）优先
    hits.sort(key=lambda h: (0 if h["category"] in
                             ("Xiaomi 数字旗舰", "REDMI K系列", "REDMI Note系列",
                              "REDMI Turbo系列", "Xiaomi MIX系列", "Xiaomi Civi系列")
                             else 1))
    if hits:
        for h in hits[:3]:
            pr = current_price(h["record"])
            print(f"  [{h['category']}] {h['name'][:40]}"
                  + (f"  ¥{pr:.0f}" if pr else ""))
    else:
        print("  （库里没找到匹配机型）")

    print("\n" + "-" * 72)
    print("说明：以上是纯经济账。是否换还取决于新机是否带来你在意的能力提升，")
    print("      本模型不判断这个 —— 它只告诉你'多花这些钱是否值'。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
