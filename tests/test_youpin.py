"""Cross-source identity, listing semantics and promotion regression gates."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import pytest
from goodsdex.youpin import apply_youpin, DEFAULT

ROOT = Path(__file__).resolve().parents[1]


def test_all_crosswalk_entries_retain_real_detail_identity_and_sku_evidence():
    manifest = json.loads(DEFAULT.read_text())
    assert manifest['sample_hits'] == 16 and manifest['sample_size'] == 50
    for item in manifest['items']:
        e = item['evidence']
        capture = json.loads(gzip.decompress((ROOT/e['capture_file']).read_bytes()))
        response = capture['response']
        canonical = json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode()
        assert hashlib.sha256(canonical).hexdigest() == e['response_json_sha256']
        g = response['data']['goods']
        assert g['goodsInfo']['gid'] == item['gid']
        assert g['goodsInfo']['name'] == item['youpin_name']
        assert g['goodsInfo']['firstTime'] == item['listed']['timestamp']
        for offer in item['offers']:
            sku = g['productInfo'][str(offer['pid'])]
            assert sku['name'] == offer['name'] and sku['skuId'] == offer['sku_id']
            single = g['priceInfo']['productsPriceInfo'].get(str(offer['pid']),{}).get('singlePrice') or {}
            if single.get('promotionPrice'):
                assert offer['price_kind'] == 'promotion'
                assert offer['price'] == single['price']/100


def test_h301_preserves_mall_gid_price_and_release_without_inventing_announcement():
    row = dict(id='CN:mi_cn:product:16725', name='米家负离子吹风机 H301',
               gid=2221501323, price=199, price_kind='sku', image='existing', category='吹风机')
    result = apply_youpin([row])[0]
    assert row['gid'] == result['gid'] == 2221501323
    assert result['youpin_gid'] == 156975
    assert result['price'] == 199 and result['price_kind'] == 'sku'
    assert result['image'] == 'existing' and result['category'] == '吹风机'
    assert result['release_upper_bound']['date'] == '2022-11-01'
    assert result['release_upper_bound']['event'] == 'channel_listing'
    assert not result.get('release')
    assert all(o['price_kind']=='promotion' and o['price']==125 for o in result['youpin_offers'])
    assert all(o['price_status']=='not_on_sale' for o in result['youpin_offers'])
    assert apply_youpin([result]) == [result]


def test_crosswalk_rejects_third_party_and_similar_variant_and_duplicate_ids():
    original = json.loads(DEFAULT.read_text())
    for change in ('brand','name','duplicate'):
        m=deepcopy(original)
        if change=='brand': m['items'][0]['brand_name']='第三方品牌'
        if change=='name': m['items'][0]['youpin_name'] += ' Pro'
        if change=='duplicate': m['items'].append(deepcopy(m['items'][0]))
        with pytest.raises(ValueError): apply_youpin([],m)


def test_model_relisting_counterexample_blocks_universal_release_promotion():
    evidence = json.loads((ROOT/'docs/youpin-20261105/semantics-reviewed.json').read_text())
    assert len(evidence)==20
    assert all(r['official_evidence']['source_type']=='official' for r in evidence)
    sound=next(r for r in evidence if r['gid']==161384)
    assert sound['delta_days']==765
    assert sound['verdict']=='listing_only_upper_bound'
