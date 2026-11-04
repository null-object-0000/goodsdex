from copy import deepcopy
import pytest
from goodsdex.source_urls import apply_source_urls, coverage, mi_url


def evidence(passed=16):
    samples=[]
    for i in range(20):
        key=f'CN:mi_cn:product:{i}'
        samples.append(dict(id=key,url=mi_url(key),final_url=mi_url(key),status=200,score=1 if i<passed else 0,passed=i<passed))
    return dict(schema=1,samples=samples,approved=[])


def row(i, **fields):
    return dict(id=f'CN:mi_cn:product:{i}',name='测试型号',brand='小米',**fields)


def approve(m, i):
    m['approved'].append(dict(id=row(i)['id'],name=row(i)['name'],url=mi_url(row(i)['id'])))


def test_below_gate_only_individually_verified():
    m=evidence(15);approve(m,0)
    assert apply_source_urls([row(0)],m)[0]['source_url']==mi_url(row(0)['id'])
    approve(m,21)
    with pytest.raises(ValueError,match='below sample gate'): apply_source_urls([row(21)],m)


def test_gate_does_not_override_failed_or_existing_and_freezes_identity():
    m=evidence();approve(m,21)
    original=[row(21),row(21,source_url='https://www.mi.com/old/'),dict(row(21),name='另一个商品'),row(22)]
    before=deepcopy(original);result=apply_source_urls(original,m)
    assert original==before
    assert result[0]==dict(original[0],source_url=mi_url(original[0]['id']))
    assert result[1:]==original[1:]
    approve(m,19)
    with pytest.raises(ValueError,match='failed sample'):apply_source_urls(original,m)


@pytest.mark.parametrize('change', ['status','score','final_url','url'])
def test_fake_success_cannot_open_gate(change):
    m=evidence(16);m['samples'][0][change]={'status':403,'score':.1,'final_url':'https://www.mi.com/','url':'https://third.party/item'}[change];approve(m,21)
    with pytest.raises(ValueError):apply_source_urls([row(21)],m)


def test_statistics_counts_rows_and_keeps_brands_separate():
    value=coverage([row(1),row(1,source_url='https://www.mi.com/1'),dict(id='CN:apple_cn:commodity:a',brand='Apple',source_url='https://www.apple.com/cn/')])
    assert value['with_source_url']==2
    assert value['by_brand']['小米']==dict(total=2,with_source_url=1,missing=1,ratio=.5)
    assert value['by_brand']['Apple']['ratio']==1
