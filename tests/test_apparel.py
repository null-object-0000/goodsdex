import json
import pytest

from goodsdex.apparel import classify_apparel, NAME_WORDS, CATEGORY_WORDS, CATEGORY_LEAVES
from goodsdex.dedupe import finalize_public
from goodsdex.shards import build_shards


@pytest.mark.parametrize('category', CATEGORY_WORDS + CATEGORY_LEAVES)
def test_apparel_category_has_priority(category):
    decision = classify_apparel(dict(name='普通商品', category=category))
    assert decision['matched_rule'] == 'category'
    assert decision['matched_text'] == category


@pytest.mark.parametrize('word', NAME_WORDS)
def test_apparel_name_fallback(word):
    decision = classify_apparel(dict(name='品牌' + word, category='旧款机型'))
    assert decision['matched_rule'] == 'name'
    assert decision['matched_text'] in '品牌' + word


@pytest.mark.parametrize('row', [
    dict(name='米家内衣物洗烘一体机', category='波轮洗衣机'),
    dict(name='米家洗衣机 波轮6kg', category='服饰', categories=['服饰', '家电']),
    dict(name='米家运动鞋除臭喷雾', category='清洁剂'),
    dict(name='手机含睡衣套装', category='手机'),
    dict(name='床品套装（含睡衣）', category='床品'),
    dict(name='含睡衣的礼盒套装', category='组合装'),
    dict(name='床品礼盒（含深睡睡衣）', category='组合装'),
    dict(name='帽式台灯', category='灯具'),
    dict(name='Osmo 自拍杆快拆背包夹', category='摄影器材配件'),
    dict(name='套装含睡衣', category='服饰'),
    dict(name='米家运动杯', category='运动鞋', categories=['运动鞋', '水杯']),
    dict(name='内衣护理设备', category_l1='家电'),
    dict(name='鞋图案相机', category_l1='数码'),
])
def test_counterexamples(row):
    assert classify_apparel(row) is None


def test_spray_is_decided_by_category():
    assert classify_apparel(dict(name='运动鞋除臭喷雾', category='护理剂')) is None
    assert classify_apparel(dict(name='服装', category='服饰'))['matched_rule'] == 'category'


def test_apparel_archive_replay_and_future_ids(tmp_path):
    rows = [dict(id='new-shirt', name='新款T恤', category='服装', price=99),
            dict(id='washer', name='米家内衣物洗烘一体机', category='滚筒洗衣机')]
    (tmp_path / 'goods.json').write_text(json.dumps(rows))
    for _ in range(2):
        finalize_public(tmp_path, previous=rows)
        meta = build_shards(tmp_path)
        excluded = json.loads((tmp_path / 'goods-excluded.json').read_text())
        assert meta['total_all'] == 2
        assert meta['total_published'] == meta['total_excluded'] == 1
        assert meta['excluded_by_rule']['apparel'] == 1
        hit = excluded['items'][0]
        assert hit['excluded_reason'] == 'apparel'
        assert hit['matched_rule'] == hit['exclusion']['matched_rule'] == 'category'
        assert hit['matched_text'] == hit['exclusion']['matched_text'] == '服装'
        assert all(hit[k] == v for k, v in rows[0].items())
        archived = json.loads((tmp_path / 'archive/apparel.json').read_text())
        assert len(archived) == 1
        assert all(archived[0][k] == v for k, v in rows[0].items())
        assert json.loads((tmp_path / 'goods.json').read_text())[0]['id'] == 'washer'
    fresh = dict(id='future-shirt', name='定制衬衫', category='其它')
    (tmp_path / 'goods.json').write_text(json.dumps([rows[1], fresh]))
    finalize_public(tmp_path)
    meta = build_shards(tmp_path)
    assert (meta['total_all'], meta['total_published'], meta['excluded_by_rule']['apparel']) == (3, 1, 2)
