"""Reviewed independent daily-news archive corroborations of existing batches only."""
from extract import *
from goodsdex.release_crosschecks import delta_days

def build():
    records=[json.loads(l) for l in (OUT/'fetches.jsonl').read_text().splitlines()]
    reviewed=[]
    def add(bid,date,needles,reason,length=1200):
      url='https://news.mydrivers.com/blog/'+date.replace('-','')+'.htm';c=next(c for c in records if c['url']==url)
      assert not c.get('error')
      txt=Path(ROOT/c['capture_file']).with_suffix('.txt');t=compact(txt.read_text());parts=[]
      for needle in needles:
       i=t.index(compact(needle));parts.append(t[i:i+length])
      e=dict(url=url,capture_url=url,captured_at=c['captured_at'],sha256=c['sha256'],capture_file=c['capture_file'],
        text_file=str(txt.relative_to(ROOT)),quote='\n[…]\n'.join(parts),quote_parts=parts,
        publisher='mydrivers',source_type='third_party',verified=True,hash_scope='response_bytes',
        locator='快科技公开当日日志正文；仅移除排版空白，片段以 […] 分隔；原始供稿署名及同日发布/开售语句均已核对')
      reviewed.append(dict(batch_id=bid,date=date,evidence=e,reason=reason))
    add('mi-tv-s-mini-led-202505','2025-05-22',['小米首款低反屏55-98英寸全覆盖！小米电视SMiniLED2025系列发布'],
        '同一2025代MiniLED低反屏系列，55/65/75/85/98首发尺寸；不包含2026款。')
    add('mi-robot-5pro-202508','2025-08-08',['小米最强扫地机！米家扫拖机器人5Pro开售'],
        '同为5 Pro首销，两种基站版本；不扩给5C或6系列。')
    add('mi-robot-m40s-202505','2025-05-10',['小米发布米家扫拖机器人M40S'],
        '同为M40S公开推出、上架预约消息；同水箱/自动上下水两版本，非M30S或M40。')
    add('mi-reviewed-1002763','2026-09-15',['小米最强画质！小米电视SProRGB-MiniLED2027开售'],
        'RGB三色背光2027代首销；明确65/75/85/98四尺寸，不含普通2026MiniLED。')
    add('mi-reviewed-0936839','2026-04-08',['小米SMiniLED2026系列预售'],
        '同一2026系列首次官宣，55/65/75/85/100五尺寸及分区均一致；不是后续至尊版。')
    add('mi-reviewed-1006141','2026-09-23',['1699元米家智能洗碗机台式5套开售'],
        '同一台式5套超薄折叠门35cm产品当日正式开售，不是嵌入式。')
    add('mi-reviewed-1006074','2026-09-23',['小米最大容量！米家智能洗碗机嵌入式20套上市'],
        '同一20套156L新款，黑/白配色，BLDC52000Pa；同为上市开售消息。')
    add('mi-reviewed-1006031','2026-09-23',['国补价129.2元起！小米发布米家筒/射灯3Pro系列'],
        '同一三款3 Pro灯具首发组合，含人在感应版；不是2代。')
    add('mi-reviewed-1006044','2026-09-23',['小米智能门锁5Max内外双摄发布','国补价2999.65元起！小米智能门锁5Max今日开售'],
        '同一5 Max普通/内外双摄两版本，原主文已冻结的深锖色身份，UWB/双摄/价格一致。')
    add('mi-reviewed-0337624','2017-12-07',['普及全面屏！红米5、5Plus正式发布'],
        '明确红米5 16/32GB、5Plus32/64GB首发，基础页与规格页同批；不扩后加内存。',1500)
    add('mi-reviewed-0362532','2018-05-31',['作为小米公司8周年旗舰手机，小米8已经正式发布','小米8SE','3699元！小米8透明探索版发布'],
        '同为5月31日首发8/8SE/透明探索版；不含9月屏幕指纹版或青春版。',1200)
    add('mi-reviewed-0352847','2018-03-27',['3299元！小米MIX2S正式发布'],
        '同一黑白首发MIX2S，非后续翡翠色。')
    add('mi-reviewed-1006476','2026-09-23',['首发第六代骁龙8至尊版！小米18Pro系列发布','小米发布会9大新品汇总'],
        '同一9月23日秋季发布会18Pro/ProMax与Pad9/9Pro，非9月7日18Fold/Pad9ProMax。',2000)
    add('mi-reviewed-0952625','2026-05-21',['1999元！小米推出米家无线吸尘器4Max'],
        '同一280AW、15万转电机、自动集尘基站4 Max新品宣布推出/开启预售，非4C。')
    return reviewed
if __name__=='__main__':
    write(OUT/'reviewed-secondary.json',build());print('reviewed secondary',len(build()))
