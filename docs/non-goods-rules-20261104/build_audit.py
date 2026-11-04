"""Audit the local 5448-row snapshot and the actual publication baseline."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.services import classify_non_goods

HERE = Path(__file__).resolve().parent
WORDS = re.compile('定金|订金|权益|预约|盲约|预售|占位|不发货|安装服务|延保|上门|以旧换新补贴|充值卡|贴膜服务')

def scan(raw):
    rows = json.loads(raw)
    hits = []
    for i, row in enumerate(rows, 1):
        decision = classify_non_goods(row)
        if decision:
            hits.append(dict(row=i, id=row['id'], name=row['name'], price=row.get('price'), **decision))
    return dict(sha256=hashlib.sha256(raw).hexdigest(), rows=len(rows),
                literal_keyword_rows=sum(bool(WORDS.search(r.get('name') or '')) for r in rows),
                matched_rows=len(hits), matched_ids=len({r['id'] for r in hits}),
                by_rule=dict(Counter(r['matched_rule'] for r in hits)), hits=hits)


def main():
    baseline_path = HERE / 'published-before.json.gz'
    if not baseline_path.exists():
        raw = (HERE / 'published-before.json').read_bytes()
        baseline_path.write_bytes(gzip.compress(raw, mtime=0))
    before = gzip.decompress(baseline_path.read_bytes())
    audit = dict(local_snapshot=scan((ROOT / 'public/goods.json').read_bytes()),
                 published_before=scan(before))
    # Synthetic boundary cases are explicitly separate from observed catalog rows.
    examples = ['空调含安装服务', '小米电视（赠延保服务）', '手机套装（含贴膜服务）']
    audit['synthetic_kept_examples'] = [dict(name=n, excluded=classify_non_goods(dict(name=n)) is not None) for n in examples]
    assert not any(r['excluded'] for r in audit['synthetic_kept_examples'])
    rows = json.loads(before)
    audit['observed_kept_with_requested_keywords'] = [r for r in rows if WORDS.search(r.get('name') or '') and not classify_non_goods(r)]
    assert audit['local_snapshot']['rows'] == 5448
    assert audit['published_before']['matched_rows'] == 1
    (HERE / 'audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    lines = ['# 全库命中清单', '', '旧本地快照 5,448 行：78 行命中（46 个身份），其中定金 1 行、既有服务 77 行。重复身份按原输入行分别列出，未去重凑数。', '', '|原行号|id|名称|价格 ¥|matched_rule|matched_text|', '|---:|---|---|---:|---|---|']
    for r in audit['local_snapshot']['hits']:
        lines.append(f"|{r['row']}|{r['id']}|{r['name']}|{r['price']}|{r['matched_rule']}|{r['matched_text']}|")
    lines += ['', '当前发布基线 2,856 行仅命中 1 行：', '', '|id|名称|价格 ¥|matched_rule|matched_text|', '|---|---|---:|---|---|']
    for r in audit['published_before']['hits']:
        lines.append(f"|{r['id']}|{r['name']}|{r['price']}|{r['matched_rule']}|{r['matched_text']}|")
    (HERE / 'matches.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: {x:y for x,y in v.items() if x != 'hits'} for k,v in audit.items() if isinstance(v, dict)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
