import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('release_lane_series',Path(__file__).parents[1]/'scripts/release_lane_series.py')
lane=importlib.util.module_from_spec(spec);spec.loader.exec_module(lane)

def test_exact_official_platform_and_month_ceiling(tmp_path, monkeypatch):
    evidence=tmp_path/'evidence.json';evidence.write_text(json.dumps({'evidence':{'url':lane.URL,'quote':'March 29, 2023; ProBook 450 G10','sha256':'a'*64,'captured_at':'2026-11-05'},'scope':'Global platform announcement'}))
    monkeypatch.setattr(lane,'DEFAULT_EVIDENCE',evidence)
    rows=[{'id':'CN:hp_cn:sku:a','source':'hp_cn','category':'笔记本','params':{'source_specs':{'productSeriesName':'HP ProBook 450 15.6 英寸 G10 笔记本电脑'}}},
          {'id':'CN:hp_cn:sku:b','source':'hp_cn','category':'笔记本','params':{'source_specs':{'productSeriesName':'HP ProBook 450 15.6 英寸 G11 笔记本电脑'}}},
          {'id':'CN:hp_cn:sku:c','source':'hp_cn','category':'笔记本','name':'战66六代','params':{}},
          {'id':'old-unverified','category':'笔记本','release_series':{'date':'2024-04-02','granularity':'day','source':'third_party','evidence':{'url':'https://example.com','quote':'test'}}}]
    before=evidence.read_bytes()
    r=lane.run(rows,tmp_path/'output',live=False)
    assert evidence.read_bytes()==before
    assert r['evidence']['url']==lane.URL
    assert r['scope']=='Global platform announcement'
    assert r['candidates']==[]
    assert len(r['inherited_candidates'])==1
    release=r['inherited_candidates'][0]['release']
    assert release['date']=='2023-03' and release['granularity']=='month'
    assert release['source']=='series_inherit' and release['market']=='GLOBAL'
    assert 'release' not in rows[0]
