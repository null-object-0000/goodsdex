"""Reject support-web metadata and keep failed retrieval distinct from absence."""
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('release_lane_hp',Path(__file__).parents[1]/'scripts/release_lane_hp.py')
lane = importlib.util.module_from_spec(spec);spec.loader.exec_module(lane)
ROW={'id':'CN:hp_cn:sku:7P2D5PC','part_number':'7P2D5PC'}

def capture(**fields):
    return {'status':200,'url':lane.ENDPOINT,'body':json.dumps({'data':{'devices':[{'productSpecs':{'data':{'productNumber':'7P2D5PC',**fields}}}]}})}

def test_web_release_is_not_product_release():
    r=lane.inspect(ROW,capture(webReleaseDate='20230301T00:00:00',webFirstPublishingDate='20230227T00:00:00'))
    assert r['release'] is None and r['missing_reason']=='no_release_field'
    assert r['none_reason']=='obtainable_not_collected'

def test_explicit_day_and_month_only():
    day_capture=capture(productLaunchDate='2023-03-29')
    day_capture.update(observed_at='2026-11-05T00:00:00Z',sha256='a'*64)
    day_release=lane.inspect(ROW,day_capture)['release']
    assert day_release['granularity']=='day'
    from goodsdex.release_dates import validate
    validate({'family':'exact-hp','ids':[ROW['id']],'release':day_release})
    assert lane.inspect(ROW,capture(productLaunchDate='2023-03'))['release']['granularity']=='month'
    assert lane.inspect(ROW,capture(productLaunchDate='2023'))['release'] is None
    assert lane.inspect(ROW,capture(productLaunchDate='2023-02-30'))['release'] is None

def test_identity_and_access():
    assert lane.inspect(ROW,{'status':404})['missing_reason']=='http_404'
    assert lane.inspect(ROW,{'status':403})['missing_reason']=='access_failed'
    assert lane.inspect(ROW,capture(productNumber='WRONG'))['missing_reason']=='model_mismatch'
    r=lane.inspect(ROW,{'status':200,'body':json.dumps({'code':406,'data':None,'message':'invalid captcha'})})
    assert r['missing_reason']=='access_failed'
