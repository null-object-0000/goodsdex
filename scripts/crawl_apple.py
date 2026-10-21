"""Apple 官方中国大陆采集入口。默认主要产品系列；不宣称完整 CTO/配件覆盖。"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from goodsdex.apple import crawl, publish_apple
from goodsdex.sources.apple_cn import FAMILIES


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", action="append", choices=FAMILIES)
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="只跑前 N 个购买页，供 smoke；不表示完整采集",
    )
    ap.add_argument("--out", default="data/categories")
    ap.add_argument("--raw", default="data/apple/raw")
    ap.add_argument("--archive", default="data/archive")
    ap.add_argument(
        "--prices-only",
        action="store_true",
        help="复用已发现的购买页刷新价格，保留已有规格表",
    )
    ap.add_argument("--public", help="增量合并进已有公开集，保留其他品牌")
    ap.add_argument("--pause", type=float, default=0.2)
    a = ap.parse_args()
    if a.limit < 0 or a.pause < 0:
        ap.error("limit/pause 不能为负")
    report = crawl(
        Path(a.out),
        Path(a.raw),
        Path(a.archive),
        a.family,
        a.limit,
        pause=a.pause,
        prices_only=a.prices_only,
    )
    if a.public:
        print(
            "published", json.dumps(publish_apple(a.out, a.public), ensure_ascii=False)
        )
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in ("seeds", "pages", "spec_discovery")
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if report["errors"] or not report["variants"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
