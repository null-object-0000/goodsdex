"""采集主流程：分类 -> 枚举 -> 多源采集(断言) -> 解析视图 -> 输出

三层（不丢证据）：
  Capture     原响应 + 状态（证据）
  Assertion   谁对哪个属性声明了什么
  View        按策略选出的展示值（可重建）

用法:
  python3 -m goodsdex.pipeline --list-categories
  python3 -m goodsdex.pipeline --category 吹风机
  python3 -m goodsdex.pipeline --pid 23966
"""
from __future__ import annotations
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .facts import Bundle, Capture, CaptureStatus, Subject
from .identity import build_identity
from .kind import classify_product_kind
from .resolve import build_view, guess_category
from .sources import mi_cn

# 已接入的数据源（--sources 只接受这些；未知源直接报错，不静默跳过）
SUPPORTED_SOURCES = {"mi_cn"}

DEFAULT_OUT = Path("data")
# 原响应超过此大小时**外置到内容寻址文件**（data/raw/<hash>.txt），
# 记录里只留引用。绝不截断 —— 截断会破坏 JSON 可解析性，
# 而依赖 JSON 的选图/拆分遇到坏快照会静默跳过，
# 使"损坏证据"伪装成"没有图"（实测 56 份快照因此损坏）。
RAW_INLINE_LIMIT = 200_000
RAW_STORE = Path("data/raw")


# 分类名 -> 安全文件名（含 / \ : * ? " < > | 等字符时替换）
_UNSAFE = str.maketrans({c: "_" for c in '/\\:*?"<>|'})


def safe_filename(name: str) -> str:
    return (name or "unnamed").translate(_UNSAFE).strip() or "unnamed"


def store_raw(raw: str, store: Path | None = None) -> tuple[str, str]:
    """保存原响应。返回 (内联内容, 外置文件的绝对路径)。

    小于阈值时内联返回（引用为空）；
    超过阈值时写入**内容寻址**文件（按 sha256 命名，天然去重），
    内联只留引用标记 + 前 2000 字符预览。

    绝不截断 —— 截断会破坏 JSON 可解析性，使损坏证据伪装成"没有图"。
    """
    import hashlib
    if len(raw) <= RAW_INLINE_LIMIT:
        return raw, ""
    store = Path(store) if store else RAW_STORE
    store.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    fp = (store / f"{digest[:2]}" / f"{digest}.txt").resolve()
    if not fp.exists():
        fp.parent.mkdir(parents=True, exist_ok=True)
        tmp = fp.with_suffix(".txt.tmp")
        tmp.write_text(raw, encoding="utf-8")
        tmp.replace(fp)
    preview = raw[:2000]
    return (f"<externalized:sha256={digest}:bytes={len(raw)}>\n{preview}",
            str(fp))


def collect_one(pid: str, name_hint: str = "", category: str = "",
                discovery: dict | None = None, variants: list | None = None) -> dict:
    """采集单个商品（产品级），返回含身份、证据、断言、视图的记录"""
    variants = variants or []
    prod = build_identity(pid, variants, market="CN", source="mi_cn",
                          category=category or "")
    if not prod.name:
        prod.name = name_hint

    bundle = Bundle(subject=Subject(subject_id=prod.product_id, kind="product",
                                    name=prod.name, market="CN",
                                    external_ids=prod.external_ids),
                    discovery=discovery or {})

    for fn in (mi_cn.fetch_mobile, mi_cn.fetch_pc):
        try:
            caps, assertions = fn(pid)
        except Exception as e:
            # 采集异常 -> 独立状态，不伪装成字段
            bundle.add_capture(Capture.make(
                "mi_cn", f"unknown://{fn.__name__}", "",
                status=CaptureStatus.TRANSPORT_ERROR, error=f"{type(e).__name__}: {e}"))
            continue
        for c in caps:
            # 大响应外置保存（不截断），并校验 hash 与内容一致
            if c.response_raw:
                c.response_raw, c.raw_ref = store_raw(c.response_raw)
                c.verify_integrity()
            bundle.add_capture(c)
        bundle.add_assertions(assertions)

    # subject 名称以官方产品名为准
    for a in bundle.assertions:
        if a.attribute == "name" and a.raw_value:
            bundle.subject.name = str(a.raw_value)
            # **必须同时写回 prod.name** —— pd = prod.to_dict() 取的是它。
            # 曾只更新 bundle.subject，导致容器展开来的子商品 name 为空
            # （name_hint 为空、identity 也推不出名字时）。
            if not prod.name:
                prod.name = str(a.raw_value)
            break

    cat = category or guess_category(bundle.subject.name)
    prod.category = prod.category or cat
    # 类型分流：整机 vs 配件耗材 vs 服务（服务/耗材没有换代意义，不进代际表）
    prod_kind = classify_product_kind(bundle.subject.name, cat)
    view = build_view(bundle.assertions, category=cat,
                      subject_id=bundle.subject.subject_id)

    # 变体级：价格与可购买属性挂在变体上（价格是时间序列，不是产品永久属性）
    price_observations = []
    for v in prod.variants:
        if v.external_ids.get("mi_cn.commodity_id"):
            price_observations.append({
                "variant_id": v.variant_id, "name": v.name,
                "attrs": v.attrs,
                "external_ids": v.external_ids,
            })

    pd = prod.to_dict()
    pd["kind"] = prod_kind

    # **容器展开**：若本商品是"系列容器"（goodsList[0] 不是自己），
    # 则把 goodsList 里的子商品也各自采成独立记录。
    #
    # 为什么不直接把容器记录改名了事：
    #   容器记录的 price/参数 来自 goodsList[0]，那是**子商品 A** 的数据。
    #   若只改名，就成了"名字是容器、数据是 A"，仍然名实不符。
    #   正确做法：容器记录**保留但标注**（数据归属写清），
    #   子商品各自成记录（它们自指、参数完整）。
    children = []
    for a in bundle.assertions:
        if a.attribute == "_container_children" and isinstance(a.raw_value, list):
            children = [str(x) for x in a.raw_value]
            break
    pd["is_container"] = bool(children)
    if children:
        # 数据归属：本条记录的 price/参数 实际属于 goodsList[0]。
        # 取 name 断言之外的方式：直接用第一条 price/sku 断言的值做线索，
        # 更准的是从 capture 里读 —— 但那要重解析，这里用容器标记本身
        # 已足够表达"本记录数据不属于自己的名字"。
        pd["container_children"] = children

    return {"product": pd,
            "captures": [c.to_dict() for c in bundle.captures],
            "assertions": [a.to_dict() for a in bundle.assertions],
            "view": view.to_dict(),
            "market_prices": price_observations,
            "discovery": bundle.discovery,
            "fetched_at": bundle.fetched_at}


def _summary(rec: dict) -> str:
    caps = rec["captures"]
    ok = sum(1 for c in caps if c["status"] == "success")
    bad = [c for c in caps if c["status"] not in ("success", "partial")]
    v = rec["view"]
    name = rec["product"].get("name") or "?"
    nvar = len(rec["product"].get("variants") or [])
    rej = f" 异常{len(bad)}" if bad else ""
    return (f"  {'✓' if ok else '✗'} {name[:24]:26s} 变体={nvar:<2d} "
            f"断言={len(rec['assertions']):3d} 视图值={len(v['values']):3d} "
            f"关系={len(v['relations']):2d} 缺口={len(v['gaps']):2d} "
            f"[{ok}/{len(caps)}源]{rej}")


def run_category(category: str, limit: int = 0, max_pages: int = 20,
                 workers: int = 4, outdir: Path = DEFAULT_OUT,
                 verbose: bool = True) -> list[dict]:
    cats = mi_cn.list_categories()
    kw = cats.get(category, category)
    if verbose:
        print(f"[1/3] 分类「{category}」-> 关键词「{kw}」")
    enum = mi_cn.enumerate_products(kw, max_pages=max_pages)
    prods, discovery = enum["items"], enum["discovery"]
    if limit:
        prods = prods[:limit]
    if verbose:
        print(f"      发现 {len(prods)} 个商品 | total={discovery['total_reported']} "
              f"完整性={discovery['completeness']} ({discovery['stop_reason']})")
        print("[2/3] 采集（断言层，保留原响应）")

    out: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(collect_one, p["pid"], p["name"], category, discovery,
                          p.get("variants")): p for p in prods}
        for f in as_completed(futs):
            p = futs[f]
            try:
                rec = f.result()
            except Exception as e:
                if verbose:
                    print(f"  ✗ {p['name'][:30]} {type(e).__name__}: {e}")
                continue
            out.append(rec)

    # **容器展开**：系列容器（如「米家冰箱 对开门系列」）的 goodsList
    # 装着若干**独立商品**（不同容量的冰箱），各自可采、参数完整。
    # 之前只解析 goodsList[0]，导致：容器记录名实不符（系列名 + 别的
    # 型号的数据），且其余型号全部漏采（实测 54 个容器）。
    containers = [r for r in out
                  if (r.get("product") or {}).get("is_container")]
    if containers:
        seen_pids = {(r.get("product") or {}).get("product_id") for r in out}
        kids_to_fetch = []
        for r in containers:
            for cid in (r["product"].get("container_children") or []):
                pid_full = f"CN:mi_cn:product:{cid}"
                if pid_full not in seen_pids:
                    kids_to_fetch.append(cid)
                    seen_pids.add(pid_full)
        if kids_to_fetch:
            if verbose:
                print(f"      容器展开: {len(containers)} 个容器 -> "
                      f"{len(kids_to_fetch)} 个子商品待采")
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futs = {ex.submit(collect_one, cid, "", category, discovery): cid
                        for cid in kids_to_fetch}
                for f in as_completed(futs):
                    try:
                        kid = f.result()
                    except Exception:
                        continue
                    kid["product"]["from_container"] = True
                    out.append(kid)

    # 类型分流 + 分类形态过滤（搜索是模糊匹配，同义词互相污染）
    from .kind import split_kinds
    from .category_filter import filter_category
    kinds = split_kinds(out)
    machines = kinds["machines"]
    kept, dropped = filter_category(machines, category)
    if verbose and (len(dropped) or len(kinds["counts"]) > 1):
        print(f"      类型分流: " + " ".join(
            f"{k}={v}" for k, v in kinds["counts"].items() if v))
        if dropped:
            print(f"      形态过滤: 保留 {len(kept)} 排除 {len(dropped)}")
    # 排除项不丢弃，随结果一起落盘（带 excluded_reason），便于复核
    for d in dropped:
        d["product"]["excluded"] = True
    # **配件/服务/未判定也要落盘**（带 kind 标记）。
    # 分流是指"不参与对比与残值"，不是"不留档"。
    # 曾写成 out = kept + dropped，把 657 配件 + 87 服务 + 466 未判定
    # 静默丢掉 —— 丢了就无法复核"到底抓到了什么"，
    # 也没法回答"官方有没有这个东西"。
    others = (kinds["buckets"]["accessory"] + kinds["buckets"]["service"]
              + kinds["buckets"]["unknown"])
    out = kept + dropped + others

    # 稳定排序（并发完成顺序不确定，输出必须可复现）
    out.sort(key=lambda r: r["product"]["product_id"])
    outdir.mkdir(parents=True, exist_ok=True)
    # 分类名可能含 / 等路径分隔符（如「毛巾/浴巾」），必须转义，
    # 否则会被当成目录层级，写文件时报 FileNotFoundError
    fp = outdir / f"{safe_filename(category)}.json"
    # **防清空保护**：只在"新结果为空"或"采集明显失败"时拒绝写入。
    # 不能用"条数缩水"当判据 —— 类型分流会把配件/服务剔出去，
    # 条数天然变少（实测：扫地机器人 85 -> 18，但新数据 0% 悬空、
    # 旧的 77% 悬空），用条数比较会把**正确的数据**挡在门外。
    if not out:
        failed = (discovery or {}).get("completeness") in ("failed", "unknown")
        if fp.exists() and failed:
            if verbose:
                print(f"\n⚠ 拒绝写入：新结果为空且采集状态为 "
                      f"{(discovery or {}).get('completeness')}，保留旧数据 {fp}")
            return out
    tmp = fp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(fp)          # 原子替换，避免写一半崩掉

    # **并入累积档案**（只增不减）。
    # 快照会被下次采集覆盖，但档案不会 —— 这是"下架也留档"的保障。
    # 实测：整分类覆盖时，下架商品在下次采集后**永久丢失**。
    try:
        from .archive import merge_archive
        st = merge_archive(category, out, archive_dir=outdir.parent / "archive")
        if verbose and (st["went_missing"] or st["revived"] or st["added"]):
            print(f"      档案: 共 {st['total']} 条（本次在场 {st['present']}，"
                  f"缺席 {st['missing']}）"
                  + (f" 新增 {st['added']}" if st["added"] else "")
                  + (f" 新缺席 {st['went_missing']}" if st["went_missing"] else "")
                  + (f" 复活 {st['revived']}" if st["revived"] else ""))
    except Exception as e:
        # 档案是长期资产，写失败不能静默 —— 但也不该拖垮本次采集
        print(f"      ⚠ 档案写入失败: {type(e).__name__}: {e}")

    if verbose:
        for r in out:
            print(_summary(r))
        print(f"\n[3/3] {len(out)} 款 -> {fp}")
        print(f"      发现: {json.dumps(discovery, ensure_ascii=False)}")
    return out


def run_pid(pid: str, outdir: Path = DEFAULT_OUT) -> dict:
    rec = collect_one(pid)
    outdir.mkdir(parents=True, exist_ok=True)
    fp = outdir / f"pid_{pid}.json"
    tmp = fp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(fp)
    v = rec["view"]
    print(f"{rec['product'].get('name')} | 断言 {len(rec['assertions'])} | "
          f"视图值 {len(v['values'])} | 关系 {len(v['relations'])} | 缺口 {len(v['gaps'])}")
    print(f"-> {fp}")
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(prog="goodsdex.pipeline", description="商品数据采集流程")
    ap.add_argument("--list-categories", action="store_true", help="列出可采集分类")
    ap.add_argument("--category", help="分类名（或直接给关键词）")
    ap.add_argument("--pid", help="单个商品 ID")
    ap.add_argument("--sources", default="mi_cn", help="数据源。当前已接入：mi_cn")
    ap.add_argument("--limit", type=int, default=0, help="限制商品数")
    ap.add_argument("--max-pages", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)

    srcs = tuple(s.strip() for s in a.sources.split(",") if s.strip())
    unknown = [s for s in srcs if s not in SUPPORTED_SOURCES]
    if unknown:
        ap.error(f"未接入的数据源: {', '.join(unknown)}。"
                 f"当前支持: {', '.join(sorted(SUPPORTED_SOURCES))}")

    if a.list_categories:
        cats = mi_cn.list_categories()
        print(f"官方分类 {len(cats)} 个：")
        for n, k in cats.items():
            print(f"  {n:24s} -> {k}")
        return 0
    if a.pid:
        run_pid(a.pid, Path(a.out))
        return 0
    if not a.category:
        ap.print_help()
        return 1
    run_category(a.category, a.limit, a.max_pages, a.workers, Path(a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
