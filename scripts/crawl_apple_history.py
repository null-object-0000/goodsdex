"""补齐 Apple 官方历史机型技术规格（不采集旧款现价）。"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from goodsdex.apple_history import crawl_history
from goodsdex.apple import publish_apple
from goodsdex.sources.apple_support import FAMILIES


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--family", action="append", choices=FAMILIES)
    ap.add_argument("--out", default="data/categories")
    ap.add_argument("--raw", default="data/apple/history/raw")
    ap.add_argument(
        "--max-age-days", type=float, default=7, help="旧记录有效期；0 强制重新抓取"
    )
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument(
        "--limit", type=int, default=0, help="限制机型页数量；报告标记非全量"
    )
    ap.add_argument("--public", help="增量合并公开集，保留其他来源")
    a = ap.parse_args()
    if a.max_age_days < 0 or a.limit < 0 or not 1 <= a.workers <= 4:
        ap.error("max-age-days/limit 必须非负，workers 在 1–4 之间")
    report = crawl_history(
        Path(a.out),
        Path(a.raw),
        a.family,
        max_age_days=a.max_age_days,
        workers=a.workers,
        limit=a.limit,
    )
    if a.public:
        publish_apple(a.out, a.public)
    print(
        json.dumps(
            {k: v for k, v in report.items() if k != "pages"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if report["errors"] or not report.get("models") else 0


if __name__ == "__main__":
    raise SystemExit(main())
