"""商品类型判定：区分整机 / 配件耗材 / 服务，避免污染对比与残值。

来自实测的问题：搜索「壁挂空调」返回 89 条，其中混着
  "空调清洁保养服务""米家除醛滤网（中央空调）""空调检测服务"
这些不是可换代的整机，混进代际表和残值计算会得出荒谬结论。

同一搜索词下三类内容混排，必须在采集后明确分流：
  machine   整机（可换代、有残值）
  accessory 配件耗材（滤网/滤芯/滤袋/支架/遥控器…）
  service   服务（安装/清洁/保养/检测/延保…）
"""
from __future__ import annotations
import re

SERVICE_WORDS = (
    "服务", "安装", "清洗", "清洁", "保养", "检测", "维修", "延保", "换新服务",
    "上门", "质检", "回收服务", "调试", "改造", "拆除", "移机", "加氟",
)
ACCESSORY_WORDS = (
    "滤网", "滤芯", "滤袋", "尘盒", "集尘袋", "海帕", "hepa", "支架", "挂架",
    "底座", "遥控器", "充电器", "数据线", "保护壳", "保护套", "贴膜", "钢化膜",
    "电池", "刷头", "滚刷", "边刷", "滤棉", "香薰", "耗材", "配件", "墨盒",
    "硒鼓", "纸盒", "收纳", "背带", "腕带", "表带", "替换", "备件",
)
# 整机特征词（出现即强烈倾向整机，用于抵消误伤）
MACHINE_WORDS = (
    "空调", "冰箱", "洗衣机", "电视", "手机", "耳机", "吹风机", "扫地机", "吸尘器",
    "净化器", "电饭煲", "电磁炉", "水壶", "投影仪", "显示器", "路由器", "音箱",
    "门锁", "摄像机", "打印机", "跑步机", "剃须刀", "牙刷", "台灯", "风扇",
    "除湿机", "加湿器", "洗碗机", "净水器", "热水器", "平板", "手表", "手环",
    # 英文机型系列（官方产品名常以系列名开头）
    "Xiaomi", "xiaomi", "Redmi", "REDMI", "redmi", "MIX", "Civi", "Turbo",
    "Note", "Pro", "Max", "Ultra", "Buds", "Book", "Pad", "Watch", "Band",
)


def classify_product_kind(name: str, category: str = "") -> str:
    """判定商品类型：machine | accessory | service | unknown"""
    n = (name or "").strip()
    if not n:
        return "unknown"

    # 服务优先：名称里明确带"服务/安装/检测"等
    for w in SERVICE_WORDS:
        if w in n:
            # "换新服务" 属于服务；但"以旧换新"整机页也常见，需排除
            if w == "服务" and any(k in n for k in ("手机", "平板", "笔记本")) \
                    and "服务" not in n[:4]:
                continue
            return "service"

    for w in ACCESSORY_WORDS:
        if w in n:
            return "accessory"

    for w in MACHINE_WORDS:
        if w in n:
            return "machine"
    return "unknown"


def split_kinds(records: list[dict]) -> dict:
    """把采集结果按类型分流，并给出统计"""
    buckets = {"machine": [], "accessory": [], "service": [], "unknown": []}
    for r in records:
        nm = (r.get("product") or {}).get("name", "")
        k = classify_product_kind(nm, (r.get("product") or {}).get("category", ""))
        r["product"]["kind"] = k
        buckets[k].append(r)
    return {
        "buckets": buckets,
        "counts": {k: len(v) for k, v in buckets.items()},
        "machines": buckets["machine"],
    }
