import io
import json
from pathlib import Path
import runpy
import sys
from urllib.error import HTTPError, URLError

import pytest
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from refresh_missing_images import failure_status


def response(status=200, payload=None, content=b''):
    result = requests.Response()
    result.status_code = status
    result.url = 'https://official.example/product'
    result._content = content if payload is None else json.dumps(payload).encode()
    return result


@pytest.mark.parametrize('error,expected', [
    (requests.Timeout('timeout'), 'network_error'),
    (requests.ConnectionError('connection refused'), 'network_error'),
    (URLError('unreachable'), 'network_error'),
    (TimeoutError('timed out'), 'network_error'),
    *[(requests.HTTPError(response=response(code)),
       'no_official_image' if code == 404 else 'network_error')
      for code in (404, 403, 406, 429, 500, 503)],
    (HTTPError('https://official.example', 404, 'Not Found', {}, None), 'no_official_image'),
    (ValueError('产品名不完全一致，保留审核'), 'no_official_image'),
    (ValueError('多商品图身份不明确，保留审核'), 'no_official_image'),
])
def test_failure_classification(error, expected):
    assert failure_status(error) == expected


@pytest.mark.parametrize('case,expected,counts', [
    ('network', 1, (0, 0, 1)),
    ('absent', 0, (0, 1, 0)),
    ('empty', 0, (0, 0, 0)),
    ('mismatch', 0, (0, 1, 0)),
    ('no_image', 0, (0, 1, 0)),
    ('mixed_failure', 1, (0, 1, 1)),
    ('partial_success', 0, (1, 0, 1)),
])
def test_script_exit_and_report(case, expected, counts, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / '_data/public/goods.json'
    path.parent.mkdir(parents=True)
    rows = [dict(id='CN:mi_cn:product:1', name='Exact model')]
    if case == 'empty':
        rows = [dict(rows[0], image='https://official.example/existing.png')]
    if case in ('mixed_failure', 'partial_success'):
        rows.append(dict(id='CN:mi_cn:product:2', name='Exact model'))
    if case == 'partial_success':
        from goodsdex.product_sources import materialize
        rows[0] = materialize(rows[0], observations=[dict(
            source='mi_store', source_url='https://www.mi.com/product/1',
            captured_at='2026-11-06T00:00:00Z', fields=dict(name='Exact model'),
            evidence=dict(method='page_fetch'))])
    path.write_text(json.dumps(rows))
    raw = io.BytesIO()
    Image.new('RGB', (300, 300)).save(raw, format='PNG')

    def fetch(url, **kwargs):
        if case == 'empty':
            pytest.fail('Existing image must not be fetched')
        if case == 'network' or kwargs.get('params', {}).get('product_id') == '2':
            raise requests.Timeout('upstream timed out')
        if case in ('absent', 'mixed_failure'):
            return response(404)
        if 'params' not in kwargs:
            return response(content=raw.getvalue())
        return response(payload=dict(data=dict(
            product=dict(name='Other model' if case == 'mismatch' else 'Exact model'),
            goodsInfo=dict(goodsList=[] if case == 'no_image' else
                           [dict(imgUrl='https://official.example/main.png')]))))

    monkeypatch.setattr(requests, 'get', fetch)
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(ROOT / 'scripts/refresh_missing_images.py'), run_name='__main__')
    assert exit_info.value.code == expected
    audit = json.loads((tmp_path / '_data/data/categories/image-refresh-report.json').read_text())
    assert tuple(sum(a['status'] == status for a in audit)
                 for status in ('added', 'no_official_image', 'network_error')) == counts
    added, absent, network = counts
    assert f'本轮 {sum(counts)} 个候选：补上 {added}、上游无图 {absent}、网络失败 {network}' in capsys.readouterr().out
    if not added:
        assert json.loads(path.read_text()) == rows
    else:
        assert json.loads(path.read_text())[0]['image'] == 'https://official.example/main.png'
    assert all('reason' in a for a in audit if a['status'] != 'added')


def test_programming_error_is_not_upstream_absence():
    with pytest.raises(TypeError, match='bug'):
        failure_status(TypeError('bug'))
