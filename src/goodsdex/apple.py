"""Apple 采集、历史保留与增量公开发布。失败页保留旧记录和旧价格时间。"""

from __future__ import annotations
import json
import copy
import time
from pathlib import Path
from collections import Counter
from .sources import apple_cn as source
from .facts import CaptureStatus, now_iso
from .archive import merge_archive
from .publish import to_public


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)


def crawl(
    out=Path("data/categories"),
    raw=Path("data/apple/raw"),
    archive=Path("data/archive"),
    families=None,
    limit=0,
    transport=source.fetch,
    pause=0.15,
    prices_only=False,
):
    out = Path(out)
    raw = Path(raw)
    wanted = list(families or source.FAMILIES)
    targets = {}
    if prices_only:
        for family in wanted:
            path = out / f"Apple_{family}.json"
            if path.exists():
                for rec in json.loads(path.read_text()):
                    url = (rec.get("product") or {}).get("source_url")
                    if url:
                        targets[source.official_url(url)] = family
    if targets:
        seed_caps, spec_urls, marketing_urls = [], [], []
    else:
        targets, seed_caps, spec_urls, marketing_urls = source.discover(
            wanted, transport, pause
        )
    report = {
        "fetched_at": now_iso(),
        "scope": "Apple CN official currently listed preconfigured SKUs; excludes full CTO, band combinations and full accessory catalogue",
        "seeds": [],
        "pages": [],
        "limited": bool(limit),
        "prices_only": prices_only,
        "families": wanted,
        "spec_discovery": [],
    }
    for cap in seed_caps:
        source.externalize(cap, raw)
        report["seeds"].append(cap.to_dict())
    seen_urls = set()
    fresh = {family: [] for family in wanted}
    replacements = {family: set() for family in wanted}
    spec_cache = {}
    for url, family in sorted(targets.items()):
        if limit and len(report["pages"]) >= limit:
            break
        cap = transport(url)
        if cap.url in seen_urls:
            continue
        seen_urls.add(cap.url)
        records = []
        if cap.status == CaptureStatus.SUCCESS:
            try:
                records = source.parse_product(cap, family)
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                cap.status = CaptureStatus.PARSE_ERROR
                cap.error = str(exc)
        spec_url = source.specs_target(records, spec_urls) if not prices_only else None
        if not spec_url and records and not prices_only:
            landing = source.marketing_target(records, marketing_urls)
            if landing:
                mc = transport(landing)
                if mc.status == CaptureStatus.SUCCESS:
                    candidates = []
                    for href in source.links_in(mc.response_raw):
                        try:
                            u = source.official_url(href)
                            if u.endswith(("/specs/", "/tech-specs/")):
                                candidates.append(u)
                        except ValueError:
                            pass
                    spec_url = source.specs_target(records, candidates)
                source.externalize(mc, raw)
                report["spec_discovery"].append(mc.to_dict())
        if spec_url:
            if spec_url not in spec_cache:
                sc = transport(spec_url)
                table = (
                    source.parse_specs(sc.response_raw)
                    if sc.status == CaptureStatus.SUCCESS
                    else None
                )
                if sc.status == CaptureStatus.SUCCESS and table is None:
                    sc.status = CaptureStatus.PARSE_ERROR
                    sc.error = "未识别官方规格表，未自动拼接多型号参数"
                source.externalize(sc, raw)
                spec_cache[spec_url] = (sc, table)
            sc, table = spec_cache[spec_url]
            for rec in records:
                rec["captures"].append(sc.to_dict())
                if table:
                    a = source._assert(
                        sc,
                        rec["product"]["variant_id"],
                        "specs_table",
                        table,
                        "html:[role=table].techspecs",
                        {
                            "scope": "family_table; preserve model columns; not variant-specific values"
                        },
                    )
                    rec["assertions"].append(a.to_dict())
                    rec["view"]["values"]["specs_table"] = table
                    rec["view"]["selected_from"]["specs_table"] = a.assertion_id
        source.externalize(cap, raw)
        for rec in records:
            rec["captures"][0] = cap.to_dict()
        if records:
            fresh[family].extend(records)
            replacements[family].add(cap.url)
        report["pages"].append(
            {
                "url": cap.url,
                "family": family,
                "status": cap.status.value,
                "error": cap.error,
                "variants": len(records),
                "specs_url": spec_url,
                "specs_status": spec_cache[spec_url][0].status.value
                if spec_url
                else "not_collected",
            }
        )
        print(f"{family}: {cap.status.value} {len(records)} SKUs {cap.url}", flush=True)
        if pause:
            time.sleep(pause)
    report["variants"] = sum(len(x) for x in fresh.values())
    report["errors"] = sum(c["status"] != "success" for c in report["seeds"]) + sum(
        p["status"] != "success" for p in report["pages"]
    )
    report["spec_errors"] = sum(
        cap.status != CaptureStatus.SUCCESS for cap, _ in spec_cache.values()
    )
    report["specs_tables"] = sum(table is not None for _, table in spec_cache.values())
    for family in wanted:
        if not fresh[family]:
            continue  # 失败、空解析、未发现都不能清空旧快照。
        path = out / f"Apple_{family}.json"
        old = json.loads(path.read_text()) if path.exists() else []
        old_by_id = {r["product"].get("variant_id"): r for r in old}
        for rec in fresh[family]:
            prev = old_by_id.get(rec["product"]["variant_id"])
            if (
                prev
                and "specs_table" not in rec["view"]["values"]
                and "specs_table" in prev["view"]["values"]
            ):
                rec["view"]["values"]["specs_table"] = copy.deepcopy(
                    prev["view"]["values"]["specs_table"]
                )
                old_specs = [
                    a
                    for a in prev.get("assertions", [])
                    if a["attribute"] == "specs_table"
                ]
                rec["assertions"].extend(copy.deepcopy(old_specs))
                cap_ids = {a["capture_id"] for a in old_specs}
                rec["captures"].extend(
                    copy.deepcopy(c)
                    for c in prev.get("captures", [])
                    if c["capture_id"] in cap_ids
                    and c["capture_id"]
                    not in {x["capture_id"] for x in rec["captures"]}
                )
                if old_specs:
                    rec["view"]["selected_from"]["specs_table"] = old_specs[-1][
                        "assertion_id"
                    ]
            if (
                rec["view"]["values"].get("price") is None
                and prev
                and prev["view"]["values"].get("price") is not None
            ):
                rec["view"]["values"]["price"] = prev["view"]["values"]["price"]
                rec["product"]["price_status"] = "stale"
                rec["product"]["price_fetched_at"] = (
                    prev["product"].get("price_fetched_at") or prev["fetched_at"]
                )
                old_asserts = [
                    a for a in prev.get("assertions", []) if a["attribute"] == "price"
                ]
                rec["assertions"].extend(copy.deepcopy(old_asserts))
                ids = {a["capture_id"] for a in old_asserts}
                existing = {c["capture_id"] for c in rec["captures"]}
                rec["captures"].extend(
                    copy.deepcopy(c)
                    for c in prev.get("captures", [])
                    if c["capture_id"] in ids and c["capture_id"] not in existing
                )
                if old_asserts:
                    rec["view"]["selected_from"]["price"] = old_asserts[-1][
                        "assertion_id"
                    ]
        keep = [
            r
            for r in old
            if (r.get("product") or {}).get("source_url") not in replacements[family]
        ]
        merged = {r["product"]["variant_id"]: r for r in keep + fresh[family]}
        write_json(path, list(merged.values()))
        merge_archive(
            f"Apple_{family}",
            fresh[family],
            archive_dir=Path(archive),
            discovery={"completeness": "partial", "stop_reason": "scope_limited"},
        )
    write_json(raw.parent / "report.json", report)
    return report


def publish_apple(cats, out):
    """只替换观察到的 Apple 料号；不覆盖小米，不丢失败页/未再出现的旧料号。"""
    out = Path(out)
    gpath = out / "goods.json"
    items = json.loads(gpath.read_text()) if gpath.exists() else []
    incoming = []
    for path in sorted(Path(cats).glob("Apple_*.json")):
        incoming.extend(to_public(r) for r in json.loads(path.read_text()))
    by_id = {
        it["id"]: it
        for it in items
        if it.get("source") == source.SOURCE
        or str(it.get("id", "")).startswith("CN:apple_cn:")
    }
    # 其他品牌的历史重复条目暂不在此处处理，保持原样。
    others = [it for it in items if it.get("id") not in by_id]
    by_id.update({it["id"]: it for it in incoming})
    merged = others + list(by_id.values())
    merged.sort(key=lambda it: str(it.get("id")))
    write_json(gpath, merged)
    meta = {
        "generated_at": now_iso(),
        "count": len(merged),
        "by_kind": dict(Counter(it.get("kind") or "unknown" for it in merged)),
        "with_price": sum(it.get("price") is not None for it in merged),
        "note": "发布集含多品牌；价格范围见 price_kind，Apple 规格表保留型号列，不视为所有变体共享参数。",
    }
    write_json(out / "meta.json", meta)
    # Apple 时间序列独立命名空间，旧小米 gid 价格接口与历史保持兼容。
    stamp = now_iso()
    price_dir = out / "prices" / "apple"
    price_dir.mkdir(parents=True, exist_ok=True)
    # 用实际观察时间作为键；旧值不会在失败后伪装成一次新观察。
    observations = {
        it["id"]: {
            "price": it.get("price"),
            "currency": it.get("currency"),
            "price_kind": it.get("price_kind"),
            "fetched_at": it.get("price_fetched_at") or it.get("fetched_at"),
        }
        for it in by_id.values()
        if it.get("price") is not None
    }
    write_json(
        price_dir / "latest.json", {"generated_at": stamp, "prices": observations}
    )
    path = price_dir / (stamp[:7] + ".jsonl")
    seen = set()
    if path.exists():
        for line in path.read_text().splitlines():
            event = json.loads(line)
            seen.add((event["id"], event["fetched_at"]))
    with path.open("a", encoding="utf-8") as fp:
        for vid, value in sorted(observations.items()):
            if (vid, value["fetched_at"]) not in seen:
                fp.write(json.dumps({"id": vid, **value}, ensure_ascii=False) + "\n")
    return {"count": len(by_id), "total": len(merged)}
