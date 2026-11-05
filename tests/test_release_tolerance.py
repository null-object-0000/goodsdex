from copy import deepcopy
from goodsdex.release_tolerance import apply,normalize
from goodsdex.release_coverage import effective


def assertion(delta=None,**changes):
    r=dict(date='2025-05-22',granularity='day',source='third_party',event='announcement',market='CN',
           release_delta_days=delta,evidence=dict(url='https://example.com/product',quote='2025年5月22日发布 X2',
           sha256='a'*64,captured_at='2026-11-05',source_type='third_party'))
    r.update(changes);return r


def test_boundaries_and_no_day_public_copy():
    for delta in (0,14,15,45,46,100):
        row=apply([dict(id='x',release=assertion(delta))])[0]
        r=effective(row)
        assert bool(r)==(delta<=45)
        if r:
            assert '22' not in r['display'] and row['release_decision']['date']=='2025-05'
            assert r['release_tolerance_days']==14
            assert r['decision_usage']==(['age'] if delta>14 else ['age','generation'])
            if delta>14: assert r['confidence']=='medium' and '约' in r['display']
        else:
            assert row['release']['date'] is None and row['release_conflicts'][0]['release_delta_days']==delta


def test_independent_source_required_for_crossed_llm():
    r=assertion(0,source='llm_crossed')
    assert normalize(r) is None
    r['llm_crosscheck']=dict(independent=True,model='model',date='2025-05-20',identity_verified=True,event_verified=True)
    assert normalize(r)['release_delta_days']==2
    r['llm_crosscheck']['date']='2025-04-01'
    assert normalize(r) is None
    assert normalize(assertion(source='llm')) is None


def test_evidence_and_all_sources_conflict():
    for key in ('url','quote','sha256','captured_at'):
        r=assertion();r['evidence'].pop(key);assert normalize(r) is None
    r=assertion();r['assertions']=[assertion(date='2025-01-01')]
    row=apply([dict(id='x',release=r,release_series=assertion(source='official',level='series'))])[0]
    assert effective(row) is None and row['release_conflicts']


def test_source_ranking_alternates_and_replay():
    rows=[dict(id='x',release=assertion(10),release_inherited=assertion(0,source='official',level='series'))]
    out=apply(rows)
    assert effective(out[0])['release_source']=='series_inherit'
    assert effective(out[0])['granularity']=='month'
    assert len(effective(out[0])['alternates'])==1
    assert apply(out)==out
    assert rows[0]['release']['date']=='2025-05-22'


def test_conflicting_inheritance_cannot_fall_back_to_another_product_date():
    rows=[dict(id='x',release=assertion(0,source='official'),
               release_inherited=assertion(46,source='series_inherit',level='series'))]
    row=apply(rows)[0]
    assert effective(row) is None and row['release']['date'] is None
    assert apply([row])==[row]
