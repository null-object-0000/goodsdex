"""Confirm absent Xiaomi IDs before publication; retain complete previous rows."""
import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.delisted import ARCHIVE_NAME, prepare
from goodsdex.publish import collect_public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous', type=Path, default=Path('_data/public/goods.json'))
    parser.add_argument('--cats', type=Path, default=Path('data/categories'))
    parser.add_argument('--archive', type=Path, default=Path('data/archive'))
    parser.add_argument('--reports', type=Path, default=Path('docs'))
    args = parser.parse_args()
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    path = args.archive / ARCHIVE_NAME
    archive = json.loads(path.read_text()) if path.exists() else {}
    previous = json.loads(args.previous.read_text())
    result, report = prepare(previous, collect_public(args.cats), archive, now=now)
    args.archive.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    tmp.replace(path)
    report['probed_at'] = now
    target = args.reports / f'delisted-{now[:10]}' / 'report.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(report['counts'], ensure_ascii=False))


if __name__ == '__main__':
    main()
