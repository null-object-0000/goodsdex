import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from goodsdex.mi_legacy import crawl, publish_legacy

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--public")
    a = ap.parse_args()
    report = crawl()
    if a.public:
        print(publish_legacy("data/categories", a.public))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(bool(report["errors"]))
