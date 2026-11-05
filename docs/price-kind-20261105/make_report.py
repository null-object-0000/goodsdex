"""Rebuild audit tables from saved official page text, snapshots, and publication receipt."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
load=lambda p:json.loads((ROOT/p).read_text())
low=load('low-input.json');pages={p['sid']:p for p in load('evidence/pages.json')}
audit=load('all-candidates.json')
rows=[]
for r in low:
    page=pages[r['spu_id']];s=next(s for s in page['selections'] if s['sku_no']==r['sku_no']);source=next(x for x in page['skus'] if x['skuNo']==r['sku_no'])
    assert source['salesPrice']==r['price']
    unknown=r['sku_no']=='0899000039-C2C-b'
    assert s['blocked']==unknown
    panel_price=float(re.search(r'￥([\d.]+)',s['text']).group(1))
    if not unknown:assert panel_price==r['price']
    note='该规格缺货不可选，未展示其可成交价；面板salesPrice=10。弹层2099为仍选中的120×200，不能移植给200×200' if unknown else f'活动价 ￥{r["price"]}；已选 '+ ' / '.join(s['selected'])
    rows.append(dict(**r,page_price=note,official_panel_price=source['salesPrice'],price_kind='unknown' if unknown else 'full',price_after=None if unknown else r['price'],
        decision='不能证实是补差或定金；整件价缺失，不进最低价' if unknown else '独立枕套/巾类/眼罩/抱枕或成套枕套整件售价，低于100合理；非加购加价',
        captured_at=s['at'],page_text=f'evidence/sku-{r["sku_no"]}.txt',screenshot=f'evidence/sku-{r["sku_no"]}.png'))
(ROOT/'atour-low-audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=1)+'\n')
def esc(x):return str(x).replace('|','\\|').replace('\n',' / ')
text='''# 亚朵低价与全库价格类型验收

30个低价SKU逐项核对，9个官方H5详情页、30次目标规格核对，另加1个3079元对照规格。29条是整件低价，1条价格语义无法确认。**10元不能证明是升级补差或定金，应标unknown，整件价null。**

官方来源：[普兰特床垫](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=1984)。22cm×200×200缺货不可选，SKU面板仍返回10；同页28cm×200×200也写“仅升级款”，但可选且弹层显示活动价3079。这是“仅升级款不必然是补差链接”的直接对照，不能编造“老客补10元升级”的故事，也不能把其他尺寸的2099元移植给该SKU。默认页“优惠后1889.1起”为券后展示，“优惠前2999起”为比较价；规格弹层120×200活动价2099，均不是10元规格的整件价。

## 发布与实现

非full一律price=null、price_missing=true、price_comparable=false；原金额保留在source_price，原promo_price另存source_promo_price。每次共享finalizer重放，亚朵collector出口也应用，价格观测再次防止部分支付金额写回历史。原price_kind中的SKU/起价/MSRP等语义迁入price_basis_kind，immutable source_record不改。类型覆盖full/deposit/upgrade_diff/bundle_extra/unknown；只有full且价格有效、可售、非retired/stale的记录可参与comparable统计。保留新采集的定金/补差记录，不沿用旧的定金排除行为；已有排除档案仍保留，不擅自恢复无关条目。

没有删除亚朵SKU：267条和38个SPU均保留。主详情与轻索引均带类型、缺价与比价资格；非full的price置空使现有API最低价/代表价消费者也不会误用，实际API分组函数验证见[consumer-validation](evidence/consumer-validation.json)：普兰特8个规格全部保留，最低价/代表价2099，10元记录referencePrice=null。

价格类型与可售状态分开；full表示完整商品报价，是否为当前可比价格另查price_comparable；原SKU面板9条不可用选项不会被comparable统计计入。未知类型不猜价。仅升级先保守unknown；3079元的已核对整件选项按精确ID、金额、可用状态放行，源金额改变须重新核查。

'''
receipt=ROOT/'publication.json'
if receipt.exists():
    p=load('publication.json');text+=f"发布代码：`{p['code_commit']}`；[发布run {p['run_id']}](https://github.com/null-object-0000/goodsdex/actions/runs/{p['run_id']})，结果 `{p['conclusion']}`。线上meta revision：`{p['revision']}`。\n\n"
    text+='线上price_kind分布：`'+json.dumps(p['price_kind'],ensure_ascii=False)+'`；其他枚举本次为0。总数'+str(p['count'])+'。\n\n'
    text+='修正后的真实字段：\n\n```json\n'+json.dumps(p['target'],ensure_ascii=False,indent=2)+'\n```\n\n'
text+='## 亚朵price<100逐条核查\n\n'
text+='入库前基准：data分支`0075b8cf`，goods sha256 `'+audit['goods_sha256']+'`；OSS及线上API另取快照逐条对账，30条金额全相等。data/OSS/API列按此顺序。工作目录旧public和_data中没有亚朵，不以其作为已发布事实。官方核查实际时间见每条captured_at；匿名读取、仅打开规格面板，未提交购物车、订单或支付。H5有时产生“登录失败”提示，但匿名详情及规格价格仍可读。\n\n'
text+='|sku_no|名称|各处入库价 data/OSS/API|页面实际价/原文|判定|证据|\n|---|---|---|---|---|---|\n'
for r in rows:
    prices='/'.join(str(x) for x in r['before_prices'].values())
    text+=f"|{r['sku_no']}|{esc(r['name'])}|{prices}|{esc(r['page_price'])}|{r['price_kind']}；{r['decision']}|[原文]({r['page_text']}) / [截图]({r['screenshot']})|\n"
text+='\n3079元对照：[页面原文](evidence/sku-0105100044-2.0-JD28.txt) / [截图](evidence/sku-0105100044-2.0-JD28.png)。官方解包响应按SPU保存在evidence/<spu>-business.json；页面首页正文、截图、全部选择状态及时间见[evidence/pages.json](evidence/pages.json)。原始salesPrice与活动/比较/券后价格不合并。\n\n'
text+='## 全库候选及前20条\n\n'
text+=f"当前发布{audit['published_count']}行（{audit['published_unique_count']}个ID），命中{audit['candidate_count']}条；另扫{audit['excluded_archive_count']}条已排除留档，命中{audit['excluded_candidate_count']}条；合计38条候选。留档与发布分组独立计算中位数。规则：名称含定金/订金/补差/差价/加购/仅升级，或正价严格小于其主category正价中位数的10%。0/null/负值不参与中位数；不限制最小样本数，样本数逐条披露。完整机器清单见[all-candidates.json](all-candidates.json)。这是复核队列，不代表38条全是差价。\n\n"
text+='|范围|ID|名称|原价|同类中位数|建议|\n|---|---|---|---:|---:|---|\n'
allrows=[('发布',r) for r in audit['candidates']]+[('已排除留档',r) for r in audit['excluded_candidates']]
for scope,r in allrows[:20]:
    suggestion=r['suggested_price_kind']+'；'+r['suggestion']
    text+=f"|{scope}|{r['id']}|{esc(r['name'])}|{r['price']}|{r['category_median']}|{suggestion}|\n"
text+='\n建议推广“类型门禁+低价审计”，不推广“低价即差价”的自动判定。灯泡/夜灯与大灯具、麦克风/电视盒子与整机、滤芯/软管与净水器共用粗类目，会产生正常价差；先拆实物品类、匹配相同配置/数量，再逐页核验。仅升级的3079元项已判full；10元项unknown。其余全库候选本轮只给清单，未猜价或批量修价。\n\n'
text+='## 验证\n\n[完整离线测试日志](evidence/tests.txt)：877 passed，8项live测试未执行；基线870 passed，无新红，原有1条pytest弃用警告。增加了部分支付不能当最低价、全价低价不误伤、预售交期非定金、unknown不回填、source_price留档、轻索引字段与共享finalizer重放、价格历史不回灌部分金额的测试。完整发布集本地finalize连续运行两次通过，3681条ID无丢失，price_kind full=2444、unknown=1237。最终线上值以publication.json及meta-after.json为准。\n'
(ROOT/'README.md').write_text(text)
print('wrote 30 rows and top20; official selections=31')
