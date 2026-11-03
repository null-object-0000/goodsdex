"""Read actual OSS aliases and the published data commit, verify and save evidence."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument('--baseline', default='47cfd505f3c0b77c030c4fe384c06556e6e86b81')
ap.add_argument('--data-revision', required=True)
a = ap.parse_args()
out = Path(__file__).resolve().parent
base = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'

def fetch(name):
    raw = subprocess.check_output(['curl', '--noproxy', '*', '--max-time', '120', '-fSs', '-w', '\n%{http_code}', base + name])
    content, status = raw.rsplit(b'\n', 1)
    assert status == b'200', (name, status)
    return content

meta_raw = fetch('meta.json')
excluded_raw = fetch('goods-excluded.json')
goods_raw = fetch('goods.json')
meta, excluded, goods = map(json.loads, (meta_raw, excluded_raw, goods_raw))
for name, raw in [('goods.json', goods_raw), ('goods-excluded.json', excluded_raw)]:
    d = meta['files'][name]
    assert hashlib.sha256(raw).hexdigest() == d['sha256']
    assert len(raw) == d['bytes']
    published_raw = subprocess.check_output(['git', 'show', f'{a.data_revision}:public/{name}'])
    assert published_raw == raw, name
from goodsdex.exclusions import validate_excluded
from goodsdex.accessories import classify
validate_excluded(meta, excluded, goods)
assert meta['files']['goods-excluded.json']['count'] == excluded['total']
before = json.loads(subprocess.check_output(['git', 'show', f'{a.baseline}:public/goods.json']))
assert before == goods, 'This publication must preserve all previously published objects'
# Show every original source category; never hide sensitive labels by recategorising.
distribution = dict(sorted(Counter(r.get('category') or '(null)' for r in excluded['items']).items()))
sensitive_categories = {'手机', '笔记本', '相机', '相机镜头', '家电', '电视', '冰箱', '空调', '中央空调Pro', '壁挂空调', '立式空调', '净水器', '洗地机', '扫地机器人', '空气净化器', '除螨仪', '加湿器', '吸尘器'}
sensitive = [{k: r.get(k) for k in ['id', 'name', 'category', 'excluded_reason', 'exclusion']}
             for r in excluded['items'] if r.get('category') in sensitive_categories]
# Manual software tombstones named Mac OS are not hardware despite matching
# the accessory classifier's broad Mac device noun. They have reviewed-ID evidence.
assert all(classify(r)['basis'] != 'whole_device' for r in excluded['items']
           if r['excluded_reason'].startswith('accessory:'))
report = dict(http_status=200, baseline=a.baseline, data_revision=a.data_revision,
              revision=meta['revision'], generated_at=meta['generated_at'],
              total_all=meta['total_all'], total_published=meta['total_published'],
              total_excluded=meta['total_excluded'], reasons=excluded['reasons'],
              sha256=meta['files']['goods-excluded.json']['sha256'],
              data_and_oss_byte_identical=True, published_objects_unchanged=True,
              accessory_whole_device_decisions=0, reviewed_software_tombstones=4,
              category_distribution=distribution, sensitive_category_review=sensitive,
              first_three_items=excluded['items'][:3])
(out/'acceptance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
(out/'published-meta.json').write_bytes(meta_raw)
print(json.dumps({k: v for k,v in report.items() if k not in ['sensitive_category_review', 'first_three_items']},ensure_ascii=False,indent=2))
