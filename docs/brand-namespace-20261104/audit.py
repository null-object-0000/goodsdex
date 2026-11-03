"""Audit a frozen release without changing IDs, product fields or meta semantics."""
import argparse
from collections import Counter
import json
from pathlib import Path

from goodsdex.brands import distribution, id_namespace, namespace_brand, normalize_brands


def audit(rows):
    after = normalize_brands(rows)
    prefixes = Counter()
    changes = []
    unknown = []
    known = 0
    for old, new in zip(rows, after):
        namespace = id_namespace(old['id'])
        prefix = ':'.join(namespace) + ':' if namespace else '(no namespace)'
        brand = namespace_brand(old['id'])
        prefixes[prefix, brand or '未知'] += 1
        if brand:
            known += 1
            assert (new['brand'], new['brand_source']) == (brand, 'id_prefix')
        # No cross-brand reassignment of already recognized brands.
        assert not old.get('brand') or old['brand'] == new['brand'], (old, new)
        assert {k: v for k, v in old.items() if k not in ('brand', 'brand_source')} == {
            k: v for k, v in new.items() if k not in ('brand', 'brand_source')}
        if (old.get('brand'), old.get('brand_source')) != (new['brand'], new['brand_source']):
            changes.append(dict(id=old['id'], before=[old.get('brand'), old.get('brand_source')],
                                after=[new['brand'], new['brand_source']]))
        if not new['brand']:
            unknown.append(dict(id=new['id'], name=new.get('name'), source=new.get('source'),
                                reason='命名空间、source、明确厂商名称前缀及已有品牌均无可识别信息'))
    assert normalize_brands(after) == after
    return dict(count=len(rows), before=distribution(rows), after=distribution(after),
                namespaces=[dict(prefix=p, count=c, brand=b) for (p, b), c in sorted(prefixes.items())],
                known_namespace_rows=known, known_namespace_coverage=1 if known else None,
                changed_brand_or_source_count=len(changes), change_samples=changes[:10],
                cross_brand_changes=0, non_brand_field_changes=0,
                unknown_count=len(unknown), unknown_samples=unknown[:10])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--public', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    result = {}
    combined = []
    for name in ('goods.json', 'goods-excluded.json'):
        path = args.public / name
        if not path.exists():
            result[name] = dict(missing=True)
            continue
        rows = json.loads(path.read_text())
        rows = rows if isinstance(rows, list) else rows['items']
        result[name] = audit(rows)
        combined.extend(rows)
    result['combined'] = audit(combined)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
