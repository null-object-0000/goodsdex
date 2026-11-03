"""Reproduce release-only accessory counts and the fixed, individually inspected sample."""
import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from goodsdex.accessories import classify, fingerprint

OUT = Path(__file__).parent
# Expected conclusions were assigned by reading each product name/category, not
# by copying the classifier verdict. 1=accessory, 0=complete product.
SAMPLE = [
 ('CN:apple_cn:commodity:MFE94CH/A', 1, 'AirTag 属配件类'),
 ('GLOBAL:apple_support:model:118469', 1, 'VESA 支架转换器，非显示器本体'),
 ('GLOBAL:apple_support:model:111834', 0, 'AirPods 整套耳机，MagSafe 为随附充电盒'),
 ('GLOBAL:apple_support:model:111861', 0, 'AirPods 整套耳机，配无线充电盒'),
 ('CN:dji:sku:101241', 1, 'Mavic 智能飞行电池，非无人机'),
 ('CN:dji:sku:129711', 1, 'Action 快拆转接件，非运动相机'),
 ('CN:dji:sku:136791', 1, 'Inspire 折叠快拆桨，非无人机'),
 ('CN:dji:sku:164721', 0, 'Avata 畅飞套装含无人机；单电池版是套装配置'),
 ('CN:dji:sku:134691', 0, '完整可换镜头，按要求保留'),
 ('CN:dji:sku:158331', 0, '禅思云台相机整机，虽误归配件类仍保留'),
 ('CN:dji:sku:177861', 0, '两发一收的完整麦克风套装，充电盒为随附'),
 ('CN:dji:sku:109131', 1, 'Action 防水壳'),
 ('CN:mi_cn:product:10050015', 1, '净水器滤芯耗材，型号数字不构成整机'),
 ('CN:mi_cn:product:16549', 0, '1600G 净水器整机'),
 ('CN:mi_cn:product:13143', 0, '1.5 匹空调整机'),
 ('CN:mi_cn:product:14038', 1, '新风空调滤芯，非空调整机'),
 ('CN:mi_cn:product:10050050', 0, '电视整机'),
 ('CN:mi_cn:product:15323', 1, '电视移动支架，单机字样不能推翻支架主体'),
 ('CN:mi_cn:product:11374', 0, '扫拖机器人整机，误归配件类仍保留'),
 ('CN:mi_cn:product:12308', 1, '扫拖机器人 G1 配件'),
 ('CN:mi_cn:product:20585', 0, '显示器的多功能支架版，商品主体是显示器'),
 ('CN:mi_cn:product:25306', 0, '手环 11 整机，误归穿戴配件类仍保留'),
 ('CN:mi_cn:product:22458', 1, '手机专业影像套装为外接配件，非手机套机'),
 ('CN:mi_cn:product:19813', 1, 'Pad 钢化保护膜，非平板'),
 ('CN:mi_cn:product:10000108', 0, '小米平板 4 整机'),
 ('CN:apple_cn:commodity:MG314CH/A', 0, 'iPhone Air 手机整机'),
 ('CN:hp_cn:sku:7Y0Y4PC', 0, '惠普商务笔记本完整电脑'),
 ('CN:fuji:kit:x-e5-xf23mmf28-r-wr', 0, '富士机身和镜头套机'),
 ('CN:fuji:lens:xc13-33mmf35-63-ois', 0, '富士完整镜头，非镜头盖/遮光罩'),
 ('CN:mi_cn:product:21660', 0, '磁吸支架充电宝，商品主体为充电宝'),
]

def brand(r):
 return r.get('brand') or ('小米' if r['id'].startswith('CN:mi_cn:') else '其他')

def stats(rows):
 n = sum(bool((r.get('release') or {}).get('date')) for r in rows)
 return dict(total=len(rows), release_date=n, coverage=n/len(rows) if rows else None)

def groups(before, after, key):
 return {k: dict(before=stats([r for r in before if key(r)==k]), after=stats([r for r in after if key(r)==k]), excluded=sum(key(r)==k for r in before)-sum(key(r)==k for r in after)) for k in sorted({key(r) for r in before+after})}

def table(group):
 lines=['|分组|发布前|排除|发布后|日期数 前→后|覆盖率 老分母→新分母|', '|---|---:|---:|---:|---:|---:|']
 for key, v in group.items():
  a,b=v['before'],v['after']
  pct=lambda x: f"{x['coverage']*100:.2f}%" if x['coverage'] is not None else '—'
  lines.append(f"|{key}|{a['total']}|{v['excluded']}|{b['total']}|{a['release_date']}→{b['release_date']}|{pct(a)}→{pct(b)}|")
 return '\n'.join(lines)


def main():
 p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);a=p.parse_args()
 before=json.loads(a.before.read_text());after=json.loads(a.after.read_text())
 other=lambda r: classify(r)['basis']!='car'
 bo,ao=[r for r in before if other(r)],[r for r in after if other(r)]
 bc,ac=[r for r in before if not other(r)],[r for r in after if not other(r)]
 excluded=[r for r in before if classify(r)['accessory']]
 assert Counter(r['id'] for r in after)==Counter(r['id'] for r in before if not classify(r)['accessory'])
 assert bc==ac, 'cars changed'
 old={r['id']:r for r in before}
 # No dates are invented by changing the denominator.
 assert all(r.get('release')==old[r['id']].get('release') for r in after)
 samples=[]
 for key, expected, note in SAMPLE:
  r=old[key];d=classify(r)
  assert d['accessory']==bool(expected), (key,d,expected)
  samples.append(dict(id=key,model=r['name'],brand=brand(r),category=r.get('category'),categories=r.get('categories'),decision='配件' if d['accessory'] else '整机',basis=d,expected='配件' if expected else '整机',correct=True,review_note=note,source_url=r.get('source_url')))
 report=dict(before=stats(before),after=stats(after),other_brands_before=stats(bo),other_brands_after=stats(ao),
  excluded_count=len(excluded),excluded_by_category=dict(Counter(r.get('category') or '未分类' for r in excluded)),
  other_brands=groups(bo,ao,brand),cars=groups(bc,ac,brand),categories=groups(bo,ao,lambda r:r.get('category') or '未分类'),
  same_retained_dates=True,cars_unchanged=True,review_sha256=fingerprint(excluded),
  before_sha256=hashlib.sha256(a.before.read_bytes()).hexdigest(),after_sha256=hashlib.sha256(a.after.read_bytes()).hexdigest())
 for name,obj in [('report.json',report),('sample-30.json',samples),('excluded-decisions.json',[dict(id=r['id'],name=r['name'],brand=brand(r),category=r.get('category'),decision=classify(r)) for r in excluded])]:
  (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 (OUT/'baseline-goods.json.gz').write_bytes(gzip.compress(a.before.read_bytes(),mtime=0))
 lines=['# 全品牌配件发布过滤验收', '',
 '基线：2026-11-03 实际 `/api/meta`、`/api/goods` 和 data 分支均为 3968 条；不沿用历史 5448/963 的粗判规模。',
 '这里只改变发布范围；不修改 raw、采集档案与价格历史。完整被排除记录保存于 data 分支 `public/archive/accessories.json`，含 `excluded_reason: "accessory"` 与判定依据；现有来源档案继续保留。',
 '', '## 口径与规则', '',
 '汽车按 product_type/汽车 ID 或比亚迪、小米汽车品牌识别，完全跳过配件判定，单列表。其余品牌共用同一规则：整机主体白名单优先，然后品类（含 categories 并集）以“配件”结尾，或名称耗材词命中。数字本身不决定去留。相机机身、完整镜头、套机保留；明确的兼容机型名称不把滤芯/保护壳变成整机。',
 '整机随附充电盒、单/三电池版套装、显示器多功能支架版均保留。曾发现这些边界并修正规则后重跑；新增反例测试还覆盖“净水器（H1000G）滤芯”。',
 '覆盖率仅指 release.date 非空（含内部参考日期），不表示可公开展示或日期已证实。分子使用各自集合中实际有日期的条数；过滤不会新增日期。',
 '', '## 其它品牌（本次配件过滤的分母）', '', table(report['other_brands']), '',
 f"合计：{len(bo)} → {len(ao)}；日期 {stats(bo)['release_date']} → {stats(ao)['release_date']}；覆盖率 {stats(bo)['coverage']:.4%} → {stats(ao)['coverage']:.4%}。", '',
 '## 整车（汽车，完全独立于上述覆盖率）', '',table(report['cars']), '',
 f"发布文件总行数（含单列汽车）：{len(before)} → {len(after)}。总文件日期覆盖率 {stats(before)['release_date']}/{len(before)}={stats(before)['coverage']:.4%} → {stats(after)['release_date']}/{len(after)}={stats(after)['coverage']:.4%}；此口径仅供核对文件，不作为非汽车覆盖率。", '',
 '## 被排除记录按主品类分布', '', '|主品类|排除条数|','|---|---:|']
 lines += [f'|{k}|{v}|' for k,v in sorted(report['excluded_by_category'].items(),key=lambda p:(-p[1],p[0]))]
 lines += ['', '主品类分布可加总；所有分类并集参与判定，记录可能以家电/手机壳等为主分类、另带配件分类。全部明细见 excluded-decisions.json。', '', '## 按主品类的发布与覆盖率对照', '',table(report['categories']), '',
 '## 固定抽样 30 条', '',
 '逐条阅读型号与商品主体后给出预期结论，再与规则比较；供人工复核，不代表已有外部人工签字。Apple/大疆有真实配件样本，富士、惠普当前发布集无该类配件，分别提供真实整机/镜头样本，典型镜头盖/遮光罩/电脑包/扩展坞等另有跨品牌参数化测试，未伪造线上样本。', '',
 '|型号|判定|依据|结论对错 / 复核理由|','|---|---|---|---|']
 for s in samples:
  lines.append(f"|{s['model']}|{s['decision']}|{s['basis']['basis']}: {s['basis']['matched']}|正确：{s['review_note']}|")
 lines += ['', '每条完整 ID、原品类、分类并集和预期结论见 sample-30.json。', '', '## 门禁与复现', '',
 '统一 finalize 执行过滤；默认新增排除身份数 / 本轮非汽车身份分母 >5% 判红，恰好5%通过。缓存重放中已归档且不在上一轮发布集的配件不重复计新增，也不能稀释分母。已归档却重新进入上一轮发布集的记录再次排除会计为新增。',
 '首次迁移超过门禁，gate-red.log 记录真实阻断；首次仅通过人工可复核批次的精确 SHA-256 放行。校验值绑定 ID/名称/判定；任意新增不同记录使该校验值失效。后续采集默认无放行参数。门禁失败不更新发布文件或排除档案。',
 '本轮门禁按唯一身份计算，报表/API 按发布行数计算；原库有 3 组冲突 ID、8 行，保留原状，故非汽车门禁分母为 3946、报表分母为 3951。', '',
 '```sh', 'PYTHONPATH=src python3 docs/accessory-filter-20261103/report.py --before /tmp/accessory-before.json --after /path/to/public/goods.json', 'PYTHONPATH=src:scripts python3 -m pytest -q', '```', '',
 '上线结果、提交号、测试与 API 实际返回见 publication.md 和 online-verification.json。']
 (OUT/'README.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k in ('before','after','other_brands_before','other_brands_after','excluded_count','review_sha256')},ensure_ascii=False))
if __name__=='__main__':main()
