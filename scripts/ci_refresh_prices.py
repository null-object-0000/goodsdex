"""GitHub Action 用的价格刷新入口。

**为什么不能直接用 prices.py**：
运行器上没有 `data/categories/`（那是内部采集产物，已 gitignore，
343 MB 也不该入 git）。但价格刷新只需要 **gid 列表**。

所以设计成：发布集里带上 gid（publish.py 已保留），
Action 从 `public/goods.json` 读出 gid 去刷价 ——
发布集既是产出，也是刷新价格的输入，形成闭环。

用法：
  python3 scripts/ci_refresh_prices.py --public public
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.prices import refresh  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", default="public")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    gpath = Path(a.public) / "goods.json"
    if not gpath.exists():
        print(f"找不到 {gpath} —— 先跑 publish", file=sys.stderr)
        return 1
    items = json.loads(gpath.read_text(encoding="utf-8"))
    gids = [str(it["gid"]) for it in items if it.get("gid")]
    if a.limit:
        gids = gids[:a.limit]
    print(f"从发布集读到 {len(gids)} 个 gid")

    res = refresh(gids, Path(a.public).parent / "data")
    print(json.dumps(res, ensure_ascii=False, indent=1))

    # 把最新价格回灌进发布集（保持 goods.json 的价格是新的一手数据）
    latest = Path(a.public).parent / "data" / "prices" / "latest.json"
    if latest.exists():
        prices = json.loads(latest.read_text(encoding="utf-8")).get("prices") or {}
        changed = 0
        for it in items:
            g = str(it.get("gid") or "")
            np = prices.get(g)
            if np and np.get("price") is not None:
                # **类型要统一再比**：goods.json 里 price 可能是字符串
                # （来自采集的 view），接口返回的是数字。
                # 曾因此把"全部商品"都算成价格变化（3469 条假变化）。
                def num(x):
                    try:
                        return float(x)
                    except (TypeError, ValueError):
                        return None
                old, new = num(it.get("price")), num(np["price"])
                if old is not None and new is not None and old != new:
                    changed += 1
                elif old is None:
                    changed += 1          # 原本没价，现在有了
                # 统一写回数字类型
                it["price"] = np["price"]
                mp = num(np.get("market_price"))
                it["market_price"] = (int(mp) if mp == int(mp) else mp
                                      if mp is not None else None)
        gpath.write_text(json.dumps(items, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        print(f"回灌完成，价格变化 {changed} 条")

    # 时间序列也要进发布集（公开的价格历史）
    src = Path(a.public).parent / "data" / "prices"
    if src.exists():
        dst = Path(a.public) / "prices"
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.glob("*.jsonl"):
            (dst / f.name).write_text(f.read_text(encoding="utf-8"),
                                      encoding="utf-8")
        lf = src / "latest.json"
        if lf.exists():
            (dst / "latest.json").write_text(lf.read_text(encoding="utf-8"),
                                             encoding="utf-8")
        print(f"时间序列已同步到 {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
