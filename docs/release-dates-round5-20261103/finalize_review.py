"""Frozen sample verdicts; never substitutes corrections for failed proposals."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path[:0] = ['src', 'scripts', str(Path(__file__).resolve().parent)]
from goodsdex.release_dates import brand_llm_gate
from release_family_llm import write
from capture_review import SOURCES

ROOT = Path(__file__).resolve().parent

# Exact original proposals remain frozen. Independent checks do not repair their
# date or replace a non-evidentiary product URL to improve the score after sampling.
VERDICTS = {
 '大疆|摄影器材配件|djilidar焦点测距器': ('lidar', '2021-10',
    '2021-10-20; DJI Ronin 4D; a LiDAR focusing system',
    '独立公告支持系统于2021-10推出；候选借系统日期，原产品页为当前8K产品薄壳，无该独立配件首次推出日期，依据不合格。'),
 '大疆|运动相机|osmoaction5pro': ('action5', '2024-09',
    'News2024-09-19; today unveils the Osmo Action 5 Pro',
    '独立官方公告印证月份；原候选只有产品页及空引文，本次直抓为薄壳，网页索引的基准测试脚注不证明首次推出，原依据未支持公告日期。'),
 '大疆|运动相机|osmo360': ('osmo360', '2025-07',
    '2025-07-31; today launches the Osmo 360',
    '独立官方公告印证月份，但模型提供的 https://www.dji.com/osmo-360 实际404，空引文，依据不合格。'),
 '富士|相机镜头|xc35mmf2': ('xc35', '2020-01',
    'January 23, 2020; XC35mmF2',
    '公告发生在2020-01；候选给2020-02，把开售窗口混成首次公告，错误；原产品引用也未提供日期原句。'),
 '富士|相机镜头|xc50-230mmf4.5-6.7oisii': ('xc50230', '2015-01',
    'January 15, 2015; XC50-230mm II',
    '独立新闻稿印证月份；模型自身明确称无法给出可回指原文且按规则留空，却仍填日期，只有产品介绍链接，原依据不合格。'),
 '富士|相机镜头|xf8mmf3.5rwr': ('xf8', '2023-05',
    '24.05.2023; Introducing XF8mmF3.5 R WR',
    '独立公告印证月份；模型自身承认未取得首发公告原句，引用仅为产品页，原依据不合格。'),
 '富士|相机|fujifilmx-t50': ('xt50', '2024-05',
    '2024年5月16日; FUJIFILM X-T50',
    '独立日本公告印证首次公告月份；套机仅按机身族，非该镜头组合上市；原候选只有产品页且明确无法回指含日期原句，原依据不合格。'),
 '小米|REDMI路由器|xiaomi路由器be6500pro': ('be6500', '2023-10',
    '小米路由器 BE6500 Pro 发售于 2023 年 10 月',
    '报道指向2023-10，候选2023-09不获印证；原链接为200空壳，无日期，判错，不从报道反填候选。'),
}


if __name__ == '__main__':
    queue = json.loads((ROOT / 'review-queue.json').read_text())
    reviews = {}
    for brand, r in queue.items():
        if not r['samples']:
            continue
        samples = []
        for s in r['samples']:
            key, date, quote, reason = VERDICTS[s['family']]
            assert len(quote.split()) <= 25
            samples.append(dict(family=s['family'], candidate_sha256=s['candidate_sha256'],
                correct_date=date, date_correct=date == s['candidate']['release']['date'],
                identity_match=True, evidence_supported=False, correct=False,
                verification_url=SOURCES[key], verification_quote=quote,
                verdict_reason=reason, checked_at=datetime.now(timezone.utc).isoformat(),
                verification_capture='web-verification-capture.json + verification-sources/',
                original_citation_status='unsupported_or_unretrievable_not_a_date_source'))
        reviews[brand] = dict(seed=r['seed'], universe_sha256=r['universe_sha256'], samples=samples)
    cs = json.loads((ROOT / 'candidates.json').read_text())
    gates = brand_llm_gate(cs, reviews)
    write(ROOT / 'reviews.json', reviews)
    write(ROOT / 'brand-gates.json', gates)
    write(Path('data/llm/release-dates.json'), dict(schema=1, enabled=True,
        run='round5-20261103', candidates=cs, reviews=reviews,
        managed_ids=sorted({key for c in cs for key in c['ids']}),
        note='All assessed brands disabled. HP has no candidates and is unassessed. Disabling this file removes only its managed LLM dates on finalization.'))
    print(json.dumps(gates, ensure_ascii=False))
