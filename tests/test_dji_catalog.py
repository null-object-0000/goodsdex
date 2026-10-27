import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from dji_catalog import parse_detail, append_only, classify
from dji_enumerate import links

FIXTURE=Path(__file__).parent/'fixtures/dji/air-3s.json'

class DJIParserTests(unittest.TestCase):
    def setUp(self):
        self.fixture=json.loads(FIXTURE.read_text())

    def source(self, fixture=None):
        f=fixture or self.fixture
        return '<script>window.__PRELOADED_STATE__ = '+json.dumps(f['state'])+';</script>'+''.join('<script type="application/ld+json">'+json.dumps(x)+'</script>' for x in f['json_ld'])

    def parse(self, fixture=None):
        return parse_detail(self.source(fixture),self.fixture['evidence_url'])

    def test_real_capture_identity_is_stable_across_runs_and_reordering(self):
        a,_,_=self.parse();b,_,_=self.parse()
        self.assertEqual([x['id'] for x in a],[x['id'] for x in b])
        f=copy.deepcopy(self.fixture);f['state']['products']['variants'].reverse()
        c,_,_=self.parse(f)
        self.assertEqual({x['id'] for x in a},{x['id'] for x in c})
        self.assertEqual(len(a),len({x['id'] for x in a}))
        for x in a:self.assertEqual(x['id'],f'CN:dji:sku:{x["mall_sku_id"]}')

    def test_actual_bundle_and_accessory_are_distinct_and_have_evidence(self):
        a,_,_=self.parse();d={x['mall_sku_id']:x for x in a}
        self.assertEqual(d[242601]['kind'],'machine')
        self.assertTrue(d[242601]['params']['套装组成'])
        self.assertTrue(d[173541]['params']['包装清单'])
        self.assertEqual(d[173601]['kind'],'accessory')
        self.assertEqual(d[173541]['name'],'DJI Air 3S 畅飞套装（普通遥控器）')
        self.assertEqual(d[173541]['price'],8788)
        self.assertNotEqual(d[173541]['id'],d[173571]['id'])
        for x in a:
            self.assertEqual(x['brand'],'大疆');self.assertEqual(x['price_kind'],'listing')
            self.assertIsNone(x['model_or_part_number'])
            self.assertNotIn('record_level',x)
            self.assertIn('?vid=',x['source_url'])
            self.assertIn('@origin.',x['image'])
            self.assertNotIn('官网系列规格',x['params'])

    def test_localized_cny_currency_is_valid_when_json_ld_is_absent(self):
        f=copy.deepcopy(self.fixture);f['json_ld']=[]
        f['state']['localization']={'country':'cn','currency':{'code':'CNY'}}
        a,_,_=self.parse(f);self.assertTrue(any(x['price'] for x in a))
        f['state']['localization']['currency']['code']='USD'
        a,_,_=self.parse(f);self.assertTrue(all(x['price'] is None for x in a))

    def test_off_sale_service_and_missing_identity_do_not_publish(self):
        f=copy.deepcopy(self.fixture)
        for v in f['state']['products']['variants']:v['status']={'code':'off_sale'}
        a,skip,_=self.parse(f)
        self.assertFalse(a);self.assertTrue(skip)

    def test_real_accessory_names_and_microphone_kits(self):
        samples=json.loads((FIXTURE.parent/'classification.json').read_text())
        kits={218901,197721,177861,218991}
        for v in samples:self.assertEqual(classify(v,{})[0],'machine' if v['id'] in kits else 'accessory',v['title'])

    def test_non_cny_and_zero_prices_are_null(self):
        f=copy.deepcopy(self.fixture)
        for v in f['state']['products']['variants']:v['price']=0
        a,_,_=self.parse(f);self.assertTrue(all(x['price'] is None for x in a))
        f['json_ld']=[]
        a,_,_=self.parse(f);self.assertTrue(all(x['price'] is None for x in a))

    def test_append_preserves_every_old_record_and_is_idempotent(self):
        old=[{'id':'CN:mi_cn:product:1','params':{'unchanged':[1,2]}}]
        rows,_,_=self.parse()
        merged,audit=append_only(old,rows)
        self.assertEqual(merged[0],old[0]);self.assertEqual(audit['missing_existing_ids'],0)
        again,audit2=append_only(merged,rows)
        self.assertEqual(merged,again);self.assertEqual(audit2['added'],0)
        duplicates,_=append_only(old+old,rows)
        self.assertEqual(duplicates[:2],old+old)

    def test_enumeration_keeps_official_links_only(self):
        self.assertEqual(links('href="/cn/product/abc?vid=123" https://store.dji.com/cn/list/power'),[
            'https://store.dji.com/cn/list/power','https://store.dji.com/cn/product/abc'])

if __name__=='__main__':unittest.main()
