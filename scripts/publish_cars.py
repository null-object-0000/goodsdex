"""Publish reviewed cars by ID. Offline; validate everything before writing."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
import math
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.supplements import metadata
from goodsdex.car_images import validate_historical_image

INPUT = ROOT / 'data/car-pilot-20261028'
HISTORY = ROOT / 'data/car-history-20261029/byd-verified.json'

SOURCES = (('byd-verified.json', '比亚迪', 'CN:byd:car:', 'www.bydauto.com.cn', 33),
           ('xiaomi-candidates.json', '小米汽车', 'CN:xiaomi_ev:car:', 'www.xiaomiev.com', 10))


def unique(rows, label, preserve_legacy=False):
    ids = [r.get('id') for r in rows]
    if any(not isinstance(key, str) or not key.strip() for key in ids):
        raise ValueError(f'{label}: missing id')
    duplicates = {key: n for key, n in Counter(ids).items() if n > 1}
    if duplicates and not (preserve_legacy and all(key.startswith(('CN:mi_cn:', 'CN:apple_cn:', 'CN:dji:', 'CN:fuji:')) for key in duplicates)):
        raise ValueError(f'{label}: duplicate IDs ({sum(n-1 for n in duplicates.values())} extra rows): ' +
                         json.dumps(dict(list(duplicates.items())[:5]), ensure_ascii=False))
    return dict(zip(ids, rows))


def prepare(previous, input_dir=INPUT, append_only=False):
    if any(r.get('schema') == 'car-product-v2' for r in previous):
        from goodsdex.car_structure import migrate, expand_sources
        result, audit = prepare(expand_sources(previous), input_dir, append_only)
        return migrate(result), audit
    gaps = json.loads((input_dir / 'parameter-gaps.json').read_text())
    excluded = {r['id'] for r in gaps}
    incoming = []
    for filename, brand, prefix, host, expected in SOURCES:
        rows = json.loads((input_dir / filename).read_text())
        if len(rows) != expected:
            raise ValueError(f'{filename}: expected {expected} reviewed configurations, got {len(rows)}')
        for original in rows:
            if original.get('id') in excluded:
                continue
            row = deepcopy(original)
            if row.get('brand') != brand or not str(row.get('id', '')).startswith(prefix):
                raise ValueError('Car ID/brand mismatch')
            for key in ('id', 'name', 'brand', 'price_kind', 'source_url'):
                if not isinstance(row.get(key), str) or not row[key].strip():
                    raise ValueError(f'Missing {key}: {row.get("id")}')
            if 'price' not in row:
                raise ValueError('Missing price field (explicit null required)')
            price = row['price']
            if price is not None and (isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0):
                raise ValueError('Invalid MSRP')
            if row['price_kind'] != ('none' if price is None else 'msrp'):
                raise ValueError('Price basis must be msrp, or none for null')
            url = urlsplit(row['source_url'])
            if url.scheme != 'https' or url.hostname != host:
                raise ValueError('Expected official source_url')
            if row.get('category') != '汽车' or row.get('product_type') != 'car' or not row.get('params'):
                raise ValueError('Missing car category/type/parameters')
            row['review_status'] = 'approved'
            incoming.append(row)
    fresh = unique(incoming, 'incoming')
    old = unique(previous, 'previous', preserve_legacy=True)
    # Approved identities are a separate, checked allowlist, including for daily captures.
    catalog = json.loads((ROOT / 'data/official/car-catalog.json').read_text())
    allowed = {r['id'] for r in catalog['rows']} - excluded
    if fresh.keys() != allowed:
        raise ValueError('Incoming IDs differ from reviewed allowlist')
    result = [{**row, **fresh[row['id']]} if row['id'] in fresh and not append_only else deepcopy(row) for row in previous]
    result.extend(deepcopy(row) for key, row in fresh.items() if key not in old)
    final = unique(result, 'result', preserve_legacy=True)
    expected_added = len(allowed - old.keys())
    added = len(final.keys() - old.keys())
    if added != expected_added or len(result) != len(previous) + added or not old.keys() <= final.keys():
        raise ValueError('Unexpected added count or lost IDs')
    # Every field of every non-target record, including implicit Xiaomi brands, is immutable.
    if [r for r in previous if r['id'] not in fresh] != [r for r in result if r['id'] not in fresh]:
        raise ValueError('Non-car records changed')
    if excluded & final.keys():
        raise ValueError('Known parameter gap would be published')
    audit = dict(old_total=len(previous), added=added, updated=sum(final[k] != old[k] for k in fresh.keys() & old.keys()), new_total=len(result))
    return result, audit


def prepare_history(previous, input_dir=None):
    if any(r.get('schema') == 'car-product-v2' for r in previous):
        from goodsdex.car_structure import migrate, expand_sources
        result, audit = prepare_history(expand_sources(previous), input_dir)
        return migrate(result), audit
    """Append the exact reviewed historical bundle, preserving every old object."""
    approved = json.loads(HISTORY.read_text())
    incoming = json.loads((input_dir / 'byd-verified.json').read_text()) if input_dir else approved
    fresh = unique(incoming, 'historical incoming')
    reviewed = unique(approved, 'historical reviewed')
    if fresh != reviewed:
        raise ValueError('Historical input differs from reviewed evidence bundle')
    old = unique(previous, 'previous', preserve_legacy=True)
    for row in incoming:
        if (row.get('brand') != '比亚迪' or not row['id'].startswith('CN:byd:car:')
                or row.get('model_year') != 2022 or '2022款' not in row.get('name', '')
                or row.get('record_level') != 'model_reference'
                or row.get('sale_status') != 'discontinued'
                or row.get('category') != '汽车' or row.get('product_type') != 'car'):
            raise ValueError('Invalid historical identity/status')
        if row.get('source_type') not in ('official', 'official_news', 'miit', 'third_party'):
            raise ValueError('Missing historical source type')
        if not row.get('source_note') or not row.get('parameter_sources'):
            raise ValueError('Missing historical provenance')
        url = urlsplit(row.get('source_url', ''))
        if url.scheme != 'https' or not url.hostname:
            raise ValueError('Invalid historical source URL')
        price = row.get('price')
        if price is None:
            if row.get('price_kind') != 'none':
                raise ValueError('Null historical price requires none')
        elif (row.get('price_kind') != 'msrp_historical'
              or row.get('price_source_type') not in ('official', 'official_news')
              or not row.get('price_source_url') or isinstance(price, bool)
              or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0):
            raise ValueError('Historical MSRP requires official price evidence')
        validate_historical_image(row)
        if set(row.get('params', {})) != set(row['parameter_sources']):
            raise ValueError('Every parameter requires provenance')
        if row['id'] in old:
            comparable = deepcopy(row)
            if old[row['id']].get('categories') == [row['category']] and 'categories' not in comparable:
                comparable['categories'] = [row['category']]
            if comparable != old[row['id']]:
                raise ValueError('Historical ID conflict; append-only publication refuses overwrite')
    result = deepcopy(previous)
    result.extend(deepcopy(r) for r in incoming if r['id'] not in old)
    unique(result, 'result', preserve_legacy=True)
    if result[:len(previous)] != previous:
        raise ValueError('Historical publication changed existing records')
    return result, dict(old_total=len(previous), added=len(result)-len(previous),
                        updated=0, new_total=len(result))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public', type=Path, default=ROOT / 'public')
    ap.add_argument('--input', type=Path, default=INPUT)
    ap.add_argument('--historical-only', action='store_true', help='Append the reviewed 2022 historical bundle only')
    ap.add_argument('--append-only', action='store_true', help='Preserve every existing record exactly')
    args = ap.parse_args()
    try:
        previous = json.loads((args.public / 'goods.json').read_text())
        result, audit = (prepare_history(previous, args.input if args.input != INPUT else None)
                         if args.historical_only else prepare(previous, args.input, args.append_only))
        meta = metadata(result, json.loads((args.public / 'meta.json').read_text()))
        # Validation is complete before either file is touched.
        for filename, value in [('goods.json', result), ('meta.json', meta)]:
            target = args.public / filename
            tmp = target.with_suffix('.json.tmp')
            tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n')
            tmp.replace(target)
        print(json.dumps(audit, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f'Car publication rejected: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
