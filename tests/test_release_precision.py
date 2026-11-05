from copy import deepcopy
import json
import pytest
from goodsdex.release_coverage import effective, matrix, apply_priority_dates, precision, missing_reason
from goodsdex.release_dates import validate


def release(**kw):
    return dict(date='2025-03-04',granularity='day',source='official',confidence='high',
        event='announcement',evidence=dict(url='https://www.hp.com/news',quote='March 4, 2025: ProBook',
            locator='body',sha256='a'*64,captured_at='2026-11-05',source_type='official'),**kw)


def test_real_day_accepted_invalid_days_and_year_rejected():
    r=release()
    assert validate(dict(family='x',ids=['x'],release=r))['date']=='2025-03-04'
    for d,g in [('2025','year'),('2025-02-29','day'),('2025-13','month'),('2025-01','day')]:
        with pytest.raises(ValueError):validate(dict(family='x',ids=['x'],release=dict(r,date=d,granularity=g)))


def test_page_and_llm_never_count_and_unknown_is_not_official_absence():
    rows=[dict(id='a',brand='惠普',category='笔记本',page_first_archived={'date':'2025-01-01'},release_llm={'date':'2025-01'}),
          dict(id='b',brand='惠普',category='笔记本',release=dict(release(),source='llm')),
          dict(id='c',brand='惠普',category='笔记本',release=release())]
    m=matrix(rows)['total']
    assert (m['day'],m['month'],m['none'],m['not_obtained'],m['official_absent'])==(1,0,2,2,0)
    assert missing_reason({'release_missing':{'reason':'official_absent'}})=='not_obtained'


def test_append_only_exact_ids_month_inheritance_idempotent(tmp_path):
    original=release()
    rows=[dict(id='a',category='笔记本',release=original),dict(id='b',category='笔记本'),dict(id='c',category='笔记本')]
    inherited=dict(release(),date='2025-03',granularity='month',source='series_inherit',release_source='series_inherit',level='series')
    path=tmp_path/'lane.json';path.write_text(json.dumps({'inherited_candidates':[{'ids':['a','b'],'release':inherited}]}))
    out=apply_priority_dates(rows,[path])
    assert out[0]==rows[0] and out[2]==rows[2]
    assert out[1]['release_inherited']['granularity']=='month'
    assert apply_priority_dates(out,[path])==out
    assert rows[1]==dict(id='b',category='笔记本')


def test_series_day_evidence_is_only_month_in_coverage():
    r=release(level='series')
    row={'id':'a','category':'笔记本','release_series':r}
    assert effective(row)['granularity']=='month'
    assert row['release_series']['date']=='2025-03-04'
    assert effective(dict(row,release_series=dict(r,usage='disabled'))) is None


def test_duplicate_id_projections_all_receive_append_only_date(tmp_path):
    rows=[dict(id='b',category='笔记本',name='one'),dict(id='b',category='笔记本',name='two')]
    path=tmp_path/'lane.json';path.write_text(json.dumps({'candidates':[{'family':'b','ids':['b'],'release':release()}]}))
    out=apply_priority_dates(rows,[path])
    assert all(r['release']['date']=='2025-03-04' for r in out)
    assert [r['name'] for r in out]==['one','two']
