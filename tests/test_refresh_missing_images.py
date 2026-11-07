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
    Image.new('RGB', (400, 400)).save(raw, format='PNG')

    def fetch(url, **kwargs):
        if case == 'empty':
            pytest.fail('Existing image must not be fetched')
        if case == 'network' or kwargs.get('json', [{}, {}])[1].get('productId') == 2:
            raise requests.Timeout('upstream timed out')
        if case in ('absent', 'mixed_failure'):
            return response(404)
        if 'json' not in kwargs:
            return response(content=raw.getvalue())
        return response(payload=dict(data=dict(
            product=dict(name='Other model' if case == 'mismatch' else 'Exact model'),
            goodsInfo=dict(goodsList=[] if case == 'no_image' else
                           [dict(imgUrl='https://official.example/main.png')]))))

    monkeypatch.setattr(requests, 'get', fetch)
    monkeypatch.setattr(requests, 'post', fetch)
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(ROOT / 'scripts/refresh_missing_images.py'), run_name='__main__')
    assert exit_info.value.code == expected
    audit = json.loads((tmp_path / '_data/public/image-refresh-report.json').read_text())
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


def test_removed_blocked_source():
    assert 'api2.order.mi.com' not in (ROOT / 'scripts/refresh_missing_images.py').read_text()


def png(size):
    raw = io.BytesIO()
    Image.new('RGB', size).save(raw, format='PNG')
    return raw.getvalue()


def test_realicon_preferred_and_image_only():
    from refresh_missing_images import refresh
    row = dict(id='CN:mi_cn:product:1', name='Exact model', miio_model='vendor.device.v1',
               price=123, params={'a': 'b'}, release='2024-01', display={'price': {'value': 123}})
    def baike(model):
        assert model == row['miio_model']
        return dict(model=model, image='https://official.example/real.png', width=480, height=480,
                    source_url='https://home.mi.com/cgi-op/api/v1/baike/v2/product?model=' + model,
                    captured_at='2026-11-07T00:00:00Z', image_sha256='abc')
    def forbidden(*a, **kw):
        pytest.fail('realIcon must win without requesting mtop or icons')
    after, audit = refresh([row], forbidden, post=forbidden, baike=baike)
    assert audit[0]['source'] == 'mijia_baike_realIcon'
    assert after[0]['image_width'] == 480
    assert {k: v for k, v in after[0].items() if k not in ('sources', 'display', 'image')
            and not k.startswith('image_')} == {k: v for k, v in row.items() if k != 'display'}
    assert after[0]['display']['price'] == row['display']['price']


@pytest.mark.parametrize('baike_failure', ['no_realIcon', 'undersized', 'http_error'])
def test_baike_fallback_to_mtop(baike_failure):
    from refresh_missing_images import refresh
    from goodsdex.sources.mi_cn import MTOP_HEADERS, MTOP_URL
    def post(url, **kw):
        assert url == MTOP_URL and kw['headers'] == MTOP_HEADERS
        assert kw['json'] == [{}, {'productId': 1}]
        return response(payload={'code': 0, 'data': {'product': {'name': 'Exact model'},
            'goodsInfo': {'goodsList': [{'picUrl': 'https://official.example/main.png'}]}}})
    after, audit = refresh([dict(id='CN:mi_cn:product:1', name='Exact model', miio_model='a.b.c')],
        lambda *a, **kw: response(content=png((800, 800))), post=post,
        baike=lambda model: dict(failure=baike_failure, product_request={'http_status': 503}))
    assert audit[0]['status'] == 'added'
    assert audit[0]['source'] == 'mi_cn_mtop_cover'
    assert after[0]['image_width'] == 800


@pytest.mark.parametrize('size,status', [((399, 480), 'no_official_image'),
                                         ((480, 399), 'no_official_image'),
                                         ((400, 400), 'added')])
def test_pics_dimensions_and_no_device_icon(size, status):
    from refresh_missing_images import refresh
    def post(*a, **kw):
        return response(payload={'data': {'product': {'name': 'Exact model',
            'icon': 'https://official.example/device.png',
            'pics': [{'url': 'https://official.example/main.png'}]}}})
    def fetch(url, **kw):
        assert url.endswith('/main.png')
        return response(content=png(size))
    row = dict(id='CN:mi_cn:product:1', name='Exact model')
    after, audit = refresh([row], fetch, post=post)
    assert audit[0]['status'] == status
    if status != 'added':
        assert after == [row]


def test_limit_and_scope():
    from refresh_missing_images import refresh
    rows = [dict(id=f'CN:mi_cn:product:{i}', name='X') for i in range(110)]
    rows[:0] = [dict(id='mihome:1'), dict(id='CN:mi_cn:product:999', image='existing')]
    calls = []
    def post(url, **kw):
        calls.append(url)
        return response(404)
    after, audit = refresh(rows, limit=500, post=post)
    assert len(calls) == len(audit) == 100
    assert after == rows


def test_baike_network_failure_not_hidden_by_mtop_absence():
    from refresh_missing_images import refresh
    row = dict(id='CN:mi_cn:product:1', name='X', miio_model='a.b.c')
    after, audit = refresh([row], post=lambda *a, **kw: response(404),
        baike=lambda model: dict(failure='http_error', product_request={'http_status': 429}))
    assert after == [row]
    assert audit[0]['status'] == 'network_error'


def test_white_background_preferred_over_other_main_shots():
    from refresh_missing_images import refresh
    def post(*a, **kw):
        return response(payload={'data': {'product': {'name': 'X',
            'pics': ['https://official.example/white.png']},
            'goodsInfo': {'goodsList': [{'picUrl': 'https://official.example/dark.png'}]}}})
    def fetch(url, **kw):
        raw = io.BytesIO()
        Image.new('RGB', (480, 480), 'white' if 'white.png' in url else 'black').save(raw, format='PNG')
        return response(content=raw.getvalue())
    after, audit = refresh([dict(id='CN:mi_cn:product:1', name='X')], fetch, post=post)
    assert after[0]['image'] == audit[0]['url'] == 'https://official.example/white.png'


def test_baike_timeout_can_fall_back():
    from refresh_missing_images import refresh
    def baike(model):
        raise requests.Timeout('timeout')
    _, audit = refresh([dict(id='CN:mi_cn:product:1', name='X', miio_model='a.b.c')],
                       post=lambda *a, **kw: response(404), baike=baike)
    assert audit[0]['status'] == 'network_error'
