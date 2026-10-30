#!/usr/bin/env python3
"""按 id 合并 public/goods.json 中「同一商品、不同分类」的重复行。

默认是 dry-run：只读输入文件、打印清点结果和冲突清单，不写任何文件。
只有显式传入 --apply 才会写文件。

字段先按 public_fields 的明确映射归一；同 gid 的小米参数取无冲突并集。
三组已核例外始终保留原始行；任何其他真实值冲突仍整组保留。

合并规则（归一之后）：
  1. 同一 id 的所有行，除 ``category`` / ``categories`` / ``fetched_at`` 外，
     每个字段的规范 JSON 必须完全一致；只要有一个字段不同，整组跳过并列入冲突。
  2. ``fetched_at`` 是采集时间戳，不是商品属性；合并时取组内最大值。
  3. ``category`` 合并为 ``categories`` 数组：保留组内全部分类、去重，
     第一个元素是保留分类。保留分类按「越具体越靠前」排序：
     非导航伪分类 > 非兜底大类 > 全库出现行数更少 > 名字更长 > 字典序。
  4. 合并行的模板取 ``fetched_at`` 最新的那一行，其余字段原样保留；
     再逐字段验证「被合并行的所有非空值」都已存在于合并行，否则跳过该组。

用法：
    python3 scripts/dedupe_by_id.py                 # dry-run
    python3 scripts/dedupe_by_id.py --input FILE    # 指定输入，仍只读
    python3 scripts/dedupe_by_id.py --apply         # 真正写文件
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from goodsdex.public_fields import PROTECTED_IDS, prepare_group, normalize_public_row, assert_public_fields

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "public" / "goods.json"

# 这三个字段允许在组内不同：category 合并成数组，fetched_at 取最新。
EXEMPT_FIELDS = {"category", "categories", "fetched_at"}

# 导航入口 / 兜底大类 / 状态桶：它们不是具体商品分类，排序时永远排在叶分类之后。
NAV_PREFIX = "查看全部"
BROAD_BUCKETS = {"家电", "配件", "其他配件", "旧款机型"}

# 互动计数会随时间变化，不构成商品身份冲突；但仍不自动合并 params 不同的组。
VOLATILE_PARAM_KEYS = {"evaluate_total", "evaluate_real", "qa_total"}

EMPTY_MARKER = "<EMPTY>"


# --------------------------------------------------------------------------- #
# 基础工具
# --------------------------------------------------------------------------- #
def is_empty(value: Any) -> bool:
    """None / 空串 / 空列表 / 空对象视为空；0 和 False 是有效值，不算空。"""
    return value is None or value == "" or value == [] or value == {}


def canonical(value: Any) -> str:
    """字段值的规范形式：字典键排序，列表顺序保留。空值统一成哨兵。"""
    if is_empty(value):
        return EMPTY_MARKER
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def timestamp_sort_key(value: Any) -> tuple[int, float, str]:
    """可解析的时间优先；同组时间都不可解析时退回字符串序，保证确定性。"""
    parsed = parse_timestamp(value)
    if parsed is not None:
        return (1, parsed.timestamp(), str(value))
    return (0, float("-inf"), str(value or ""))


def newest_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(rows, key=lambda row: timestamp_sort_key(row.get("fetched_at")))


def newest_timestamp(rows: list[dict[str, Any]]) -> Any:
    values = [row.get("fetched_at") for row in rows if not is_empty(row.get("fetched_at"))]
    if not values:
        return None
    return max(values, key=timestamp_sort_key)


def category_rank(category: str, global_counts: collections.Counter) -> tuple:
    """越小越具体。导航伪分类和兜底大类永远排在具体叶分类后面。"""
    return (
        1 if category.startswith(NAV_PREFIX) else 0,
        1 if category in BROAD_BUCKETS else 0,
        global_counts.get(category, 0),
        -len(category),
        category,
    )


def ordered_categories(
    categories: Iterable[str], global_counts: collections.Counter
) -> list[str]:
    """按具体 -> 宽泛排序；调用方已保证去重。"""
    return sorted(categories, key=lambda item: category_rank(item, global_counts))


def short(value: Any, limit: int = 72) -> str:
    text = canonical(value).replace("\n", "\\n")
    return text if len(text) <= limit else text[:limit] + "…"


# --------------------------------------------------------------------------- #
# 数据读取与分组
# --------------------------------------------------------------------------- #
def load_rows(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"输入不是合法 JSON：{path}：{exc}") from exc
    if not isinstance(data, list):
        raise SystemExit(f"输入顶层必须是数组，实际是 {type(data).__name__}：{path}")
    for index, row in enumerate(data):
        if not isinstance(row, dict):
            raise SystemExit(f"第 {index + 1} 行不是对象：{type(row).__name__}")
    return data, digest


def group_by_id(rows: list[dict[str, Any]]) -> collections.OrderedDict[str, list[dict[str, Any]]]:
    groups: collections.OrderedDict[str, list[dict[str, Any]]] = collections.OrderedDict()
    for index, row in enumerate(rows):
        pid = row.get("id")
        if not isinstance(pid, str) or not pid.strip():
            raise SystemExit(f"第 {index + 1} 行缺少非空字符串 id")
        groups.setdefault(pid, []).append(row)
    return groups


# --------------------------------------------------------------------------- #
# 单组分析
# --------------------------------------------------------------------------- #
def collect_categories(rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """返回 (分类去重列表, 结构问题列表)。"""
    seen: list[str] = []
    problems: list[str] = []
    for row in rows:
        value = row.get("category")
        if isinstance(value, str) and value.strip():
            if value not in seen:
                seen.append(value)
        elif is_empty(value):
            problems.append("category 缺失或为空")
        else:
            problems.append("category 不是字符串")
        extra = row.get("categories")
        if extra is not None:
            if not isinstance(extra, list) or any(
                not isinstance(item, str) or not item.strip() for item in extra
            ):
                problems.append("categories 不是非空字符串数组")
            else:
                for item in extra:
                    if item not in seen:
                        seen.append(item)
    return seen, sorted(set(problems))


def differing_fields(rows: list[dict[str, Any]]) -> list[str]:
    fields: set[str] = set()
    for row in rows:
        fields.update(row.keys())
    differing = []
    for field in sorted(fields):
        if field in EXEMPT_FIELDS:
            continue
        if len({canonical(row.get(field)) for row in rows}) > 1:
            differing.append(field)
    return differing


def differing_param_keys(rows: list[dict[str, Any]]) -> list[str]:
    keys: set[str] = set()
    for row in rows:
        params = row.get("params")
        if isinstance(params, dict):
            keys.update(params.keys())
    changed = []
    for key in sorted(keys):
        values = set()
        for row in rows:
            params = row.get("params")
            values.add(canonical(params.get(key) if isinstance(params, dict) else None))
        if len(values) > 1:
            changed.append(key)
    return changed


def build_merged(
    rows: list[dict[str, Any]],
    categories: list[str],
    global_counts: collections.Counter,
) -> dict[str, Any]:
    """构造合并行；调用前必须已确认除豁免字段外没有冲突。"""
    ordered = ordered_categories(categories, global_counts)
    chosen = ordered[0]
    template = newest_row(rows)
    merged: dict[str, Any] = {}
    for key, value in template.items():
        if key == "category":
            merged["category"] = chosen
            merged["categories"] = ordered
        elif key == "categories":
            # categories 只在 category 后面插入一次；若模板顺序异常，兜底补在末尾。
            continue
        else:
            merged[key] = value
    if "categories" not in merged:
        merged["category"] = chosen
        merged["categories"] = ordered
    latest = newest_timestamp(rows)
    if latest is not None:
        merged["fetched_at"] = latest
    return merged


def verify_no_loss(
    merged: dict[str, Any],
    rows: list[dict[str, Any]],
    categories: list[str],
) -> list[str]:
    """证明合并不丢信息：逐行、逐字段检查非空值都出现在合并行里。"""
    problems: list[str] = []
    for row in rows:
        for field, value in row.items():
            if field == "category":
                continue
            if field == "categories":
                continue
            if field == "fetched_at":
                continue
            if is_empty(value):
                continue
            if canonical(merged.get(field)) != canonical(value):
                problems.append(
                    f"{field}: 丢弃行的非空值 {short(value)} 未出现在合并行"
                )
    if set(merged.get("categories") or []) != set(categories):
        problems.append("categories 并集不一致")
    if merged.get("category") not in categories:
        problems.append("保留 category 不在 categories 中")
    return problems


def analyze(
    groups: collections.OrderedDict[str, list[dict[str, Any]]],
    total_rows: int,
) -> dict[str, Any]:
    global_counts = collections.Counter(
        row.get("category") for row in groups.values() for row in row if isinstance(row.get("category"), str)
    )
    duplicate_groups = {
        pid: rows for pid, rows in groups.items() if len(rows) > 1
    }
    exact_duplicate_groups = sum(
        1
        for rows in duplicate_groups.values()
        if len({canonical(row) for row in rows}) == 1
    )

    safe: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    skipped_validation: list[dict[str, Any]] = []

    for pid, rows in duplicate_groups.items():
        original_rows = rows
        try:
            rows = prepare_group(rows)
        except ValueError:
            rows = original_rows
        differing = differing_fields(rows)
        categories, structural_problems = collect_categories(rows)
        if pid in PROTECTED_IDS:
            structural_problems.append(f"Protected group: {PROTECTED_IDS[pid]}")
        timestamp_problems = []
        for row in rows:
            value = row.get("fetched_at")
            if not is_empty(value) and parse_timestamp(value) is None:
                timestamp_problems.append(f"fetched_at 不是合法 ISO 8601: {value!r}")
        if differing or structural_problems or timestamp_problems:
            conflicts.append(
                {
                    "id": pid,
                    "rows": original_rows,
                    "fields": differing,
                    "problems": sorted(set(structural_problems + timestamp_problems)),
                }
            )
            continue
        if not categories:
            conflicts.append(
                {"id": pid, "rows": rows, "fields": [], "problems": ["没有可用分类"]}
            )
            continue

        merged = build_merged(rows, categories, global_counts)
        problems = verify_no_loss(merged, rows, categories)
        if problems:
            skipped_validation.append({"id": pid, "rows": rows, "problems": problems})
            continue
        safe.append(
            {
                "id": pid,
                "rows": original_rows,
                "categories": ordered_categories(categories, global_counts),
                "merged": merged,
            }
        )

    removed = sum(len(item["rows"]) - 1 for item in safe)
    after_rows = total_rows - removed
    # 所有非冲突的输出行（合并行 + 单行 id）都会补 categories；冲突组保持原样。
    backfill_rows = (
        after_rows
        - sum(len(item["rows"]) for item in conflicts)
        - sum(len(item["rows"]) for item in skipped_validation)
    )

    return {
        "global_counts": global_counts,
        "duplicate_groups": duplicate_groups,
        "exact_duplicate_groups": exact_duplicate_groups,
        "safe": safe,
        "conflicts": conflicts,
        "skipped_validation": skipped_validation,
        "removed": removed,
        "after_rows": after_rows,
        "backfill_rows": backfill_rows,
    }


# --------------------------------------------------------------------------- #
# 输出
# --------------------------------------------------------------------------- #
def pct(part: int, total: int) -> str:
    return f"{part * 100 / total:.2f}%" if total else "0.00%"


def row_count_distribution(groups: Iterable[list[dict[str, Any]]]) -> collections.Counter:
    return collections.Counter(len(rows) for rows in groups)


def print_distribution(counter: collections.Counter) -> str:
    return " / ".join(f"{size}行={counter[size]}组" for size in sorted(counter))


def conflict_kind(item: dict[str, Any]) -> str:
    """把冲突组按互斥形态归类，便于清点和排优先级。"""
    fields = item["fields"]
    if not fields:
        return "category_only_problem"
    if fields == ["params"]:
        keys = differing_param_keys(item["rows"])
        return "params_counters" if keys and set(keys) <= VOLATILE_PARAM_KEYS else "params_spec"
    if "params" in fields:
        return "params_plus_struct"
    return "struct_only"


def field_counts(conflicts: list[dict[str, Any]]) -> collections.Counter:
    counts: collections.Counter = collections.Counter()
    for item in conflicts:
        for field in item["fields"]:
            counts[field] += 1
        for problem in item["problems"]:
            counts[problem] += 1
    return counts


def print_report(
    input_path: Path,
    input_digest: str,
    rows: list[dict[str, Any]],
    groups: collections.OrderedDict[str, list[dict[str, Any]]],
    result: dict[str, Any],
    verbose_params: bool = False,
) -> None:
    total_rows = len(rows)
    unique_ids = len(groups)
    dup_groups = result["duplicate_groups"]
    dup_rows = sum(len(value) for value in dup_groups.values())
    safe = result["safe"]
    conflicts = result["conflicts"]
    skipped = result["skipped_validation"]
    safe_rows = sum(len(item["rows"]) for item in safe)
    conflict_rows = sum(len(item["rows"]) for item in conflicts)
    removed = result["removed"]
    after_rows = result["after_rows"]
    final_rows = total_rows - removed - sum(len(item["rows"]) - 1 for item in conflicts) - sum(
        len(item["rows"]) - 1 for item in skipped
    )
    fields_checked = sorted(
        {
            field
            for row in rows
            for field in row.keys()
            if field not in EXEMPT_FIELDS
        }
    )

    print("== 商品库重复 id 清理 / dry-run ==")
    print(f"输入: {input_path}")
    print(f"SHA-256: {input_digest}")
    print()
    print("[总量]")
    print(f"合并前行数: {total_rows:,}")
    print(f"唯一 id:    {unique_ids:,}")
    print(f"重复 id:    {len(dup_groups):,}")
    print(f"重复 id 涉及行: {dup_rows:,}")
    print(f"重复多出的行（可压缩量）: {dup_rows - len(dup_groups):,}")
    print(f"行数分布: {print_distribution(row_count_distribution(dup_groups.values()))}")
    print(f"逐字段硬校验: {len(fields_checked)} 个字段（排除 category/categories/fetched_at）")
    print()

    print("[1. 分类清点]")
    print(f"严格逐字段（含 fetched_at）完全相同的组: {result['exact_duplicate_groups']:,}")
    print(
        f"仅 category 不同（fetched_at 时间戳不同，视为采集元数据）: "
        f"{len(safe):,} 组 / {safe_rows:,} 行（{pct(len(safe), len(dup_groups))} 的重复 id）"
    )
    print(
        f"还有其他字段不同（整组跳过，绝不合并）: "
        f"{len(conflicts):,} 组 / {conflict_rows:,} 行（{pct(len(conflicts), len(dup_groups))} 的重复 id）"
    )
    counts = field_counts(conflicts)
    print("  差异字段（可重叠，按组计）:")
    for field, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"    {field}: {count:,} 组")
    buckets: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for item in conflicts:
        buckets[conflict_kind(item)].append(item)
    labels = [
        ("params_counters", "仅 params 不同（仅互动计数变化）"),
        ("params_spec", "仅 params 不同（含规格键/值变化）"),
        ("params_plus_struct", "params + 结构性字段都不同"),
        ("struct_only", "仅结构性字段不同（name/price/gid/image/from_container 等）"),
        ("category_only_problem", "category 本身缺失/类型错误"),
    ]
    print("  互斥拆分:")
    for key, label in labels:
        items = buckets.get(key, [])
        if items:
            rows_in_bucket = sum(len(item["rows"]) for item in items)
            print(f"    {label}: {len(items):,} 组 / {rows_in_bucket:,} 行")
    all_params = [
        item for item in conflicts if "params" in item["fields"]
    ]
    volatile_only = sum(
        1
        for item in all_params
        if (keys := differing_param_keys(item["rows"])) and set(keys) <= VOLATILE_PARAM_KEYS
    )
    nonvolatile = len(all_params) - volatile_only
    print(f"    params 差异合计: {len(all_params):,} 组（仅计数 {volatile_only:,} / 含规格 {nonvolatile:,}）")
    print(f"  可合并组行数分布: {print_distribution(row_count_distribution(item['rows'] for item in safe))}")
    print(f"  冲突组行数分布: {print_distribution(row_count_distribution(item['rows'] for item in conflicts))}")
    print()

    print("[2. 合并计划]")
    print(f"计划合并: {len(safe):,} 组 (id)")
    print(f"合并前: {total_rows:,} 行 / {unique_ids:,} 唯一 id")
    print(f"合并后: {total_rows:,} - {removed:,} = {after_rows:,} 行 / {unique_ids:,} 唯一 id")
    print(f"剩余重复 id（冲突未合并）: {len(conflicts):,} 组 / {conflict_rows:,} 行")
    print(f"若冲突组全部人工解决后的最终行数: {final_rows:,}")
    print(f"将补 categories 字段的行数: {result['backfill_rows']:,}（冲突组保持原样）")
    print("保留 category 规则: 导航伪分类/兜底大类最后；再按全库出现行数少、名字长、字典序")
    print("categories 规则: 去重、保留全部原分类（含父分类如「家电」）、保留 category 排第一")
    if safe:
        print("合并样例:")
        for item in safe[:3]:
            categories = item["categories"]
            print(
                f"  {item['id']}: {len(item['rows'])} 行 -> category={categories[0]!r} / "
                f"categories={categories!r}"
            )
    print()

    print("[3. 无信息损失校验]")
    print(f"可合并组通过逐字段并集校验: {len(safe):,}/{len(safe):,}")
    print(f"被丢弃行中的字段冲突: 0（冲突组不丢弃任何行）")
    print(f"校验失败而额外跳过的组: {len(skipped):,}")
    for item in skipped[:5]:
        print(f"  {item['id']}: {'; '.join(item['problems'][:3])}")
    print()

    print(f"[4. 冲突清单] 共 {len(conflicts):,} 组（整组保留，等待人工判断）")
    print(f"{'id':<38} {'行数':>4}  差异字段")
    print("-" * 100)
    for item in sorted(conflicts, key=lambda value: value["id"]):
        fields = ", ".join(item["fields"]) if item["fields"] else "—"
        problems = "；".join(item["problems"])
        suffix = f"；{problems}" if problems else ""
        print(f"{item['id']:<38} {len(item['rows']):>4}  {fields}{suffix}")
    print()

    structural = [
        item for item in conflicts if any(field != "params" for field in item["fields"])
    ]
    if structural:
        print(f"[5. 结构性字段冲突详情] 共 {len(structural):,} 组（不含仅 params 不同的组）")
        for item in sorted(structural, key=lambda value: value["id"]):
            print(f"  {item['id']}（{len(item['rows'])} 行）:")
            for field in item["fields"]:
                if field == "params":
                    keys = differing_param_keys(item["rows"])
                    print(f"    params: {len(keys)} 个键不同 -> {', '.join(keys[:12])}"
                          + (" …" if len(keys) > 12 else ""))
                else:
                    values = " | ".join(
                        short(row.get(field), 56) for row in item["rows"]
                    )
                    print(f"    {field}: {values}")
        print()

    nonvolatile_groups = []
    for item in conflicts:
        if "params" not in item["fields"]:
            continue
        keys = differing_param_keys(item["rows"])
        if not keys or not set(keys) <= VOLATILE_PARAM_KEYS:
            nonvolatile_groups.append((item, keys))
    if nonvolatile_groups:
        print(f"[6. params 非计数差异] 共 {len(nonvolatile_groups):,} 组（含规格键或值变化）")
        shown = sorted(nonvolatile_groups, key=lambda value: value[0]["id"])
        if not verbose_params:
            shown = shown[:6]
        for item, keys in shown:
            print(f"  {item['id']}（{len(item['rows'])} 行）: {', '.join(keys)}")
        if not verbose_params and len(nonvolatile_groups) > len(shown):
            print(f"  …… 其余 {len(nonvolatile_groups) - len(shown):,} 组用 --verbose-params 查看")
        print()

    print("[结论]")
    print(f"安全合并 {len(safe):,} 组后，行数 {total_rows:,} -> {after_rows:,}，唯一 id 仍为 {unique_ids:,}")
    print(f"合并不会丢字段：{len(safe):,} 组全部通过非空字段并集逐项比对")
    print(f"仍有 {len(conflicts):,} 组字段冲突，必须人工核验后才能合并")


# --------------------------------------------------------------------------- #
# 写文件
# --------------------------------------------------------------------------- #
def atomic_write(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=1)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def attach_categories(row: dict[str, Any], categories: list[str]) -> dict[str, Any]:
    """把 categories 放在 category 后面；已有 categories 的旧字段不重复输出。"""
    output: dict[str, Any] = {}
    inserted = False
    for key, value in row.items():
        if key == "category":
            output[key] = value
            output["categories"] = categories
            inserted = True
        elif key == "categories":
            continue
        else:
            output[key] = value
    if not inserted:
        output["categories"] = categories
    return output


def build_output(
    rows: list[dict[str, Any]],
    groups: collections.OrderedDict[str, list[dict[str, Any]]],
    result: dict[str, Any],
) -> list[dict[str, Any]]:
    """输出顺序沿用输入；重复组用合并行替换首次出现位置，其余行删除。"""
    merged_by_id = {item["id"]: item["merged"] for item in result["safe"]}
    conflict_ids = {item["id"] for item in result["conflicts"]}
    skipped_ids = {item["id"] for item in result["skipped_validation"]}
    output: list[dict[str, Any]] = []
    emitted: set[str] = set()
    for row in rows:
        pid = row["id"]
        if pid in merged_by_id:
            if pid not in emitted:
                output.append(merged_by_id[pid])
                emitted.add(pid)
            continue
        if pid in conflict_ids or pid in skipped_ids or pid in PROTECTED_IDS:
            # 冲突组保持原样：不合并、不补 categories，避免产生半合并状态。
            output.append(row)
            continue
        if pid not in emitted:
            new_row = normalize_public_row(row)
            if not isinstance(new_row.get("categories"), list):
                new_row = attach_categories(new_row, [new_row.get("category")])
            output.append(new_row)
            emitted.add(pid)
    return output


def category_membership(rows):
    """Match the API: union category membership per ID, explicit arrays take priority."""
    membership = {}
    for row in rows:
        values = row.get("categories") if isinstance(row.get("categories"), list) else [row.get("category")]
        if any(not isinstance(c, str) or not c for c in values):
            raise ValueError(f"Invalid category membership: {row['id']}")
        membership.setdefault(row["id"], set()).update(values)
    return membership


def validate_merge(before, after, result):
    """Fail closed; also used by tests to reject corrupted candidate output."""
    old, new = group_by_id(before), group_by_id(after)
    if old.keys() != new.keys():
        raise ValueError("Unique IDs changed")
    removed = sum(len(item["rows"]) - 1 for item in result["safe"])
    if len(after) != len(before) - removed or (removed and len(after) >= len(before)):
        raise ValueError("Row reduction differs from safe groups")
    conflicts = {item["id"]: item for item in result["conflicts"]}
    for pid, rows in old.items():
        if pid in conflicts:
            # Exact serialized values preserve missing/null/empty distinctions too.
            if json.dumps(rows, sort_keys=True) != json.dumps(new[pid], sort_keys=True):
                raise ValueError(f"Conflict modified: {pid}")
        elif len(new[pid]) != 1:
            raise ValueError(f"Safe duplicate remains: {pid}")
    for item in result["safe"]:
        pid = item["id"]
        prepared = prepare_group(old[pid])
        problems = verify_no_loss(new[pid][0], prepared, collect_categories(prepared)[0])
        if problems:
            raise ValueError(f"Merged field loss: {pid}: {problems}")
    def brands(groups):
        return dict(sorted(collections.Counter(
            rows[0].get("brand") or ("小米" if pid.startswith("CN:mi_cn:") else "未知")
            for pid, rows in groups.items()).items()))
    before_brands, after_brands = brands(old), brands(new)
    if before_brands != after_brands:
        raise ValueError("Brand facets changed")
    before_membership, after_membership = category_membership(before), category_membership(after)
    if before_membership != after_membership:
        raise ValueError("Per-ID category membership changed")
    counts = lambda membership: dict(sorted(collections.Counter(c for values in membership.values() for c in values).items()))
    before_counts, after_counts = counts(before_membership), counts(after_membership)
    if before_counts != after_counts:
        raise ValueError("Category facets changed")
    import random
    sampled = random.Random(20261029).sample(sorted(before_counts), min(5, len(before_counts)))
    queries = []
    for category in sampled:
        before_ids = {pid for pid, cats in before_membership.items() if category in cats}
        after_ids = {pid for pid, cats in after_membership.items() if category in cats}
        if before_ids != after_ids:
            raise ValueError(f"Category query changed: {category}")
        queries.append(dict(category=category, before=len(before_ids), after=len(after_ids)))
    return dict(before_rows=len(before), after_rows=len(after), before_unique_ids=len(old),
                after_unique_ids=len(new), merged_groups=len(result["safe"]), removed_rows=removed,
                conflict_groups=len(conflicts), conflict_rows=sum(len(old[pid]) for pid in conflicts),
                conflicts_unchanged=True, brands_before=before_brands, brands_after=after_brands, facets_before=before_counts, facets_after=after_counts,
                category_queries=queries)


def dedupe_rows(rows):
    """The single merge implementation for CLI and publication; no input mutation."""
    groups = group_by_id(rows)
    result = analyze(groups, len(rows))
    if result["skipped_validation"]:
        raise ValueError("Safe-group validation failed")
    output = build_output(rows, groups, result)
    audit = validate_merge(rows, output, result)
    audit["merged_ids"] = [item["id"] for item in result["safe"]]
    audit["conflicts"] = [dict(id=item["id"], type=PROTECTED_IDS.get(item["id"], "field_conflict"), fields=item["fields"],
                               row_count=len(item["rows"]), problems=item["problems"],
                               rows_sha256=hashlib.sha256(json.dumps(item["rows"], ensure_ascii=False, sort_keys=True).encode()).hexdigest())
                          for item in sorted(result["conflicts"], key=lambda item: item["id"])]
    return output, audit


def finalize_public(public, previous=None, retained_ids=()):
    """Run after all brand publishers and guards, before push/OSS upload."""
    from goodsdex.supplements import metadata
    public = Path(public)
    rows, digest = load_rows(public / "goods.json")
    from goodsdex.release_policy import remove_reviewed_non_goods, assert_no_empty_shells, allowed_deletions
    retained = remove_reviewed_non_goods(rows)
    assert_no_empty_shells(retained)
    output, audit = dedupe_rows(retained)
    assert_public_fields(output)
    if previous is not None:
        from goodsdex.release_policy import assert_no_lost_ids
        assert_no_lost_ids(previous, output, retained_ids)
    audit["input_sha256"] = digest
    audit["output_sha256"] = hashlib.sha256((json.dumps(output, ensure_ascii=False, indent=1) + "\n").encode()).hexdigest()
    audit_path = public / "merge-audit.json"
    combined = json.loads(audit_path.read_text()) if audit_path.exists() else {}
    # Keep the supplemental arithmetic audit under its original keys.
    if "deduplication" not in combined:
        combined["supplement_conflicts"] = combined.get("conflicts", [])
    combined["allowed_deletions"] = {**combined.get("allowed_deletions", {}), **allowed_deletions(rows, output)}
    combined["conflicts"] = audit["conflicts"]
    combined["deduplication"] = audit
    combined["published_count"] = len(output)
    meta_path = public / "meta.json"
    meta = metadata(output, json.loads(meta_path.read_text()) if meta_path.exists() else {})
    # All checks finish before the first release file is replaced.
    for name, value in (("goods.json", output), ("meta.json", meta), ("merge-audit.json", combined)):
        atomic_write(public / name, value)
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="按 id 合并 goods.json 的跨分类重复行；默认 dry-run，只读不写。"
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="输入 JSON（默认 public/goods.json）")
    parser.add_argument("--output", type=Path, default=None, help="--apply 时的输出路径（默认覆盖输入）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="只读并打印报告（默认）")
    mode.add_argument("--apply", action="store_true", help="显式写文件")
    parser.add_argument("--backup", action="store_true", help="--apply 覆盖原文件前生成 .bak 备份")
    parser.add_argument("--verbose-params", action="store_true", help="打印全部 params 非计数差异组")
    args = parser.parse_args(argv)

    input_path = args.input.expanduser().resolve()
    if not input_path.is_file():
        raise SystemExit(f"输入文件不存在：{input_path}")

    rows, digest = load_rows(input_path)
    groups = group_by_id(rows)
    result = analyze(groups, len(rows))

    print_report(input_path, digest, rows, groups, result, args.verbose_params)

    if not args.apply:
        after_digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
        print()
        print(f"[dry-run] 未写入任何文件；输入 SHA-256 前后一致: {'是' if after_digest == digest else '否'}")
        return 0

    output_path = (args.output or input_path).expanduser().resolve()
    output, validation = dedupe_rows(rows)
    output_ids = [row["id"] for row in output]
    allowed_duplicates = {
        item["id"]: len(item["rows"])
        for item in result["conflicts"] + result["skipped_validation"]
    }
    for pid, count in collections.Counter(output_ids).items():
        expected_count = allowed_duplicates.get(pid, 1)
        if count != expected_count:
            raise SystemExit(
                f"内部错误：id {pid} 输出 {count} 行，预期 {expected_count} 行"
            )
    expected_rows = len(groups) + sum(
        len(item["rows"]) - 1 for item in result["conflicts"]
    ) + sum(len(item["rows"]) - 1 for item in result["skipped_validation"])
    if len(output) != expected_rows:
        raise SystemExit(
            f"内部错误：输出行数 {len(output)} != 预期 {expected_rows}"
        )
    if args.backup and output_path == input_path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = input_path.with_name(input_path.name + f".bak-{stamp}")
        backup_path.write_bytes(input_path.read_bytes())
        print(f"[apply] 备份: {backup_path}")
    atomic_write(output_path, output)
    print()
    print(f"[apply] 已写入: {output_path}")
    print(f"[apply] 行数: {len(rows):,} -> {len(output):,}")
    print(f"[apply] SHA-256: {hashlib.sha256(output_path.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())