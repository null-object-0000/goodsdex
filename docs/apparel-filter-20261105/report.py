"""Read-only audit of a frozen baseline and a finalized release."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.apparel import classify_apparel, categories, NAME_WORDS
from goodsdex.exclusions import validate_excluded
HERE = Path(__file__).resolve().parent


def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def table(rows, cols):
    def cell(value):
        return str(value if value is not None else '').replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['|' + '|'.join(cols) + '|', '|' + '|'.join('---' for _ in cols) + '|'] +
                     ['|' + '|'.join(cell(r.get(c)) for c in cols) + '|' for r in rows])


def candidates(row):
    # Inspection only. These expressions never run in the publisher.
    from goodsdex.accessories import classify
    whole_device = classify(row)['basis'] == 'whole_device'
    name = str(row.get('name') or '')
    principal = re.split(r'(?:含|赠送|附赠|赠|送)', name, maxsplit=1)[0]
    groups = {
        '食品/饮料': r'胶囊咖啡(?!机)|咖啡豆|咖啡粉|茶叶|饮料|矿泉水|饼干|零食|食品',
        '消耗品': r'滤芯|滤网|清洁剂|清洁液|洗手液|洗衣液|牙膏|墨水|墨盒|墨粉|硒鼓|抽纸|卷纸|纸巾|替换芯|尘袋|拖布|刷头',
        '虚拟服务': r'会员|延保|安装服务|上门安装|安装调试|清洗服务|检测服务|拆旧费|上门勘测|上门维修|清洁保养.*服务|换新服务|充值卡|贴膜服务',
        '一次性用品': r'一次性|即弃|用后即弃',
    }
    return [group for group, pattern in groups.items() if re.search(pattern, principal) and not (whole_device and group == '消耗品')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--public', type=Path, required=True)
    a = ap.parse_args()
    before_raw = gzip.decompress((HERE / 'published-before.json.gz').read_bytes())
    before = json.loads(before_raw)
    after = json.loads((a.public / 'goods.json').read_bytes())
    excluded = json.loads((a.public / 'goods-excluded.json').read_bytes())
    meta = json.loads((a.public / 'meta.json').read_bytes())
    validate_excluded(meta, excluded, after)
    hits = [dict(id=r['id'], name=r['name'], category=r.get('category'), categories=categories(r),
                 brand=r.get('brand'), **classify_apparel(r)) for r in before if classify_apparel(r)]
    removed = {r['id'] for r in before} - {r['id'] for r in after}
    assert removed == {r['id'] for r in hits}
    assert not ({r['id'] for r in after} - {r['id'] for r in before})
    apparel = [r for r in excluded['items'] if r['excluded_reason'] == 'apparel']
    assert {r['id'] for r in apparel} == removed
    by_id = {r['id']: r for r in before}
    assert all(all(r.get(k) == v for k, v in by_id[r['id']].items()) for r in apparel)
    washer = next(r for r in before if r.get('name') == '米家内衣物洗烘一体机')
    assert washer['id'] in {r['id'] for r in after}
    spray = [r for r in [*before, *excluded['items']] if '运动鞋' in r.get('name','') and '喷雾' in r.get('name','')]
    bundles = [r for r in before if re.search(r'含[^，,;；。|]*睡衣', r.get('name',''))]
    synthetic = [dict(name='米家运动鞋除臭喷雾', category='清洁剂'),
                 dict(name='床品套装（含睡衣）', category='床品')]
    assert all(classify_apparel(r) is None for r in [washer, *spray, *bundles, *synthetic])
    evidence = dict(washer_observed=washer, spray_observed=spray, included_pajamas_observed=bundles,
                    explicitly_synthetic=[dict(**r, excluded=bool(classify_apparel(r))) for r in synthetic],
                    observed_category_conflicts_kept=[r for r in before if r.get('name') in
                        ('米家洗衣机 波轮6kg', '米家运动杯', '米家便携水杯')])
    write('counterexamples.json', evidence)
    summary = dict(before_sha256=hashlib.sha256(before_raw).hexdigest(), before_published=len(before),
                   after_published=len(after), total_all=meta['total_all'], total_excluded=meta['total_excluded'],
                   excluded_by_rule=meta['excluded_by_rule'], newly_excluded=len(hits),
                   by_brand=dict(Counter(r['brand'] for r in hits)),
                   by_match=dict(Counter(r['matched_rule'] for r in hits)),
                   removed_ids=sorted(removed),
                   retained_rows_changed=sum((Counter(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in after) -
                       Counter(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in before if r['id'] not in removed)).values()))
    write('audit.json', summary)
    write('matches.json', hits)
    (HERE / 'matches.md').write_text('# 服饰排除命中清单\n\n' + table(hits, ['id','name','category','categories','matched_rule','matched_text']) + '\n')
    shortlist = []
    for status, rows in [('published', after), ('already_excluded', excluded['items'])]:
        for row in rows:
            groups = candidates(row)
            if groups:
                shortlist.append(dict(id=row['id'], name=row['name'], category=row.get('category'),
                                      groups=groups, status=status,
                                      existing_reason=row.get('excluded_reason')))
    counts = {status: dict(Counter(g for r in shortlist if r['status'] == status for g in r['groups']))
              for status in ('published', 'already_excluded')}
    write('non-durables.json', dict(counts=counts, total_unique=len({r['id'] for r in shortlist}), items=shortlist))
    active = [r for r in shortlist if r['status'] == 'published']
    (HERE / 'non-durables.md').write_text('# 非耐用品候选（仅列出，不新增排除）\n\n按名称主体审计，排除咖啡机/胶囊耳机等设备误命中；多组重叠不重复计身份。候选词见 report.py，未命中不代表已证明耐用。完整 JSON 同时列出已被既有规则排除的历史记录。\n\n' +
        table([dict(status=s, **{g: counts[s].get(g,0) for g in ('食品/饮料','消耗品','虚拟服务','一次性用品')}) for s in counts],
              ['status','食品/饮料','消耗品','虚拟服务','一次性用品']) +
        '\n\n发布中候选前 20 条（不足 20 条全部列出）：\n\n' + table(active[:20], ['id','name','category','groups','status']) +
        '\n\n既有排除记录前 20 条（不是本次新增排除）：\n\n' + table([r for r in shortlist if r['status']=='already_excluded'][:20], ['id','name','category','groups','existing_reason']) + '\n')
    print(json.dumps(dict(summary=summary, candidates=counts), ensure_ascii=False))

if __name__ == '__main__':
    main()
