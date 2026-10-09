"""查一个商品（或多个）的官方状态：在售 / 已下架 / ID 无效。

用途：回答「我这台还能不能买到 / 官方还有没有它的资料」这类问题。
**如实报告**——官方已删除就说已删除，不拿第三方数据拼一个看起来
完整的规格表（那正是本项目反复避免的自欺）。

用法:
  PYTHONPATH=src python3 scripts/product_status.py 13363
  PYTHONPATH=src python3 scripts/product_status.py 13363 9726 100059815902
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from goodsdex.facts import CaptureStatus  # noqa: E402
from goodsdex.sources import mi_cn  # noqa: E402

# 状态 -> 给用户看的中文说明（区分"有效结论"与"我们出错了"）
LABEL = {
    CaptureStatus.SUCCESS: ("✅ 在售", "官方正常返回商品数据"),
    CaptureStatus.PARTIAL: ("⚠️ 部分数据", "官方只返回了部分内容"),
    CaptureStatus.DELISTED: ("🚫 官方已下架",
                             "商品存在过，官方现已撤下 —— 规格不可得，"
                             "这是有效结论，不是抓取失败"),
    CaptureStatus.NOT_FOUND: ("❓ ID 无效",
                              "官方说不认识这个 ID —— 可能是我们查错了，"
                              "不代表官方没有该产品"),
    CaptureStatus.RATE_LIMITED: ("⏳ 被限流", "稍后重试，与商品状态无关"),
    CaptureStatus.TRANSPORT_ERROR: ("🌐 网络错误", "没连上，不是商品状态问题"),
    CaptureStatus.SOURCE_ERROR: ("❌ 官方报错", "未知业务错误"),
}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    rc = 0
    for pid in sys.argv[1:]:
        caps, ass = mi_cn.fetch_mobile(pid)
        c = caps[0]
        label, explain = LABEL.get(c.status, ("?", ""))
        name = next((a.raw_value for a in ass if a.attribute == "name"), None)
        print(f"{pid}")
        print(f"  {label}   {explain}")
        if name:
            print(f"  名称：{name}")
        if c.error:
            print(f"  官方原文：{c.error}")
        print()
        if c.status is CaptureStatus.DELISTED:
            rc = 2      # 区别于"出错"
    return rc


if __name__ == "__main__":
    sys.exit(main())
