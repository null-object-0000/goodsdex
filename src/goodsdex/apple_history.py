"""沿官方文稿目录补齐历史技术规格；增量保留，价格任务不访问这些页面。"""

from __future__ import annotations

import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

from .sources import apple_support as source
from .sources.apple_cn import externalize
from .facts import CaptureStatus, now_iso
from .apple import write_json


def crawl_history(
    out=Path("data/categories"),
    raw=Path("data/apple/history/raw"),
    families=None,
    transport=source.fetch,
    max_age_days=7,
    workers=3,
    limit=0,
):
    out, raw = Path(out), Path(raw)
    report = {
        "fetched_at": now_iso(),
        "scope": "official documentation model references, historical and current; not purchasable CN SKUs",
        "limited": bool(limit),
        "discovery": {
            "completeness": "partial",
            "stop_reason": "official_documentation_scope",
        },
        "families": {},
        "pages": [],
        "errors": [],
        "attempt_errors": [],
        "coverage_gaps": [],
        "cached": 0,
        "by_locale": {},
    }
    locale_counts = Counter()
    total = 0

    def capture(url):
        cap = transport(url)
        if cap.status != CaptureStatus.SUCCESS:
            # Retry transient errors once; failed captures remain visible in report.
            failed = cap
            externalize(failed, raw)
            if failed.status in (
                CaptureStatus.TRANSPORT_ERROR,
                CaptureStatus.SOURCE_ERROR,
            ):
                cap = transport(url)
                return url, cap, failed
        return url, cap, None

    def save_cap(cap, intermediate=False):
        externalize(cap, raw)
        report["pages"].append(cap.to_dict())
        if cap.status != CaptureStatus.SUCCESS:
            report["attempt_errors" if intermediate else "errors"].append(
                {"url": cap.url, "status": cap.status.value, "error": cap.error}
            )

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for family in families or source.FAMILIES:
            path = out / f"Apple_history_{family}.json"
            old = json.loads(path.read_text()) if path.exists() else []
            merged = {r["product"]["product_id"]: r for r in old}
            threshold = datetime.fromisoformat(now_iso()) - timedelta(days=max_age_days)
            recent_docs = {
                url
                for r in old
                for url in r["product"].get(
                    "source_docs_urls", [r["product"]["source_docs_url"]]
                )
                if r.get("parser_version") == source.VERSION
                and datetime.fromisoformat(r["fetched_at"]) > threshold
            }
            seed = source.ORIGIN + "/zh-cn/docs/" + source.FAMILIES[family][0]
            cap = transport(seed)
            targets = (
                source.model_links(cap.response_raw, cap.url, family)
                if cap.status == CaptureStatus.SUCCESS
                else {}
            )
            if cap.status == CaptureStatus.SUCCESS and not targets:
                cap.status, cap.error = (
                    CaptureStatus.PARSE_ERROR,
                    "官方目录未解析出机型链接",
                )
            save_cap(cap)
            # Known historical documentation remains a source even if omitted from today's directory.
            for rec in old:
                docs_url = rec["product"]["source_docs_url"]
                if "/docs/" in docs_url:
                    targets.setdefault(docs_url, rec["product"]["name"])
            discovered = set(targets)
            seen = {seed}
            spec_targets = {}
            recent_specs = {
                url
                for r in old
                for url in r["product"].get(
                    "spec_request_urls",
                    [r["product"].get("spec_request_url", r["product"]["source_url"])],
                )
                if r.get("parser_version") == source.VERSION
                and datetime.fromisoformat(r["fetched_at"]) > threshold
            }
            if family in source.IDENTIFY:
                identify_cap = transport(
                    source.ORIGIN + "/zh-cn/" + source.IDENTIFY[family]
                )
                specs = (
                    source.specs_links(identify_cap.response_raw, identify_cap.url)
                    if identify_cap.status == CaptureStatus.SUCCESS
                    else []
                )
                if identify_cap.status == CaptureStatus.SUCCESS and not specs:
                    identify_cap.status, identify_cap.error = (
                        CaptureStatus.PARSE_ERROR,
                        "识别页未发现技术规格链接",
                    )
                save_cap(identify_cap)
                for spec in specs:
                    if spec not in recent_specs:
                        spec_targets[spec] = (identify_cap.url, identify_cap.to_dict())
                    else:
                        report["cached"] += 1
            # Watch family pages can contain sub-model cards; bounded recursive discovery.
            for depth in range(3):
                pending = sorted(set(targets) - seen)
                if not pending:
                    break
                seen.update(pending)
                to_fetch = [u for u in pending if u not in recent_docs]
                report["cached"] += len(pending) - len(to_fetch)
                if limit:
                    to_fetch = to_fetch[: max(0, limit - total)]
                total += len(to_fetch)
                next_targets = {}
                for requested, model_cap, failed in pool.map(capture, to_fetch):
                    if failed:
                        save_cap(failed, intermediate=True)
                    found = (
                        source.specs_links(model_cap.response_raw, model_cap.url)
                        if model_cap.status == CaptureStatus.SUCCESS
                        else []
                    )
                    children = (
                        source.model_links(
                            model_cap.response_raw, model_cap.url, family
                        )
                        if model_cap.status == CaptureStatus.SUCCESS
                        else {}
                    )
                    next_targets.update(children)
                    discovered.update(children)
                    if (
                        model_cap.status == CaptureStatus.SUCCESS
                        and not found
                        and not children
                    ):
                        report["coverage_gaps"].append(
                            {
                                "url": model_cap.url,
                                "reason": "机型页无技术规格链接或子机型",
                            }
                        )
                    save_cap(model_cap)
                    for spec_url in found:
                        # Same specification doc may be linked by several configurations.
                        if spec_url not in recent_specs:
                            spec_targets[spec_url] = (requested, model_cap.to_dict())
                targets = next_targets
            fresh_ids = set()
            for requested, spec_cap, failed in pool.map(capture, sorted(spec_targets)):
                if failed:
                    save_cap(failed, intermediate=True)
                rec = None
                if spec_cap.status == CaptureStatus.SUCCESS:
                    try:
                        docs_url, docs_capture = spec_targets[requested]
                        rec = source.parse_specs(spec_cap, family, docs_url)
                    except (ValueError, KeyError, TypeError) as exc:
                        spec_cap.status, spec_cap.error = (
                            CaptureStatus.PARSE_ERROR,
                            str(exc),
                        )
                save_cap(spec_cap)
                if rec:
                    rec["product"]["spec_request_url"] = requested
                    rec["captures"] = [spec_cap.to_dict(), docs_capture]
                    key = rec["product"]["product_id"]
                    previous = merged.get(key, {}).get("product", {})
                    rec["product"]["source_docs_urls"] = sorted(
                        set(
                            previous.get(
                                "source_docs_urls", [previous.get("source_docs_url")]
                            )
                            + [docs_url]
                        )
                        - {None}
                    )
                    rec["product"]["spec_request_urls"] = sorted(
                        set(
                            previous.get(
                                "spec_request_urls",
                                [
                                    previous.get(
                                        "spec_request_url", previous.get("source_url")
                                    )
                                ],
                            )
                            + [requested]
                        )
                        - {None}
                    )
                    merged[key] = rec
                    fresh_ids.add(key)
            # Missing or failed pages never delete earlier references or refresh their observation time.
            if merged:
                write_json(
                    path,
                    sorted(merged.values(), key=lambda r: r["product"]["product_id"]),
                )
            report["families"][family] = {
                "discovered_model_pages": len(discovered),
                "spec_pages": len(spec_targets),
                "updated": len(fresh_ids),
                "models": len(merged),
            }
            report["models"] = sum(f["models"] for f in report["families"].values())
            locale_counts.update(
                r["product"]["document_locale"] for r in merged.values()
            )
            report["by_locale"] = dict(locale_counts)
            write_json(raw.parent / "report.json", report)
            print(
                f"Apple history {family}: {len(merged)} model documents, {len(fresh_ids)} updated",
                flush=True,
            )
    return report
