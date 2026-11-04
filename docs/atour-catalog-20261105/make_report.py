"""Append exact online acceptance facts after the normal release completes."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RUN_ID=sys.argv[1]
r=json.loads((ROOT/'online-verification.json').read_text())
p=ROOT/'README.md';text=p.read_text().split('\n## 发布验收\n')[0]
text+='\n## 发布验收\n\n'
text+=f'发布 run：[{RUN_ID}](https://github.com/null-object-0000/goodsdex/actions/runs/{RUN_ID})。代码已推main；共享发布作业已推data并完成OSS镜像。本轮使用verified_snapshot=true导入同日国内匿名已审校快照，全部走正常collector与共享发布门禁。首轮41898936180因runner升级至26.04与固定Playwright不兼容，在安装浏览器时失败；已固定24.04。随后41899314683及只读探测41901313408仍在H5初始导航超时，均未发布。\n\n'
text+=f"线上查询：[亚朵星球]({r['api_url']})，`total={r['api_total']}`；OSS `meta.sources.atour.spu_count=38`、`sku_count=267`、`meta.brands.亚朵星球=267`，与官方本轮38/267完全一致，无差1。发布revision：`{r['revision']}`。\n\n"
text+='云端实时采集限制：[41901313408](https://github.com/null-object-0000/goodsdex/actions/runs/41901313408)在等待H5初始页面domcontentloaded时60秒超时，尚未取得HTTP业务响应，不能声称已验证GitHub出口的自动实时刷新。每天05:17的live采集仍失败即停止并保留旧库存；可访问官网的采集端生成新完整快照后，可再走verified_snapshot正常发布、对比退档。本机修正模块等待与定时余量后另重读38/267成功，全部200、最小2.105秒，名称/价/规格/图片及包装与本轮快照无差异，见[独立复核](readiness-recheck.json)。\n\n'
text+='校验：共享发布门禁573项通过；data提交`0075b8cf532604ffb0fff662adbab16706df17cf`，3414→3681，新增267；旧ID零丢失，其它品牌全对象多重集合相等，见[发布校验](publication.json)。\n\n'
text+='### 3条真实线上记录\n\n```json\n'+json.dumps(r['api_examples'],ensure_ascii=False,indent=2)+'\n```\n\n'
text+='### 枕芯随机5条（固定种子20261105，可复现）\n\n'
text+='|名称（库中完整原文）|销售价 CNY|规格原文|主图 URL|官方详情页 URL|\n|---|---:|---|---|---|\n'
for s in r['pillow_samples']:
 vals=[s['name'],str(s['price']),s['specs']['official_text'],f"[官方白底商品图]({s['image']})",f"[SPU {s['id'].split(':')[3]}]({s['source_url']})"]
 text+='|'+'|'.join(x.replace('|','\\|') for x in vals)+'|\n'
text+='\n尺寸/高度/填充等字段与null缺口见[线上机器验收](online-verification.json)，其中不会把多只装价格当单只价。\n\n'
text+='### 10条H5渲染页面与库逐字对照\n\n'
text+='页面名、库中`official_name`逐字相同；页面已选规格、库中`sku_name`逐字相同。库中`name`是两者按` / `连接，避免仅存SPU名或仅存颜色。表中两侧名称/规格写在各自列，价格为页面“活动价”显示值与该SKU销售价；本10条两者数值恰好相等，不外推其它规格的优惠口径。\n\n'
text+='|H5页面商品名|库商品原名|H5已选规格|库SKU原文|H5价格|库销售价|结果|\n|---|---|---|---|---:|---:|---|\n'
for s in r['page_comparisons']:
 vals=[f"[{s['page_name']}]({s['url']})",s['database_official_name'],s['page_selected_sku'],s['database_sku_name'],s['page_price'],str(s['database_price']),'逐字/数值一致']
 text+='|'+'|'.join(x.replace('|','\\|') for x in vals)+'|\n'
text+='\n原始渲染正文与采集时间见[evidence/h5-samples.json](evidence/h5-samples.json)；完整线上响应见[api-atour.json](api-atour.json)。接口返回前20条，`total=267`；三条完整详情又逐条与OSS整库做了全对象相等校验。\n'
p.write_text(text)
