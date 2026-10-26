"""覆盖审计的分页、失败语义及跨分类 ID 去重。"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from audit_category_coverage import LimitedClient, enumerate_query
from report_category_coverage import analyze, index_public, present


def group(pid, name='商品', commodity=123):
    return {'product_id':str(pid),'commodity_list':[{'name':name,'commodity_id':commodity}]}


class FakeClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.urls = []

    def get(self, url):
        self.urls.append(url)
        return 'cb('+json.dumps({'code':200,'data':next(self.responses)})+');'


def test_enumerates_past_total_to_empty_and_reuses_pages(tmp_path):
    client=FakeClient([{'total':1,'pc_list':[group(1)]},
                       {'total':2,'pc_list':[group(2)]},
                       {'total':2,'pc_list':[]}])
    result=enumerate_query('耳机',client,tmp_path/'pages')
    assert result['found']==2 and result['pages']==3 and result['status']=='complete'
    assert len(client.urls)==3
    assert all('page_size=20&' in u for u in client.urls)
    cached=enumerate_query('耳机',FakeClient([]),tmp_path/'pages')
    assert cached==result


def test_empty_with_total_gap_is_partial(tmp_path):
    result=enumerate_query('x',FakeClient([{'total':2,'pc_list':[group(1)]},
                                         {'total':2,'pc_list':[]}]),tmp_path/'pages')
    assert result['status']=='partial' and result['found']==1


def test_schema_error_is_not_empty(tmp_path):
    with pytest.raises(RuntimeError,match='schema_error'):
        enumerate_query('x',FakeClient([{'total':0}]),tmp_path/'pages')


def test_repeated_pages_do_not_loop_forever(tmp_path):
    with pytest.raises(RuntimeError,match='pagination_stalled'):
        enumerate_query('x',FakeClient([{'total':2,'pc_list':[group(1)]}]*2),tmp_path/'pages')


def test_pid_normalization_gid_namespace_and_cross_category_dedup():
    public=[{'id':'CN:mi_cn:product:1','gid':99}]
    ids,gids=index_public(public)
    assert present(group(1),ids,gids)
    assert not present(group(2,commodity=99),ids,gids)
    assert present(dict(group(2),gid=99),ids,gids)
    enums={name:{'query':name,'scope':'tree','status':'complete','items':[group(1),group(2)]}
           for name in ['甲','乙']}
    stats,missing=analyze(enums,public,[])
    assert len(missing)==1 and missing['2']['tree_categories']==['甲','乙']
    assert all(s['have']==1 and s['missing']==1 for s in stats)


def test_budget_applies_to_retries_and_logs_rate_limit(tmp_path):
    client=LimitedClient(tmp_path,limit=2)
    error=HTTPError('https://example.com',429,'limited',None,None)
    with patch('audit_category_coverage.mi_cn._get',side_effect=error), \
         patch('audit_category_coverage.time.sleep'):
        with pytest.raises(RuntimeError,match='request_budget_exhausted'):
            client.get('https://example.com')
    logs=[json.loads(s) for s in (tmp_path/'requests.jsonl').read_text().splitlines()]
    assert client.count==2 and len(logs)==2
    assert all(r['status']=='rate_limited' for r in logs)
