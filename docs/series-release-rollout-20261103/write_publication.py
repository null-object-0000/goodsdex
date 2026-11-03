"""Render publication proof only after successful real API verification."""
import json
from pathlib import Path
P=Path(__file__).parent

def main():
 live=json.loads((P/'online-verification.json').read_text());pub=json.loads((P/'publication.json').read_text());data=json.loads((P/'published-data.json').read_text())
 assert pub['conclusion']=='success' and live['full_catalog_equal'] and live['series_count']==149
 lines=['# 发布及线上验收','','实现提交：`4565cf5ae66150d95b1e5e8c6974ee44dca9541a`。', '', '[实际发布任务](https://github.com/null-object-0000/goodsdex/actions/runs/41621428338)成功，经过正常 collect → candidate → 持锁合并 → 发布门禁 → finalize → data → OSS 镜像及读回校验。没有直接修改API数据，也没有强制推数据分支。', '',
 f"data 提交：`{data['commit']}`；商品SHA256：`{data['sha256']}`。发布商品与本地正常finalize逐值相同，2909行；小米1695行，149条独立series字段。发布前后除series字段外的每一个商品字段均相同；汽车全部保留。", '',
'本地基线470通过，最终472通过；[云端离线测试](https://github.com/null-object-0000/goodsdex/actions/runs/41621428507)464通过、8项既有live测试按配置跳过；发布门禁171通过。没有新增测试失败。详见测试日志、`cloud-tests.json`、`publication.json`、`publication-excerpt.log`。', '',
 f"线上验收时间：{live['checked_at']}。`/api/goods` 与 data 发布商品全量逐值相同，149条系列字段；3个真实详情接口的series及原release对象逐值相同。另核对21243、21378、23676三个应留空的型号详情，全部无series字段。线上API按15分钟周期同步，早先仍为17条的真实观测保留在 `online-attempts.jsonl`，不冒充发布失败或测试失败。", '',
'[完整线上核对JSON](online-verification.json)与 [真实API快照](api-goods-after.json.gz)。', '',
'## 三个真实ID摘录','','以下从真实 `/api/goods/<id>` 返回提取；省略其他字段，完整series对象及原release见JSON。']
 for row in live['details']:
  sr=row['series_release'];lines+=['',f"[{row['name']}]({row['url']})",'', '```json',json.dumps(dict(id=row['id'],series_release={k:sr[k] for k in ('date','granularity','level','batch_id','source','event','display')},release=row['release']),ensure_ascii=False,indent=2),'```']
 lines+=['','## 验收边界','','1728口径尚未闭环：线上和data真实小米分母均为1695，缺少另外33条对应身份，未构造样本或虚报覆盖率。当前1695条全部进入清单；本轮完成当日官方逐ID扫描复核、品类检索与目标批次正文审核，未声称对1546条留空记录逐型号穷尽网络检索。具体检索层级与缺失原因已逐名列出。']
 (P/'publication.md').write_text('\n'.join(lines)+'\n')
 print('publication evidence rendered')
if __name__=='__main__':main()
