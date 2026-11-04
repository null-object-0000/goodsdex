"""Run against immutable before/after publication directories."""
import json
import re
import sys
from pathlib import Path
from collections import Counter
from goodsdex.services import classify_service

before, after = map(Path, sys.argv[1:3])
load = lambda root, name: json.loads((root / name).read_text())
b, a = load(before, 'goods.json'), load(after, 'goods.json')
e = load(after, 'goods-excluded.json')
services = [r for r in e['items'] if r['excluded_reason'].startswith('service:')]
assert e['reasons']['service:installation'] == sum(r['excluded_reason'] == 'service:installation' for r in services) == 17
assert len(b) - len(a) == len(services)
# Preserve every field of every non-service row, including true variants.
identity = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
assert Counter(map(identity, (r for r in b if not classify_service(r)))) == Counter(map(identity, a))
report = ['# 服务排除验收', '', '| 口径 | 修前 | 修后 |', '|---|---:|---:|']
bm, am = load(before, 'meta.json'), load(after, 'meta.json')
for k in ['total_all', 'total_published', 'total_excluded']:
    report.append(f'| {k} | {bm[k]} | {am[k]} |')
report += ['', 'total_published 是发布库（含历史下架），沿用原验收 2902 条口径，不将缺少 sale_status 的记录伪称为已验证在售。', '', '| 主类目 | 发布修前 | 发布修后 | 整机修前 | 整机修后 |', '|---|---:|---:|---:|---:|']
for c in ['手机', '笔记本', '电视', '空调', '中央空调Pro', '冰箱', '波轮洗衣机', '滚筒洗衣机', '灯具', '摄像机', 'REDMI路由器', '家庭屏']:
    matches = lambda r: c in [r.get('category'), *(r.get('categories') or [])]
    old, new = [r for r in b if matches(r)], [r for r in a if matches(r)]
    devices = [r for r in old if not classify_service(r)]
    assert len(devices) == len(new)
    report.append(f'| {c} | {len(old)} | {len(new)} | {len(devices)} | {len(new)} |')
report += ['', '整机误伤 0；非服务行逐字段、多重集合完全一致。灯具按 category/categories 合集计数，服务移除不冒充整机损失。', '', '## 全部服务明细（每行 1 条）', '', '| ID | 名称 | 价格 ¥ | 理由 |', '|---|---|---:|---|']
for r in services:
    report.append(f"| {r['id']} | {r['name']} | {r.get('price')} | {r['excluded_reason']} |")
report += ['', '## 同类服务扫描', '']
for word in ['延保', '上门清洗', '以旧换新', '检测服务', '拆旧费', '清洁保养', '换新服务', '勘测服务', '上门维修']:
    hit = [r for r in b if word in r['name']]
    report.append(f'- {word}：{len(hit)} 条；' + '；'.join(f"{r['name']} ¥{r.get('price')}" for r in hit))
uncertain = [r for r in b if re.search('服务|安装|延保|上门|以旧换新|拆旧', r['name']) and not classify_service(r)]
report += ['', '拿不准或实物描述保留：' + json.dumps([dict(name=r['name'], price=r.get('price')) for r in uncertain], ensure_ascii=False)]
Path('docs/services-20261104/README.md').write_text('\n'.join(report) + '\n')
Path('docs/services-20261104/services.json').write_text(json.dumps(services, ensure_ascii=False, indent=2)+'\n')
