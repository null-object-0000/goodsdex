import gzip
import json
from collections import Counter
from pathlib import Path
from goodsdex.legacy_catalog import apply_legacy_catalog, category_of
from goodsdex.accessories import classify
from goodsdex.apparel import classify_apparel
from goodsdex.price_semantics import apply as prices, coverage

ROOT=Path(__file__).resolve().parents[1]

def frozen():
    return json.loads(gzip.decompress((ROOT/'docs/legacy-catalog-20261105/before-223.json.gz').read_bytes()))

def test_all_223_lossless_reclassification_and_time_separation():
    before=frozen(); after=apply_legacy_catalog(before)
    assert len(after)==223 and {r['id'] for r in after}=={r['id'] for r in before}
    assert all(r['category']!='旧款机型' and not r['category_review_required'] for r in after)
    assert sum(bool(r.get('archived_at')) for r in after)==139
    assert sum(r['captured_at_unknown'] for r in after)==139
    assert sum(bool(r['captured_at']) for r in after)==84
    for old,new in zip(before,after):
        for field in ('price','historical_price'):
            assert old.get(field)==new.get(field)
        if old.get('source_url'):
            assert new['source_url']==old['source_url']
        else:
            recovered=json.loads((ROOT/'docs/legacy-catalog-20261105/source-url-recovery.json').read_text())['items']
            assert any(r['id']==new['id'] and r['source_url']==new['source_url'] for r in recovered)
        if old.get('image') and old.get('image_scope')=='series':
            assert new['image'] is None and new['reference_image']['url']==old['image']
        else:
            assert old.get('image')==new.get('image')
        assert new['price_missing']=='page_no_price'
        if new['image'] is None: assert new['image_missing']=='page_no_image'
        if new.get('archived_at'): assert new['archived_at']!=new['captured_at']
    assert apply_legacy_catalog(after)==after
    normalized=prices(after)
    assert all(r['price_missing']=='page_no_price' for r in normalized)
    assert coverage(normalized)['price_missing_count']==223

def test_exclusions_follow_real_categories_and_keep_appliance():
    rows=apply_legacy_catalog(frozen())
    for row in rows:
        if row['category']=='配件': assert classify(row)['accessory'], row['name']
        if row['category'] in ('服饰','箱包'): assert classify_apparel(row), row['name']
    row={'id':'washer','name':'米家内衣物洗烘一体机','category':'滚筒洗衣机'}
    assert not classify_apparel(row) and not classify(row)['accessory']

def test_explicit_series_preserves_every_variant_and_never_uses_historical_price():
    rows=apply_legacy_catalog(frozen())
    for series,count in [('红米5 系列',7),('小米笔记本 Air',6)]:
        members=[r for r in rows if r.get('series')==series]
        assert len(members)==count and len({r['family_group_key'] for r in members})==1
        assert all(r['price'] is None and r['attrs'] for r in members)
    air=[r for r in rows if r.get('series')=='小米笔记本 Air']
    assert {r['attrs']['size'] for r in air}=={'12.5英寸','13.3英寸'}
    assert len({r['series_key'] for r in air})>1
    assert category_of('未知型号 ABC') is None
    assert category_of('小米米家插线板')=='配件'

def test_archived_evidence_survives_next_release_provenance_guard():
    from goodsdex.backfill import validate_row, has_observation_time
    rows=apply_legacy_catalog(frozen())
    for row in rows:
        validate_row(row)
    assert not has_observation_time({'source_url':'https://www.mi.com/', 'archived_at':'2018-01-01', 'captured_at_unknown':True})
    assert not has_observation_time({'source_url':'https://web.archive.org/web/20180101000000/https://www.mi.com/', 'archived_at':'2018-01-01'})

def test_collector_replay_and_exclusion_archive_keep_known_original_urls():
    before=frozen()
    replay=[dict(row,source_url=None) for row in before if row.get('source_url')]
    restored=apply_legacy_catalog(replay)
    original={r['id']:r['source_url'] for r in before if r.get('source_url')}
    assert all(r['source_url']==original[r['id']] for r in restored)

def test_cold_source_cache_cannot_erase_verified_exact_model_images():
    rows=[dict(r,image=None) for r in frozen()]
    restored=apply_legacy_catalog(rows)
    original={r['id']:r for r in frozen()}
    assert sum(bool(r['image']) for r in restored)==50
    for row in restored:
        if row['image']:
            assert original[row['id']]['image_scope']=='model'
            assert row['image']==original[row['id']]['image']

def test_actual_finalizer_preserves_links_and_model_images_in_excluded_sidecar(tmp_path):
    from goodsdex.dedupe import finalize_public
    from goodsdex.accessories import fingerprint
    cold=[dict(r,source_url=None,image=None) for r in frozen()]
    reviewed=apply_legacy_catalog(cold)
    digest=fingerprint([r for r in reviewed if r['category']=='配件'])
    (tmp_path/'goods.json').write_text(json.dumps(cold))
    (tmp_path/'meta.json').write_text('{}')
    finalize_public(tmp_path,reviewed_accessory_sha256=digest)
    published=json.loads((tmp_path/'goods.json').read_text())
    excluded=json.loads((tmp_path/'goods-excluded.json').read_text())['items']
    all_rows=published+excluded
    assert len(published)==182 and len(excluded)==41 and len(all_rows)==223
    assert all(r.get('source_url') for r in all_rows)
    # Official images remain 50; 17 independent device icons are display fallbacks.
    assert sum(bool(r['image']) for r in all_rows)==50
    icons=[r['image_mihome'] for r in all_rows if r.get('image_mihome')]
    assert len(icons)==17
    assert all(r['width']==r['height']==168 and r['scope']=='device_icon' for r in icons)
    from goodsdex.mihome_catalog import apply_catalog
    expected={r['id']:r for r in apply_catalog(reviewed)}
    assert all(r['source_url']==expected[r['id']]['source_url'] and r['image']==expected[r['id']]['image'] for r in all_rows)
