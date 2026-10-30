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
