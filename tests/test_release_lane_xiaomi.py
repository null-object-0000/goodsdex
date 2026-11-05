"""Release extraction must fail closed when generation or date is unsupported."""
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('release_lane_xiaomi', Path(__file__).resolve().parents[1]/'scripts/release_lane_xiaomi.py')
lane = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lane)


def test_priority_scope_includes_old_computers_but_not_stickers():
    def row(name, category='旧款机型'):
        return dict(id='CN:mi_cn:product:1', name=name, category=category)
    assert lane.in_scope(row('15.6"游戏本 8代i7 16G 1060'))
    assert lane.in_scope(row('米家宠物空气净化器','空气净化器'))
    assert not lane.in_scope(row('米家智能宠物饮水机滤芯套装','宠物饮水机'))
    assert not lane.in_scope(row('小米笔记本定制贴纸','笔记本'))


def test_official_2021_release_cannot_date_2025_generation(tmp_path, monkeypatch):
    payload = tmp_path/'article.json'
    payload.write_text(json.dumps(dict(data=dict(content='RedmiBook Pro 11th Gen Intel Core H35. Official sales start from March 4th, 2021 via all Xiaomi official channels in Mainland China.'))))
    def fake_fetch(url, directory, refresh):
        return dict(url=url,status=200,reason='retrieved_requires_exact_model_event_review',
                    capture_file=str(payload),sha256='a'*64,captured_at='2026-11-05T00:00:00Z')
    monkeypatch.setattr(lane,'fetch',fake_fetch)
    rows=[dict(id='CN:mi_cn:product:20992',name='REDMI Book Pro 14 2025',category='笔记本',
               source_url='https://www.mi.com/shop/buy/detail?product_id=20992')]
    result=lane.run(rows,tmp_path/'out',live=False)
    assert result['candidates']==[]
    assert result['discoveries'][0]['date']=='2021-03-04'
    assert result['records'][0]['official_absence_confirmed'] is False
    assert result['observations'][0]['reason']=='no_verified_month_level_statement_for_exact_model'


def test_model_year_and_page_metadata_cannot_supply_month(tmp_path, monkeypatch):
    payload=tmp_path/'article.json'
    payload.write_text(json.dumps(dict(data=dict(add_time='1618827484',content='RedmiBook Pro announced in 2021.'))))
    monkeypatch.setattr(lane,'fetch',lambda url,directory,refresh:dict(url=url,status=200,
        reason='retrieved_requires_exact_model_event_review',capture_file=str(payload),sha256='b'*64,captured_at='2026-11-05T00:00:00Z'))
    rows=[dict(id='CN:mi_cn:product:1',name='REDMI Book Pro 2021',category='笔记本')]
    result=lane.run(rows,tmp_path/'out',live=False)
    assert not result['candidates']
    assert not result['discoveries']
    assert result['summary']==dict(total=1,hits=0,missing=1)
