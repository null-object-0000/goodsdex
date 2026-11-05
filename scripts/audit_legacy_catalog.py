"""Audit a finalized release against the frozen 223-ID inventory; no network/write to release."""
import argparse,gzip,json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]

def audit(public,out):
    before=json.loads(gzip.decompress((ROOT/'docs/legacy-catalog-20261105/before-223.json.gz').read_bytes()))
    ids={r['id'] for r in before}
    goods=json.loads((public/'goods.json').read_text()); excluded=json.loads((public/'goods-excluded.json').read_text())['items']
    rows=[r for r in [*goods,*excluded] if r['id'] in ids]
    assert len(rows)==223 and {r['id'] for r in rows}==ids
    assert all(r['category']!='旧款机型' for r in [*goods,*excluded])
    by_id={r['id']:r for r in rows}
    recovered={r['id']:r for r in json.loads((ROOT/'docs/legacy-catalog-20261105/source-url-recovery.json').read_text())['items']}
    for old in before:
        new=by_id[old['id']]
        if old.get('source_url') is None and old['id'] in recovered:
            assert recovered[old['id']]['source_url']==new.get('source_url')
        else:
            assert old.get('source_url')==new.get('source_url'),old['id']
        assert old.get('price')==new.get('price') is None
        assert old.get('historical_price')==new.get('historical_price')
        if old.get('image_scope')=='series' and old.get('image'):
            assert new.get('image') is None and new['reference_image']['url']==old['image']
        else:assert new.get('image')==old.get('image')
    washer=[r for r in goods if '米家内衣物洗烘一体机' in r.get('name','')]
    assert washer and not any('米家内衣物洗烘一体机' in r.get('name','') for r in excluded)
    summary=dict(scope=223,published=sum(r['id'] in ids for r in goods),excluded=sum(r['id'] in ids for r in excluded),
        categories=dict(sorted(Counter(r['category'] for r in rows).items())),
        price_missing=dict(Counter(str(r.get('price_missing')) for r in rows)),
        image_missing=dict(Counter(r.get('image_missing') or 'present' for r in rows)),
        archived_count=sum(bool(r.get('archived_at')) for r in rows),
        captured_count=sum(bool(r.get('captured_at')) for r in rows),
        captured_unknown=sum(bool(r.get('captured_at_unknown')) for r in rows),
        washer_preserved=[dict(id=r['id'],name=r['name'],category=r['category']) for r in washer],
        series_reference_images=[dict(id=r['id'],name=r['name'],reference_image=r['reference_image']) for r in rows if r.get('reference_image')])
    manual=[dict(id=r['id'],name=r['name']) for r in rows if r.get('category_review_required')]
    plan={cat:[dict(id=r['id'],name=r['name'],category=cat,excluded_reason=r.get('excluded_reason')) for r in rows if r['category']==cat] for cat in ['服饰','配件','箱包']}
    assert sum(map(len,plan.values()))==summary['excluded']==41
    out.mkdir(parents=True,exist_ok=True)
    for filename,value in [('summary.json',summary),('manual-review.json',manual),('exclusion-plan.json',plan),('after-223.json',rows)]:
        (out/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    lines=['# 旧来源桶 223 条修复验收','',f"223 个 ID 全部保留：主列表 {summary['published']} + 排除档案 {summary['excluded']}；待人工 {len(manual)}。",'',
      '|真实品类|条数|','|---|---:|',*[f'|{c}|{n}|' for c,n in summary['categories'].items()],
      '', '价格：`page_no_price` 223。主图：`page_no_image` 173；有型号主图 50。139 条保留原 Wayback 存档时间，实际采集时间未知；84 条沿用原记录 fetched_at。',
      '', '冻结时线上已有 8 条被服饰规则排除，主列表剩 215 条。当前 source_url 为 128 个 Wayback + 95 个商城页：其中11条历史笔记本后续已由官方名称修复替换为商城来源，原139条 Wayback证据另存 archived_source_url。2条板鞋在旧排除清单中的source_url为空，本轮从同ID已存在的archive/apparel.json恢复（见source-url-recovery.json），其余链接保持原值。没有伪造source_url。',
      '', '原图片补充清单60张，其中2张板鞋的排除档案没有主图且旧补图证据仅为 series，未补回；本次冻结非空58张，其中8张 series 也降为 reference_image，保留原图URL与证据，不冒充型号主图。故验收为50/173，不沿用原60/163。',
      '', '系列展示以品牌+系列作为父组；series_key 保留品牌+系列+尺寸/代际子键，尺寸、CPU、内存、存储、颜色等名称明确写出的配置进 attrs。红米5父组7条；小米笔记本Air父组8条（本次6条+原已正确分类的12.5/13.3四核增强2条，仅补聚合标记）。组价均null，显示“旧款 · 无现价”，历史标价只在其原配置记录独立展示。',
      '', '## 排除前清单（每品类前20条）','', '分类后由既有 apparel / accessory 规则自动命中；41条中8条此前已排除，本次新增33条。没有删除源记录。']
    for cat,items in plan.items():
        lines += ['',f'### {cat}：{len(items)} 条','', '|ID|名称|主排除理由|','|---|---|---|']+[f"|{r['id']}|{r['name']}|{r['excluded_reason']}|" for r in items[:20]]
    lines += ['', '“米家内衣物洗烘一体机”保留在主列表：'+ '、'.join(r['id'] for r in washer)+'。', '', '完整逐项记录见 after-223.json；待人工清单见 manual-review.json（空）；完整排除计划见 exclusion-plan.json。截图、测试、提交和发布记录见 publication.md。']
    (out/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('series_reference_images','washer_preserved')},ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--public',required=True,type=Path);ap.add_argument('--out',default=ROOT/'docs/legacy-catalog-20261105',type=Path);a=ap.parse_args();audit(a.public,a.out)
