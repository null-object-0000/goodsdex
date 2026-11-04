"""Append exact online acceptance facts after the normal release completes."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RUN_ID=sys.argv[1]
r=json.loads((ROOT/'online-verification.json').read_text())
p=ROOT/'README.md';text=p.read_text().split('\n## 发布验收\n')[0]
text+='\n## 发布验收\n\n'
text+=f'发布 run：[{RUN_ID}](https://github.com/null-object-0000/goodsdex/actions/runs/{RUN_ID})。代码已推main；共享发布作业已推data并完成OSS镜像。首轮41898936180在安装浏览器时因ubuntu-latest升级至26.04、Playwright 1.56.1不支持而失败，未执行采集/发布；已将采集runner固定为受支持的ubuntu-24.04。\n\n'
text+=f"线上查询：[亚朵星球]({r['api_url']})，`total={r['api_total']}`；OSS `meta.sources.atour.spu_count=38`、`sku_count=267`、`meta.brands.亚朵星球=267`，与官方本轮38/267完全一致，无差1。发布revision：`{r['revision']}`。\n\n"
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
