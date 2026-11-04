# 发布后真实 API 摘录

/api/meta：

```json
{
  "revision": "f5699bf587db43969d4b8169ed7c2907",
  "total_published": 2902,
  "release_scope": {
    "policy": "machine-release-v1",
    "label": "整机口径覆盖率",
    "denominator": "machine",
    "counting_unit": "published_rows",
    "total": 2902,
    "tiers": {
      "machine": 2554,
      "accessory": 256,
      "third_party_selection": 92
    },
    "brands": {
      "Apple": {
        "total": 639,
        "machine": 639,
        "accessory": 0,
        "third_party_selection": 0,
        "product_covered": 417,
        "series_only_covered": 0,
        "covered": 417,
        "missing": 222,
        "coverage": 0.6525821596244131,
        "product_coverage": 0.6525821596244131
      },
      "比亚迪": {
        "total": 14,
        "machine": 14,
        "accessory": 0,
        "third_party_selection": 0,
        "product_covered": 3,
        "series_only_covered": 0,
        "covered": 3,
        "missing": 11,
        "coverage": 0.21428571428571427,
        "product_coverage": 0.21428571428571427
      },
      "大疆": {
        "total": 281,
        "machine": 275,
        "accessory": 6,
        "third_party_selection": 0,
        "product_covered": 96,
        "series_only_covered": 0,
        "covered": 96,
        "missing": 179,
        "coverage": 0.3490909090909091,
        "product_coverage": 0.3490909090909091
      },
      "富士": {
        "total": 63,
        "machine": 24,
        "accessory": 39,
        "third_party_selection": 0,
        "product_covered": 5,
        "series_only_covered": 0,
        "covered": 5,
        "missing": 19,
        "coverage": 0.20833333333333334,
        "product_coverage": 0.20833333333333334
      },
      "惠普": {
        "total": 218,
        "machine": 218,
        "accessory": 0,
        "third_party_selection": 0,
        "product_covered": 0,
        "series_only_covered": 0,
        "covered": 0,
        "missing": 218,
        "coverage": 0.0,
        "product_coverage": 0.0
      },
      "小米": {
        "total": 1684,
        "machine": 1381,
        "accessory": 211,
        "third_party_selection": 92,
        "product_covered": 82,
        "series_only_covered": 96,
        "covered": 178,
        "missing": 1203,
        "coverage": 0.12889210716871832,
        "product_coverage": 0.05937726285300507
      },
      "小米汽车": {
        "total": 3,
        "machine": 3,
        "accessory": 0,
        "third_party_selection": 0,
        "product_covered": 3,
        "series_only_covered": 0,
        "covered": 3,
        "missing": 0,
        "coverage": 1.0,
        "product_coverage": 1.0
      }
    },
    "note": "对外只报整机口径覆盖率；同时披露配件周边和第三方精选条数。单品与系列分列，LLM和页面首存不计入。"
  }
}
```

3个真实 /api/goods/<id>：

```json
[
  {
    "id": "CN:dji:sku:192291",
    "name": "DJI ROMO P 扫地机器人（水箱版）",
    "release": {
      "date": "2025-08",
      "source": "third_party",
      "event": "announcement",
      "display_allowed": true,
      "crosscheck_status": "corroborated",
      "crosscheck_delta_days": 0
    },
    "sources": [
      {
        "date": "2025-08-06",
        "event": "announcement",
        "url": "https://www.ithome.com/0/873/541.htm",
        "quote": "大疆今晚发布了旗下首款扫地机器人 ROMO 系列 ，具备“旗舰无人机的精密感知与机电技术”，还有自清洁功能。 大疆 ROMO 系列官方介绍亮点如下： 优雅未来感设计，提升家居格调 旗舰无人机感知系统，毫米级避障，0 干预通行 25000 Pa 绝尘吸力，席卷脏污 柔性双机械臂，100% 贴边无死角 164 ml 超大容量机载水箱，持续湿拖清除重污 0 缠绕双滚刷，无惧超长毛发，免维护 独创高压自冲洗技术，基站 200 天免维护 独创消音舱设计，过滤 80%"
      },
      {
        "date": "2025-08-06",
        "event": "announcement",
        "url": "https://news.mydrivers.com/1/1066/1066711.htm",
        "quote": "快科技8月6日消息，今晚，大疆首款扫地机器人系列DJI ROMO正式发布，包含ROMO P、ROMO A、ROMO S三个型号，其中最入门的DJI ROMO S扫地机器人（水箱版）起售价4699元，支持国补。 这款扫地机器人之前被曝光时，就因为独特的透明基站被关注。 ROMO P采用透明机器人与透明基站设计，为行业唯一透明基站，兼具极简美学与精密机械质感，可提升家居格调；ROMO A为透明机器人搭配白色基站，ROMO S则为白色机器人与白色基站。 全系搭载"
      }
    ]
  },
  {
    "id": "CN:mi_cn:product:8152",
    "name": "小米8 SE 6GB+64GB",
    "release": {
      "date": "2018-05",
      "source": "third_party",
      "event": "announcement",
      "display_allowed": true,
      "crosscheck_status": "corroborated",
      "crosscheck_delta_days": 0
    },
    "sources": [
      {
        "date": "2018-05-31",
        "event": "announcement",
        "url": "https://www.ithome.com/0/362/555.htm",
        "quote": "5⽉31⽇下午2点，深圳大运中⼼， ⼀场有史以来规模最大的小米发布会 。 本次发布会上，小米发布了多达7款新品！是不是有点懵？没关系！话不多说，IT之家为小伙伴们奉上今天的发布新品汇总！ 一、跑分怒破30万的小米8旗舰手机 全球首款双频GPS，超精准定位手机，2699元起 小米8搭载高通骁龙845处理器，正面采用6.21\"三星AMOLED屏幕，支持P3广色域，色彩鲜艳通透；背部采用特有的“水滴弧形”设计，四曲面玻璃机身与7系铝边框精密衔接，机身相当于5.5"
      },
      {
        "date": "2018-05-31",
        "event": "announcement",
        "url": "https://news.mydrivers.com/1/579/579904.htm",
        "quote": "5月31日，小米在深圳发布小米8，同时还带来了一款小屏旗舰小米8 SE，该机首发高通骁龙710SoC，售价1799元起，非常具有竞争力。 小米8 SE将在6月8日（今天）上午10点正式开售，4GB RAM+64GB ROM售价1799元起，6GB RAM+64GB ROM售价1999元起。 配置方面，小米8 SE采用5.88英寸全面屏（相当于传统5.2英寸机身握感），屏幕为三星AMOLED，配置上首发高通骁龙710，配备4/6GB内存，电池容量为3120m"
      }
    ]
  },
  {
    "id": "CN:byd:car:han:2023:dmi",
    "name": "比亚迪 汉 2023款 DM-i",
    "release": {
      "date": "2023-05",
      "source": "third_party",
      "event": "announcement",
      "display_allowed": true,
      "crosscheck_status": "corroborated",
      "crosscheck_delta_days": 0
    },
    "sources": [
      {
        "date": "2023-05-18",
        "event": "announcement",
        "url": "https://news.mydrivers.com/1/910/910685.htm",
        "quote": "5月18日，比亚迪汉DM-i冠军版、DM-p战神版上市发布会如期举行。会上，比亚迪汉DM-i冠军版、DM-p战神版正式上市。 其中，汉DM-i冠军版共计推出6款车型，售价18.98-24.98万元，新增冰川蓝车色，内饰配置将有所升级，同时，新增纯电续航200km版本。 而汉DM-p战神版推出1款车型，售价28.98万元，新车为比亚迪官方改装版本， 新车在现款汉DM-p车型基础上，进行了运动化的装饰，外观与内饰更运动化。 同时，新车还首搭了比亚迪云辇-C智能"
      },
      {
        "date": "2023-05-18",
        "event": "announcement",
        "url": "https://www.ithome.com/0/694/151.htm",
        "quote": "IT之家 5 月 22 日消息，比亚迪汉 DM-i 冠军版 / 汉 DM-p 战神版将于 5 月 18 日正式上市，前者售价区间为 18.98 万-24.98 万元，起售价相比老款车型降低 1 万元，后者售价 28.98 万元。 新车都有不同程度的升级 ，比如汉 DM-i 冠军版增加了一款纯电续航 200km 的版本，汉 DM-p 战神版配备了云辇-C 智能阻尼车身控制系统。 比亚迪汽车官方 5 月 21 日表示，汉 DM-i 冠军版 / DM-p 战神版"
      }
    ]
  }
]
```
