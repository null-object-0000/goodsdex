# L6 结构化第三方发布时间

入口：`scripts/release_lane_structured.py`，合并入口：`release_dates_run.py --lane L6`。
单独脚本默认扫描同一组 300 个唯一 gid，每站独立 checkpoint；失败也记录，不进行模糊映射。
统计单位是 gid 扫描，`queried` 单列有候选访问或搜索尝试的 gid，站点/搜索熔断不等于访问过每个商品页。

```sh
PYTHONPATH=src python3 scripts/release_lane_structured.py --goods /path/to/goods.json
# 显式复用状态和证据；无网络，不制造页面
PYTHONPATH=src python3 scripts/release_lane_structured.py --goods /path/to/goods.json --no-live
# 先阅读 sample-summary.json。确认要扩量后显式指定；不会因为抽样失败自动扩量
PYTHONPATH=src python3 scripts/release_lane_structured.py --goods /path/to/goods.json --full
```

统一 runner 对应 `--l6-full`。GitHub daily dispatch 的 lane=L6、l6_full=false 是默认抽样。
本机 cron 用 `GOODSDEX_RELEASE_LANE=L6`，显式全量还需 `GOODSDEX_L6_FULL=1`；使用当日目录，跨日会重新尝试。
如果工作目录内已有 source-state.json，同一身份指纹直接续跑；需要重新采集失败项时使用新的 output 目录。

映射要求标题/h1 的型号段完全一致，且正文也出现型号；仅正规化大小写、空白、全角与已列明的品牌别名。
没有数字的泛称、系列及无法证明配置的名字留空；HP 只按完整货号，不借战66/战99系列日期。
发现页不是参数页时，只跟随同一商品数字 ID 的参数链接；参数页身份还会重新验证。
ZOL `/series/` 页不作为单型号命中，搜索摘要不作日期证据。此策略会牺牲命中率，拒绝强配。

ZOL、太平洋、百科请求（含重定向）按域名串行，至少 2.1 秒；503/429 持久化退避到至少 10 秒并继续降速。
Bing 搜索独立 1 秒间隔，不减少商品站点的间隔。验证/挑战页面会熔断该入口，不尝试登录或绕过。
ZOL 站内 service 接口按 DSH 已知失败跳过；太平洋站内搜索能力探测单列在 site-search-capabilities.json。
该探测无法连接时，精确品牌+型号的 Bing/百度 site 搜索作为后备入口；不会把搜索无结果记成字段不存在。

日期只取字段名直接相邻的明确年月/年月日。百科日→月，原始日期存 raw_date；仅年份不入库。
结构化证据优先级 ZOL > 太平洋 > 百科，其余保存 alternates。官方（含隐藏日期）始终保留。
与 L5 或多站证据差距超过 45 天、月份区间跨越阈值时进入复核，撤下第三方及继承日期，保留 previous_release。
证据重放重新验证完整身份指纹、原页面字节 SHA256、标题/正文型号、字段和日期。
沿用库内嵌套 release 对象；release_precision/source/evidence/quote/confidence/cross_check 为兼容字段。

本次原始快照的 gzip 存在 before.json.gz；所有统计以当次快照为准，不把研究估计当实际产出。
result.json 和三个 state 文件保留每次查询、原始页面路径和失败原因。throttle/requests.jsonl 可复核请求间隔。
HP 抽查见 hp-quickspecs/result.json：5 货号关联 2 份系列 PDF，不视为 5 个独立系列样本。

发布候选同时携带 L6/result.json 和 captures；共享 publish job 在 finalizer 前从 `_data/docs/release-coverage/L6` 恢复证据包和原始页面。这样每天新采集的证据可在独立发布 job 中重新核验，后续价格等发布也能沿用最新发布集的证据，而不会退回代码仓库中的旧抽样包。
