"""Live-source-derived contract tests. No fabricated product facts."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import io
from goodsdex.shards import build_shards
from goodsdex.supplements import merge

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('hp',ROOT/'scripts/crawl_hp.py')
hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp)
FIXTURE=(ROOT/'tests/fixtures/hp/DC0F0PA.html').read_text()
URL='https://www.hpstore.cn/hp-omen-16-inch-gaming-laptop-ap1025ax-dc0f0pa.html'

class HPTests(unittest.TestCase):
    def row(self,text=FIXTURE):return hp.parse_product(text,URL,'2026-10-29T08:00:00Z')[0]
    def test_official_sku_and_specs(self):
        r=self.row();self.assertEqual(r['id'],'CN:hp_cn:sku:DC0F0PA')
        self.assertEqual(r['brand'],'惠普');self.assertEqual(r['category'],'笔记本')
        self.assertIn('9955HX',r['params']['CPU型号'])
        self.assertEqual(r['params']['variant_attrs']['dimensionCapacity']['label'],'16GB+1TB')
        self.assertIn('5060',r['params']['显卡'])
        self.assertIsNone(r['params']['上市时间']) # Magento createdAt is NOT a launch date.
        self.assertIsNone(r['market_price']);self.assertEqual(r['price_kind'],'store_sale')
        self.assertEqual(r['price'],12499)
    def test_sku_disagreement_fails(self):
        with self.assertRaises(ValueError):self.row(FIXTURE.replace('<h4 class="value">\n                                            DC0F0PA','<h4 class="value">\n                                            BADSKU'))
    def test_ancillary_price_cannot_be_used(self):
        r=self.row(FIXTURE.replace('id="product-price-17428"','id="product-price-other"'))
        self.assertIsNone(r['price']);self.assertIsNone(r['price_kind'])
    def test_out_of_scope_fails(self):
        with self.assertRaises(ValueError):self.row(FIXTURE.replace('笔记本电脑','打印机'))
    def test_absent_specs_stay_null(self):
        import re
        r=self.row(re.sub(r'<dd data-th="重量">[\s\S]+?</dd>','',FIXTURE))
        self.assertIsNone(r['params']['重量'])
    def test_merge_retains_failures_and_other_brand_byte_values(self):
        old=[dict(id='old',brand='富士',params={'x':['original']}),self.row()]
        before=copy.deepcopy(old);result=hp.merge_hp(old,[])
        self.assertEqual(result,before);self.assertEqual(old,before)
        with self.assertRaises(ValueError):hp.merge_hp(old,[dict(id='not-hp',brand='惠普')])
    def test_generic_publisher_preserves_hp(self):
        r=self.row();rows,_=merge([],[],[r]);self.assertEqual(rows,[r])
    def test_listing_follows_source_next_and_dedupes(self):
        text='<link rel="next" href="https://www.hpstore.cn/laptops-tablets.html?p=2" />'+2*'<a class="product-item-link" href="https://www.hpstore.cn/x.html">x</a>'
        urls,nxt=hp.listing(text,URL);self.assertEqual(len(urls),1);self.assertTrue(nxt.endswith('?p=2'))
    def test_image_rejects_undersized_and_bad_type(self):
        from PIL import Image
        im=Image.new('RGB',(799,900));b=io.BytesIO();im.save(b,format='PNG');raw=b.getvalue()+bytes(40000)
        class Client:
            def get(self,url):return raw,dict(status=200,content_type='image/png')
        result,info=hp.image_check(Client(),'https://media.hpstore.cn/x.png')
        self.assertIsNone(result);self.assertFalse(info['ok'])
    def test_no_loss_assertion_in_supplement_publisher(self):
        with self.assertRaises(ValueError):merge([],[],[dict(id='CN:mi_cn:product:1')])

class HourlyImageReuseTests(unittest.TestCase):
    def test_known_store_refresh_retains_historical_support_skus_without_fetching_them(self):
        import tempfile, sys
        sys.path.insert(0, str(ROOT/'scripts'))
        from build_hp_history import parse_capture
        capture = json.loads((ROOT/'tests/fixtures/hp/support-35L83PC.json').read_text())
        history = parse_capture(capture, dict(part_numbers=[], urls=[], capture_id='test', observed_at='first'))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            row, image = hp.parse_product(FIXTURE, URL, 'before')
            (out/'goods.json').write_text(json.dumps([row, history]))
            (out/'audit.json').write_text(json.dumps({'images': [{'url': image, 'ok': True}]}))
            calls = []
            class Client:
                requests = []
                def get(self, url):
                    calls.append(url)
                    assert url == URL
                    return FIXTURE.encode(), {'fetched_at': 'now'}
            with patch.object(sys, 'argv', ['crawl_hp', '--out', tmp, '--known-only', '--reuse-images']), \
                 patch.object(hp, 'Client', return_value=Client()):
                self.assertEqual(hp.main(), 0)
            saved = json.loads((out/'goods.json').read_text())
            self.assertEqual(calls, [URL])
            self.assertEqual(saved[1], history)

    def test_reuse_verified_image_still_fetches_fresh_sku_and_price(self):
        import tempfile
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            _, image = hp.parse_product(FIXTURE, URL, '2026-10-29T08:00:00Z')
            (out/'audit.json').write_text(json.dumps({'images': [{'url': image, 'ok': True}]}))
            class FakeClient:
                requests = []
                def get(self, url):
                    return FIXTURE.encode(), {'fetched_at': '2026-10-31T00:00:00Z'}
            with patch.object(sys, 'argv', ['crawl_hp.py', '--out', tmp, '--reuse-images', '--limit', '1']), \
                 patch.object(hp, 'Client', return_value=FakeClient()), \
                 patch.object(hp, 'listing', return_value=([URL], None)), \
                 patch.object(hp, 'image_check', side_effect=AssertionError('Known verified image must not be downloaded')):
                self.assertEqual(hp.main(), 0)
            rows = json.loads((out/'goods.json').read_text())
            self.assertEqual(rows[0]['price'], 12499)
            self.assertEqual(rows[0]['image'], image)
            self.assertEqual(rows[0]['fetched_at'], '2026-10-31T00:00:00Z')

    def test_known_only_refresh_never_enters_catalogue_discovery(self):
        import tempfile
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            row, image = hp.parse_product(FIXTURE, URL, '2026-10-29T08:00:00Z')
            (out/'goods.json').write_text(json.dumps([row]))
            (out/'audit.json').write_text(json.dumps({'images': [{'url': image, 'ok': True}]}))
            class FakeClient:
                requests = []
                def get(self, url):
                    if url != URL:
                        raise AssertionError('Hourly known-only refresh must not discover more URLs')
                    return FIXTURE.encode(), {'fetched_at': '2026-10-31T00:00:00Z'}
            with patch.object(sys, 'argv', ['crawl_hp.py', '--out', tmp, '--reuse-images', '--known-only']), \
                 patch.object(hp, 'Client', return_value=FakeClient()), \
                 patch.object(hp, 'listing', side_effect=AssertionError('No catalogue discovery')):
                self.assertEqual(hp.main(), 0)
            self.assertEqual(len(json.loads((out/'goods.json').read_text())), 1)

    def test_hourly_request_starts_stay_at_least_2_1_seconds_apart(self):
        client = hp.Client(interval_from_start=True)
        with patch.object(hp.time, 'monotonic', side_effect=[0.0, 0.0, 1.0, 2.1]), \
             patch.object(hp.time, 'sleep') as sleep, \
             patch.object(hp.urllib.request, 'build_opener') as opener:
            open_url = opener.return_value.open
            response = open_url.return_value.__enter__.return_value
            response.read.return_value = b'fresh response'
            response.url = URL
            response.status = 200
            response.headers.get.return_value = 'text/html'
            client.get(URL)
            client.get(URL)
            self.assertAlmostEqual(sleep.call_args_list[0].args[0], 0)
            self.assertAlmostEqual(sleep.call_args_list[1].args[0], 1.1)
            self.assertEqual(client.last['www.hpstore.cn'], 2.1)


class DelistingTests(unittest.TestCase):
    def evidence(self, final='https://www.hpstore.cn/laptops-tablets.html'):
        return dict(url=URL, final_url=final, status=200, fetched_at='2026-11-03T01:00:00Z',
                    redirects=[dict(url=URL, status=301, location=final)])

    def test_only_verified_catalogue_is_delisting(self):
        catalogue = '<a class="product-item-link" href="https://www.hpstore.cn/other.html">other</a>'
        self.assertIsNotNone(hp.delisting_evidence(catalogue, self.evidence()))
        for final in [URL, 'https://www.hpstore.cn/customer/account/login/',
                      'https://evil.example/laptops-tablets.html']:
            self.assertIsNone(hp.delisting_evidence(catalogue, self.evidence(final)))
        self.assertIsNone(hp.delisting_evidence('challenge', self.evidence()))
        self.assertIsNone(hp.delisting_evidence(FIXTURE, self.evidence()))
        with self.assertRaisesRegex(ValueError, 'missing'):
            hp.parse_product(catalogue, URL, 'now')

    def run_batch(self, count, removed=1, broken=False, repeat=False, gone_status=None):
        import tempfile
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            row, image = hp.parse_product(FIXTURE, URL, 'before')
            rows = []
            for n in range(count):
                r = copy.deepcopy(row)
                r.update(id='CN:hp_cn:sku:SKU'+str(n), part_number='SKU'+str(n),
                         source_url=URL+'?n='+str(n))
                rows.append(r)
            (out/'goods.json').write_text(json.dumps(rows))
            (out/'audit.json').write_text(json.dumps({'images': [{'url': image, 'ok': True}]}))
            calls = []
            class FakeClient:
                def __init__(self): self.requests = []
                def get(self, url):
                    calls.append(url)
                    n = int(url.split('=')[-1])
                    info = dict(url=url, final_url=url, status=200, fetched_at='now')
                    if n < removed:
                        if gone_status:
                            from urllib.error import HTTPError
                            raise HTTPError(url, gone_status, 'Gone', {}, io.BytesIO(b'Official page removed'))
                        info.update(final_url='https://www.hpstore.cn/laptops-tablets.html',
                                    redirects=[dict(status=301, location='https://www.hpstore.cn/laptops-tablets.html')])
                        return b'<a class="product-item-link" href="https://www.hpstore.cn/other.html">other</a>', info
                    return (b'broken PDP' if broken else FIXTURE.replace('DC0F0PA', 'SKU'+str(n)).encode()), info
            argv = ['crawl_hp.py', '--out', tmp, '--raw', str(out/'raw'), '--reuse-images', '--known-only']
            with patch.object(sys, 'argv', argv), patch.object(hp, 'Client', side_effect=lambda *a, **kw: FakeClient()):
                status = hp.main()
                audit = json.loads((out/'audit.json').read_text())
                saved = json.loads((out/'goods.json').read_text())
                if repeat:
                    first = copy.deepcopy(saved)
                    calls.clear()
                    self.assertEqual(hp.main(), 0)
                    self.assertEqual(len(calls), count-removed)
                    saved = json.loads((out/'goods.json').read_text())
                    self.assertEqual(saved[:removed], first[:removed])
                    audit = json.loads((out/'audit.json').read_text())
            return status, audit, saved, rows

    def test_archives_and_skips_confirmed_delistings(self):
        status, audit, saved, old = self.run_batch(20, repeat=True)
        self.assertEqual(status, 0)
        self.assertEqual(audit['errors'], [])
        self.assertEqual(audit['delisted_count'], 0)
        self.assertEqual(audit['delisted_skipped_count'], 1)
        self.assertEqual(len(saved), len(old))
        expected = hp.mark_delisted(old[0], saved[0]['delisted_evidence'])
        self.assertEqual(saved[0], expected)
        self.assertEqual(saved[0]['delisted_at'], 'now')

    def test_threshold_fails_without_checkpoint_bypass(self):
        status, audit, saved, old = self.run_batch(9)
        self.assertEqual(status, 1)
        self.assertEqual(audit['delisted_count'], 1)
        self.assertIn('10%', audit['errors'][0]['error'])
        self.assertEqual(saved, old)
        self.assertEqual(self.run_batch(10)[0], 0)  # exactly 10% allowed

    def test_live_pdp_parse_failure_still_fails(self):
        status, audit, saved, old = self.run_batch(20, broken=True)
        self.assertEqual(status, 1)
        self.assertEqual(audit['delisted_count'], 1)
        self.assertTrue(any('missing' in e['error'] for e in audit['errors']))
        self.assertEqual(saved, old)

    def test_known_http_404_and_410_retire_without_losing_configuration(self):
        for code in (404, 410):
            status, audit, saved, old = self.run_batch(10, gone_status=code)
            self.assertEqual(status, 0)
            self.assertEqual(audit['error_count'], 0)
            self.assertEqual(saved[0]['status'], 'retired')
            self.assertEqual(saved[0]['retirement_evidence']['status'], code)
            self.assertEqual(saved[0]['params'], old[0]['params'])
            self.assertEqual(saved[0]['image'], old[0]['image'])


class BlockedSourceTests(unittest.TestCase):
    def test_three_http_403_preserve_archive_public_meta_and_image_audit(self):
        import tempfile, sys
        from urllib.error import HTTPError
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'hp'; out.mkdir()
            public = Path(tmp) / 'public'; public.mkdir()
            row, image = hp.parse_product(FIXTURE, URL, 'before')
            rows = [dict(row, id=row['id']+str(i), source_url=URL+'?i='+str(i)) for i in range(5)]
            (out/'goods.json').write_text(json.dumps(rows))
            (out/'audit.json').write_text(json.dumps({'images': [{'url': image, 'ok': True}]}))
            (public/'goods.json').write_text(json.dumps(rows))
            (public/'meta.json').write_text('{"generated_at":"before"}')
            paths = [out/'goods.json', out/'audit.json', public/'goods.json', public/'meta.json']
            before = [p.read_bytes() for p in paths]
            calls = []
            class Blocked:
                requests = []
                def get(self, url):
                    calls.append(url)
                    raise HTTPError(url, 403, 'Forbidden', {}, None)
            with patch.object(sys, 'argv', ['crawl_hp', '--out', str(out), '--public', str(public), '--known-only']), patch.object(hp, 'Client', return_value=Blocked()):
                self.assertEqual(hp.main(), 0)
            self.assertEqual(len(calls), 3)
            self.assertEqual([p.read_bytes() for p in paths], before)
            status = json.loads((out/'collection-status.json').read_text())
            self.assertEqual(status['conclusion'], 'degraded')
            self.assertEqual(status['error'], 'blocked: 403 from hpstore.cn')

    def test_http_retry_is_bounded_and_backs_off(self):
        from urllib.error import HTTPError
        client = hp.Client()
        forbidden = HTTPError(URL, 403, 'Forbidden', {}, None)
        with patch.object(client, '_get_once', side_effect=forbidden) as get, patch.object(hp.time, 'sleep') as sleep:
            with self.assertRaises(HTTPError):
                client.get(URL)
            self.assertEqual(get.call_count, 3)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [5, 10])
        with patch.object(client, '_get_once', side_effect=[forbidden, (b'ok', {})]), patch.object(hp.time, 'sleep'):
            self.assertEqual(client.get(URL), (b'ok', {}))
