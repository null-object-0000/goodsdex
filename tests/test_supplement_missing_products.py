"""Missing-only import preserves old prices, handles delisting, and resumes offline."""
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('supplement', ROOT / 'scripts/supplement_missing_products.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SupplementTests(unittest.TestCase):
    def test_append_only_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / 'data/supplement-20261027'
            def put(path, obj):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(obj))
            old_record = {'product': {'product_id': 'CN:mi_cn:product:1', 'name': '旧鼠标',
                            'category': '键鼠套装', 'kind': 'machine'},
                          'view': {'values': {'price': '123'}}, 'fetched_at': 'old'}
            old_archive = {'id': 'CN:mi_cn:product:1', 'price': '456', 'missing_since': 'old'}
            put(root / 'data/categories/键鼠套装.json', [old_record])
            put(root / 'data/archive/键鼠套装.json', {'category': '键鼠套装', 'items': {'CN:mi_cn:product:1': old_archive}})
            baseline = [{'id': 'CN:mi_cn:product:99', 'price': '789', 'custom': True}]
            put(root / 'data/coverage-20261026/baseline-committed-public.json', baseline)
            groups = [{'product_id': str(n), 'commodity_list': [{'commodity_id': str(n * 10), 'name': '测试滤芯 白色'}]} for n in (1, 2, 3, 4)]
            put(root / 'data/coverage-20261026/enumeration.json', {'键鼠套装': {'items': groups}})
            source = root / 'missing.csv'
            with source.open('w') as f:
                writer = csv.DictWriter(f, fieldnames=['product_id', 'name', 'in_committed', 'supplement_categories', 'tree_categories'])
                writer.writeheader()
                for n in (1, 2, 3, 4):
                    writer.writerow({'product_id': n, 'name': '测试滤芯', 'in_committed': 'False', 'supplement_categories': '键鼠套装'})
            calls = []
            class FakeClient:
                def __init__(self, limit):
                    assert limit == 300
                    self.rows = []
                def cached(self, url, body, headers):
                    pid = body[1]['productId']
                    calls.append((pid, body))
                    assert headers['X-User-Agent'] == 'channel/mishop platform/mishop.m'
                    event = {'status': 200, 'error': None, 'id': len(calls), 'request_body': body, 'fetched_at': '2026-10-27T00:00:00Z'}
                    self.rows.append(event)
                    if pid == '2':
                        return event, json.dumps({'code': 400480502, 'message': '该产品已下架'})
                    return event, json.dumps({'code': 0, 'data': {
                        'product': {'productId': int(pid), 'name': '测试滤芯', 'defaultGid': 333},
                        'goodsInfo': {'goodsList': [{'productId': int(pid) if pid == '3' else 999,
                            'price': '55', 'imgUrl': 'wrong', 'carouselList': [{'imgUrl': 'first-carousel'}],
                            'classParameters': {}}]}}})
            with patch.multiple(mod, ROOT=root, OUT=out, CSV=source), patch.object(mod.history, 'Client', FakeClient):
                with patch.object(mod.history, 'OUT', out), patch.object(mod.history, 'EVIDENCE', out / 'evidence'):
                    mod.main()
                    first_public = (root / 'public/goods.json').read_bytes()
                    mod.main()
                    self.assertEqual((root / 'public/goods.json').read_bytes(), first_public)
            self.assertEqual(len(calls), 5)  # local duplicate makes zero requests; resume makes zero requests
            records = json.loads((root / 'data/categories/键鼠套装.json').read_text())
            self.assertEqual(records[0], old_record)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[1]['product']['kind'], 'accessory')
            self.assertEqual(records[1]['view']['values']['img_url'], 'first-carousel')
            arch = json.loads((root / 'data/archive/键鼠套装.json').read_text())
            self.assertEqual(arch['items']['CN:mi_cn:product:1'], old_archive)
            results = json.loads((out / 'results.json').read_text())
            self.assertEqual([r['status'] for r in results], ['duplicate_local', 'delisted', 'added', 'identity_mismatch'])
            public = json.loads(first_public)
            self.assertEqual(public[0], baseline[0])
            self.assertEqual(len(public), 3)
            self.assertEqual(len(json.loads((out / 'public-added.json').read_text())), 2)


if __name__ == '__main__':
    unittest.main()
