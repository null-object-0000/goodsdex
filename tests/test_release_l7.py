"""L7 gates: model hallucinations, tampered captures, series and identity drift."""
from copy import deepcopy
import gzip
import hashlib
import pytest
from goodsdex import release_l7 as l7
from goodsdex.release_coverage import matrix, usable

def fixture(tmp_path,monkeypatch):
    monkeypatch.setattr(l7,'ROOT',tmp_path)
    row=dict(id='mi:test',name='米家吹风机 H501 SE',brand='小米',params={'型号':'H501 SE'})
    raw='<html><script>假型号2020年1月</script><body>2024/5/20 米家吹风机 H501 SE 今日发布。</body></html>'.encode()
    (tmp_path/'capture.gz').write_bytes(gzip.compress(raw))
    r=dict(date='2024-05',source='llm_verified',policy=l7.POLICY,granularity='month',level='product',confidence='medium',
           market='CN',event='announcement',crosscheck_status='page_verified',usage='fact',display_allowed=True,
           evidence=dict(url='https://www.ithome.com/0/1/2.htm',final_url='https://www.ithome.com/0/1/2.htm',
                         http_status=200,sha256=hashlib.sha256(raw).hexdigest(),captured_at='2026-11-05T00:00:00Z',
                         capture_file='capture.gz',quote='2024/5/20 米家吹风机 H501 SE 今日发布。'))
    e=dict(id=row['id'],name=row['name'],identity_sha256=l7.fingerprint(row),identity_terms=[row['name']],
           reviewed=True,identity_reason='完整精确型号含 SE',event_reason='当日发布原文',release=r)
    return row,e

def test_captured_month_and_mutually_exclusive_source(tmp_path,monkeypatch):
    row,e=fixture(tmp_path,monkeypatch)
    out=l7.apply([row],dict(policy=l7.POLICY,entries=[e]))
    assert usable(out[0]['release'])
    assert out[0]['release_source']=='llm_verified'
    c=matrix(out)['total']
    assert (c['llm_verified'],c['third_party'],c['official'],c['covered'])==(1,0,0,1)
    assert l7.apply(out,dict(policy=l7.POLICY,entries=[e]))==out

@pytest.mark.parametrize('mutation',[
    lambda e:e['release']['evidence'].update(http_status=403),
    lambda e:e['release']['evidence'].update(final_url='https://item.jd.com/1'),
    lambda e:e['release']['evidence'].update(sha256='0'*64),
    lambda e:e.update(identity_terms=['H501 Pro']),
    lambda e:e['release'].update(date='2024-06'),
    lambda e:e['release'].update(date='2024'),
    lambda e:e['release'].update(level='series'),
    lambda e:e.update(reviewed=False),
    lambda e:e['release']['evidence'].update(quote='2024/5/20 虚构型号发布'),
    lambda e:e.update(identity_terms=['假型号']),
])
def test_fail_closed(tmp_path,monkeypatch,mutation):
    row,e=fixture(tmp_path,monkeypatch);mutation(e)
    with pytest.raises(ValueError):l7.check(e,row)

def test_official_preserved_and_configuration_drift_skipped(tmp_path,monkeypatch):
    row,e=fixture(tmp_path,monkeypatch)
    row['release']=dict(source='official',date='2023-01',usage='disabled')
    assert l7.apply([row],dict(policy=l7.POLICY,entries=[e]))[0]['release']==row['release']
    row['params']['型号']='H501 Pro'
    assert l7.apply([row],dict(policy=l7.POLICY,entries=[e]))==[row]

@pytest.mark.parametrize('url',['https://item.jd.com/1','https://forum.ithome.com/x','https://tieba.baidu.com/x',
    'https://ithome.com.evil.test/x','https://u:p@www.ithome.com/x','https://www.ithome.com:8080/x'])
def test_source_whitelist(url):
    assert not l7.publisher(url)

def test_month_numeric_boundary_and_script_head_are_not_body_evidence():
    assert not l7.has_month('2024/11/20','2024-01')
    assert l7.has_month('2024/1/20','2024-01')
    assert l7.body_text(b'<head><title>Model 2024/1</title></head><body>Other</body>')=='Other'


@pytest.mark.parametrize('url', [
    'https://bbs.xiaomi.cn/thread/123',
    'https://www.byd.com/cn/news/123',
    'https://h5mall.yaduo.com/goods/detail/123',
])
def test_explicit_official_channels(url):
    assert l7.publisher(url)

def test_official_shop_needs_launch_language(tmp_path, monkeypatch):
    row,e=fixture(tmp_path,monkeypatch)
    e['release']['evidence'].update(url='https://www.mi.com/shop/buy/detail?product_id=1',
                                  final_url='https://www.mi.com/shop/buy/detail?product_id=1')
    with pytest.raises(ValueError, match='shop_no_launch_statement'):
        l7.check(e,row)


def test_car_guard_allows_only_captured_l7_replay(tmp_path, monkeypatch):
    import json
    from goodsdex.cars import assert_cars_unchanged
    from goodsdex.release_tolerance import apply as select
    row,e=fixture(tmp_path,monkeypatch)
    row.update(id='CN:byd:car:test',price=100000,product_type='car')
    e.update(id=row['id'],identity_sha256=l7.fingerprint(row))
    bundle=tmp_path/'reviewed.json'
    bundle.write_text(json.dumps(dict(policy=l7.POLICY,entries=[e])))
    monkeypatch.setattr(l7,'INPUT',bundle)
    result=select(l7.apply([row]))
    assert result != [row]
    assert_cars_unchanged([row],result)
    altered=deepcopy(result);altered[0]['price']+=1
    with pytest.raises(ValueError,match='car objects'):
        assert_cars_unchanged([row],altered)
    altered=deepcopy(result);altered[0]['release']['date']='2024-06'
    with pytest.raises(ValueError,match='car objects'):
        assert_cars_unchanged([row],altered)


def test_chinese_month_followed_by_day_is_valid_but_other_months_are_not():
    assert l7.has_month('2023 年 9 月 20 日首次发布', '2023-09')
    assert l7.has_month('2023年09月20日', '2023-09')
    assert not l7.has_month('2023年10月20日', '2023-09')
    assert not l7.has_month('2023/11/20', '2023-01')


def test_date_replay_selects_exact_reviewed_identity_before_checking(tmp_path, monkeypatch):
    import json
    from goodsdex.release_dates import apply_release_dates
    row, entry = fixture(tmp_path, monkeypatch)
    old_row = deepcopy(row)
    old_row['name'] = old_row['name'].replace(' ', '')
    old_entry = deepcopy(entry)
    old_entry.update(name=old_row['name'], identity_sha256=l7.fingerprint(old_row),
                     identity_terms=[old_row['name']])
    bundle = tmp_path / 'identities.json'
    bundle.write_text(json.dumps(dict(policy=l7.POLICY, entries=[old_entry, entry])))
    monkeypatch.setattr(l7, 'INPUT', bundle)
    row['release'] = deepcopy(entry['release'])
    assert apply_release_dates([row])[0]['release'] == row['release']
    row['params']['型号'] = 'H501 Pro'
    with pytest.raises(ValueError, match='no longer matches'):
        apply_release_dates([row])
