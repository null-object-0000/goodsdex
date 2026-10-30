import json
from copy import deepcopy
import pytest
from goodsdex.backfill import apply
from goodsdex.supplements import DEFAULT_SUPPLEMENTS
from goodsdex.car_structure import migrate, expand_sources


def patch(**fields):
    return dict(id='x',source='s',source_url='https://example.org',captured_at='2026-10-30',field='historical_price',fields=fields)


def test_historical_price_never_populates_current_price():
    original=[dict(id='x',price=None)]
    result,_=apply(original,[patch(historical_price=99,price_kind='msrp_historical')])
    assert result[0]['price'] is None
    assert original==[dict(id='x',price=None)]
    with pytest.raises(ValueError): apply(original,[patch(price=99,historical_price=99,price_kind='msrp_historical')])
    for key in ('source','source_url','captured_at'):
        p=patch(historical_price=99,price_kind='msrp_historical');del p[key]
        with pytest.raises(ValueError):apply(original,[p])


def test_existing_value_and_provenance_win():
    for row in [dict(id='x',price=10),dict(id='x',historical_price=10),dict(id='x',price_source='official')]:
        result,audit=apply([row],[patch(historical_price=99,price_kind='msrp_historical',price_source='s')])
        assert result==[row]
        assert len(audit['skipped'])==1


def test_reference_image_cannot_claim_trim_scope():
    p=patch(image='url',image_scope='trim');p['field']='image'
    with pytest.raises(ValueError):apply([dict(id='x')],[p])


def test_historical_cars_roundtrip_and_tampering_fails():
    rows=[r for r in json.loads(DEFAULT_SUPPLEMENTS.read_text()) if r.get('source')=='pcauto']
    assert len(rows)==6
    assert sum(len(r['trims']) for r in rows)==23
    assert migrate(expand_sources(rows))==rows
    for r in rows:
        assert r['price'] is None
        assert r['model_year_confidence']=='third_party'
        assert all(t['price'] is None for t in r['trims'])
    bad=deepcopy(rows);bad[0]['trims'][0]['source_record']['model_year']=2020
    with pytest.raises(ValueError):migrate(bad)
