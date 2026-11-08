from goodsdex.discovery_prices import normalize_discovery_quote
from goodsdex.price_semantics import normalize


def row(**values):
    return dict(id='CN:mi_cn:product:25802',name='REDMI Clip Neo',
                name_source={'identity_verified':True,'product_id':'25802'},**values)


def test_verified_initial_string_quote_is_full_numeric_price():
    result=normalize(normalize_discovery_quote(row(price='399',market_price='499')))
    assert result['price']==399 and result['market_price']==499
    assert result['price_kind']=='full' and result['price_comparable']


def test_fresh_price_refresh_repairs_only_verified_numeric_string_unknowns():
    result=normalize(normalize_discovery_quote(row(price=399,source_price='399',price_kind='unknown')))
    assert result['price']==399 and result['price_kind']=='full'
    for source in ({},{'identity_verified':True,'product_id':'other'}):
        before=row(price=399,source_price='399',price_kind='unknown');before['name_source']=source
        assert normalize(normalize_discovery_quote(before))['price'] is None
    explicit=row(price=399,source_price='399',price_kind='unknown',price_kind_evidence={'basis':'manual review'})
    assert normalize(normalize_discovery_quote(explicit))['price'] is None


def test_partial_payments_and_invalid_amounts_never_become_full_prices():
    for name in ('耳机 定金','耳机 补差价','仅升级'):
        before=row(price='99');before['name']=name
        assert normalize(normalize_discovery_quote(before))['price'] is None
    for value in ('nan','inf','-1','not a price'):
        assert normalize(normalize_discovery_quote(row(price=value)))['price'] is None
