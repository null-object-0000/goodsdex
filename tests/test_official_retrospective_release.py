"""Real-source census acceptance: locked rows, exact packages and original text."""
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

import pytest

from goodsdex.release_dates import apply_release_dates, validate
from goodsdex.release_scope import displayable, scope_coverage
from goodsdex.series_release import apply_series_releases

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'docs/release-dates-round10-20261104'


def read(name):
    return json.loads((AUDIT / name).read_text())


@pytest.fixture(scope='module')
def corpus():
    baseline = json.loads(gzip.decompress((AUDIT / 'baseline.json.gz').read_bytes()))
    result = apply_series_releases(apply_release_dates(baseline))
    return baseline, result


def test_retrospective_preserves_locked_apple_and_all_non_date_fields(corpus):
    before, after = corpus
    assert len(before) == len(after)
    locked = 0
    for a, b in zip(before, after):
        assert {k: v for k, v in a.items() if k not in ('release', 'release_series')} == {
            k: v for k, v in b.items() if k not in ('release', 'release_series')}
        if a.get('brand') == 'Apple' and displayable(a.get('release')):
            locked += 1
            assert a['release'] == b['release']
    assert locked == 417
    coverage = scope_coverage(after)['brands']
    assert coverage['Apple']['covered'] == 535
    assert coverage['富士']['covered'] == 13
    assert coverage['大疆']['covered'] == 96


def test_retrospective_full_replay_is_idempotent(corpus):
    assert apply_series_releases(apply_release_dates(corpus[1])) == corpus[1]


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def normalized(value):
    return ' '.join(value.split())


def test_every_new_product_quote_is_in_hashed_official_response():
    candidates = read('new-candidates.json') + read('apple-new-candidates.json')
    assert len(candidates) == 159
    for candidate in candidates:
        validate(candidate)
        release = candidate['release']
        evidence = release['evidence']
        raw = gzip.decompress((ROOT / evidence['capture_file']).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == evidence['sha256']
        parser = Text()
        parser.feed(raw.decode('shift_jis' if 'mall-jp.' in evidence['url'] else 'utf-8', errors='replace'))
        text = normalized(' '.join(parser.parts))
        assert normalized(evidence['quote']) in text, candidate['name']
        for quote in evidence.get('supporting_quotes', []):
            assert normalized(quote) in text
        if evidence.get('identity_quote'):
            assert normalized(evidence['identity_quote']) in text
        assert evidence['source_type'] == release['source'] == 'official'
        assert release['event'] in ('announcement', 'availability')
        assert re.search(r'発売日|推出|available|availability|ships|shipping|arriv|on sale|deliver',
                         evidence['quote'], re.I)


def test_reported_launch_is_not_availability_or_china_sale(corpus):
    rows = {r['id']: r for r in corpus[1]}
    for suffix, month in [('x-s20', '2023-06'), ('x100vi', '2024-02')]:
        release = rows['CN:fuji:model:' + suffix]['release']
        assert release['date'] == month
        assert release['event'] == 'announcement'
        assert release['market'] == 'GLOBAL_REPORTED_BY_CN_OFFICIAL'
        assert release['label'] == '全球推出月份（官方回溯）'
        assert displayable(release)
    assert rows['GLOBAL:apple_support:model:111940']['release']['date'] == '2014-10'
    assert rows['GLOBAL:apple_support:model:111940']['release']['event'] == 'availability'


def test_exact_kit_page_required_and_market_is_visible(corpus):
    before, after = corpus
    original = {r['id']: r for r in before}
    allowed = {'CN:fuji:kit:x-e5-xf23mmf28-r-wr', 'CN:fuji:kit:x-h2-16-80mm',
               'CN:fuji:kit:x-t50-xc15-45mm'}
    for row in after:
        key = row['id']
        if key.startswith('CN:fuji:kit:') and key not in allowed:
            assert row.get('release') == original[key].get('release')
        if row.get('brand') == '大疆':
            assert row.get('release') == original[key].get('release')
        release = row.get('release') or {}
        if release.get('retrospective') and release.get('market') == 'JP':
            assert release['label'] == '日本发售时间'
        if release.get('retrospective') and release.get('market') == 'US':
            assert release['label'] == '美国发售时间'


def test_xiaomi_history_remains_series_and_preserves_product_dates(corpus):
    original = {r['id']: r for r in corpus[0]}
    after = {r['id']: r for r in corpus[1]}
    for key in ('CN:mi_cn:product:3488', 'CN:mi_cn:product:6334'):
        assert after[key]['release'] == original[key]['release']
        assert after[key]['release_series']['level'] == 'series'
        assert after[key]['release_series']['source'] == 'official'
        assert after[key]['release_series']['event'] == 'announcement'
    # Undated Air models lack an exact generation identity: no inaugural-date inheritance.
    key = 'CN:mi_cn:product:10000032'
    assert after[key].get('release_series') == original[key].get('release_series')
