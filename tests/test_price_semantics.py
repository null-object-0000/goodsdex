from goodsdex.price_semantics import normalize, apply, comparable, coverage, candidates


def test_partial_offer_cannot_be_minimum_and_keeps_source_fact():
    rows = apply([dict(id='diff',name='床垫升级补差价',price=10,price_kind='sku_sales_price'),
                  dict(id='whole',name='床垫120cm',price=2999)])
    assert rows[0]['price'] is None and rows[0]['source_price'] == 10
    assert rows[0]['price_kind'] == 'upgrade_diff' and rows[0]['price_missing']
    assert min(r['price'] for r in rows if comparable(r)) == 2999
    assert apply(rows) == rows
    assert coverage(rows)['price_kind'] == {'full':1,'upgrade_diff':1}


def test_deposit_extra_unknown_and_missing_never_restore_source_price():
    for name, kind in [('手机定金','deposit'),('枕套加价购','bundle_extra'),('床垫补差','upgrade_diff')]:
        r=normalize(dict(id='x',name=name,price=10,promo_price=8))
        assert r['price_kind']==kind and r['price'] is None and r['promo_price'] is None
    r=normalize(dict(id='x',name='不明报价',price=10,price_kind='unknown'))
    assert r['price'] is None and not comparable(r)
    assert normalize(dict(id='x',price=None))['price_kind']=='unknown'


def test_real_inexpensive_items_and_delivery_presale_not_partial():
    for name in ['预售7天控温被','升级款床垫','枕套两只装','毛巾','免定金枕头','含枕套组合装']:
        r=normalize(dict(id='x',name=name,price=35,price_kind='sku_sales_price'))
        assert r['price_kind']=='full' and comparable(r)
        assert r['price_basis_kind']=='sku_sales_price'
    assert not comparable(normalize(dict(id='x',price=99,sale_status='unavailable_option')))


def test_review_queue_does_not_claim_statistical_low_is_partial():
    rows=[dict(id=str(i),name='普通商品',category='床垫',price=p) for i,p in enumerate([10,2999,3999])]
    audit=candidates(rows)
    assert len(audit)==1 and audit[0]['suggested_price_kind']=='unknown'
    assert audit[0]['category_median']==2999


def test_finalizer_keeps_partial_records_and_shard_fields(tmp_path):
    import json
    from goodsdex.dedupe import finalize_public
    from goodsdex.shards import build_shards
    rows=[dict(id='CN:atour:spu:1984:sku:fee',name='床垫补差链接',source='atour',spu_id=1984,
        official_name='床垫',category='床垫',bundle=False,price=10,params={})]
    (tmp_path/'goods.json').write_text(json.dumps(rows))
    finalize_public(tmp_path, previous=rows)
    result=json.loads((tmp_path/'goods.json').read_text())
    assert len(result)==1 and result[0]['price'] is None
    meta=build_shards(tmp_path)
    assert meta['price_kind']=={'upgrade_diff':1}
    item=json.loads((tmp_path/'index/atour.json').read_text())['items'][0]
    assert item['price_missing'] and not item['price_comparable'] and item['source_price']==10


def test_upgrade_model_label_does_not_establish_upgrade_fee():
    r=normalize(dict(id='x',name='床垫（仅升级款）',price=10))
    assert r['price_kind']=='unknown' and r['source_price']==10 and r['price'] is None
    r=normalize(dict(id='CN:atour:spu:1984:sku:0105100044-2.0-JD28',name='床垫（仅升级款）',
        price=3079,official_sku_status=1))
    assert r['price_kind']=='full' and r['price']==3079


def test_price_history_does_not_reintroduce_partial_amount():
    from goodsdex.price_history import observation
    event=observation(dict(id='CN:atour:spu:1984:sku:x',name='床垫补差',price=10,
        fetched_at='2026-11-05T00:00:00Z'))
    assert event['price'] is None and event['missing_status']=='no_price'
