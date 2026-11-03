"""Explicit model-to-article review recipes, not automatic family propagation."""
import json,re
from capture import *
base='https://www.apple.com.cn/newsroom/'
# IDs identify the complete model in the archive, without SKU/capacity expansion.
recipes=[
('2026/09/apple-debuts-iphone-18-pro-and-iphone-18-pro-max/','148590 148591','iPhone 18 Pro'),
('2026/09/apple-unveils-iphone-duo/','148588','iPhone Duo'),
('2026/09/introducing-apple-watch-series-12-with-the-all-new-health-sensing-system/','148589','Apple Watch Series 12'),
('2026/09/apple-unveils-apple-watch-ultra-4/','148758','Apple Watch Ultra 4'),
('2026/09/apple-introduces-airpods-5/','148759','AirPods 5'),
('2026/08/apple-introduces-mac-studio-with-m5-max-and-m5-ultra/','128107','Mac Studio'),
('2026/08/apple-unveils-powerful-mac-mini-with-m6-and-m5-pro/','128108','Mac mini'),
('2026/03/apple-introduces-airpods-max-2-powered-by-h2/','126620','AirPods Max 2'),
('2026/03/apple-introduces-the-new-macbook-air-with-m5/','126320 126321','M5'),
('2026/03/apple-introduces-stunning-studio-display-xdr/','126323 126324','Studio Display XDR'),
('2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/','126318 126319','M5 Pro'),
('2026/03/apple-introduces-iphone-17e/','126470','iPhone 17e'),
('2026/03/say-hello-to-macbook-neo/','126322','MacBook Neo'),
('2026/01/apple-introduces-new-airtag-with-expanded-range-and-improved-findability/','126203','AirTag'),
('2025/10/apple-unveils-new-14-inch-macbook-pro-with-the-m5-chip/','125405','M5'),
('2025/10/apple-vision-pro-upgraded-with-the-powerful-m5-chip-and-comfortable-dual-knit-band/','125436','M5'),
('2025/09/apple-debuts-iphone-17/','125089','iPhone 17'),
('2025/09/apple-unveils-iphone-17-pro-and-iphone-17-pro-max-cn/','125090 125091','iPhone 17 Pro'),
('2025/09/introducing-iphone-air-a-powerful-new-iphone/','125092','iPhone Air'),
('2025/09/apple-introduces-apple-watch-series-11-cn/','125093','Apple Watch Series 11'),
('2025/09/introducing-apple-watch-ultra-3-cn/','125095','Apple Watch Ultra 3'),
('2025/09/apple-introduces-apple-watch-se-3-cn/','125094','Apple Watch SE 3'),
('2025/09/introducing-airpods-pro-3-the-ultimate-audio-experience-cn/','125135','AirPods Pro 3'),
('2025/03/apple-unveils-new-mac-studio/','122211','Mac Studio'),
('2025/03/apple-introduces-the-new-macbook-air-with-m4-and-a-gorgeous-new-sky-blue-color/','122209 122210','M4'),
('2025/03/apple-introduces-ipad-air-with-powerful-m3-chip-new-magic-keyboard/','122240','A16'),
('2025/02/apple-debuts-iphone-16e/','122208','iPhone 16e'),
('2024/10/apples-new-macbook-pro-features-the-incredibly-powerful-m4-family-of-chips/','121552 121553 121554','M4'),
('2024/10/apples-all-new-mac-mini-is-even-more-mighty-and-more-mini/','121555','M4'),
('2024/10/apple-unveils-the-new-imac-with-the-powerful-m4-chip-available-in-fresh-colors/','121556 121557','M4'),
('2024/10/apple-introduces-powerful-new-ipad-mini-with-a17-pro/','121456','A17 Pro'),
('2024/09/apple-introduces-all-new-airpods-4-with-industry-defining-audio-and-design/','121203 121205','AirPods'),
('2024/09/introducing-apple-watch-series-10/','121202','Apple Watch Series 10'),
('2024/09/apple-introduces-iphone-16-iphone-16-plus/','121029 121030','iPhone 16'),
('2024/09/apple-debuts-iphone-16-pro-iphone-16-pro-max/','121031 121032','iPhone 16 Pro'),
('2024/03/apple-unveils-the-new-13-and-15-inch-macbook-air-with-the-powerful-m3-chip/','118551 118552','M3'),
('2024/06/apple-vision-pro-arrives-in-new-countries-and-regions-beginning-june-28/','117810','Apple Vision Pro'),
('2023/10/apple-supercharges-24-inch-imac-with-new-m3-chip/','117733 117734','M3'),
('2023/09/apple-upgrades-airpods-pro-2nd-generation-with-usb-c-charging/','111834','USB-C'),
('2023/09/apple-introduces-the-advanced-new-apple-watch-series-9/','111833','Apple Watch Series 9'),
('2023/09/apple-unveils-iphone-15-pro-and-iphone-15-pro-max/','111828 111829','iPhone 15 Pro'),
('2023/09/apple-debuts-iphone-15-and-iphone-15-plus/','111830 111831','iPhone 15'),
('2023/06/apple-unveils-new-mac-studio-and-brings-apple-silicon-to-mac-pro/','111343 111835 111836','Mac Pro'),
('2023/06/apple-introduces-the-15-inch-macbook-air/','111346','M2'),
('2022/10/apple-unveils-completely-redesigned-ipad-in-four-vibrant-colors/','111840','iPad'),
('2022/09/apple-debuts-iphone-14-pro-and-iphone-14-pro-max/','111846 111849','iPhone 14 Pro'),
('2022/09/apple-reveals-apple-watch-series-8-and-the-new-apple-watch-se/','111848 111853','Apple Watch'),
('2022/09/apple-announces-the-next-generation-of-airpods-pro/','111851','AirPods Pro'),
('2022/06/apple-unveils-all-new-macbook-air-supercharged-by-the-new-m2-chip/','111869','MacBook Pro'),
('2022/03/apple-announces-the-new-iphone-se-a-powerful-smartphone-in-an-iconic-design/','111866','iPhone SE'),
('2021/09/apple-reveals-apple-watch-series-7-featuring-the-largest-most-advanced-display/','111909','Apple Watch Series 7'),
('2020/11/introducing-the-next-generation-of-mac/','111883 111893 111894','M1'),
('2020/10/apple-introduces-homepod-mini-a-powerful-smart-speaker-with-amazing-sound/','111914','HomePod mini'),
('2020/04/iphone-se-a-powerful-new-smartphone-in-a-popular-design/','111882','iPhone SE'),
('2020/03/new-macbook-air-has-more-to-love-and-is-now-just-999/','111991','MacBook Air'),
('2019/11/apple-introduces-16-inch-macbook-pro-the-worlds-best-pro-notebook/','111932','MacBook Pro'),
('2019/09/apple-introduces-dual-camera-iphone-11/','111865','iPhone 11'),
('2019/09/iphone-11-pro-and-iphone-11-pro-max-the-most-powerful-and-advanced-smartphones/','111878 111879','iPhone 11 Pro'),
('2019/09/apple-introduces-new-version-of-the-most-popular-ipad-starting-at-329/','111911','iPad'),
('2019/03/all-new-ipad-air-and-ipad-mini-deliver-dramatic-power-and-capability/','111904 111939','iPad'),
('2019/03/airpods-the-worlds-most-popular-wireless-headphones-are-getting-even-better/','111856','AirPods'),
('2018/10/new-mac-mini-packs-huge-punch/','111912','Mac mini'),
('2018/09/apple-introduces-iphone-xr/','111868','iPhone X'),
('2018/09/iphone-xs-and-iphone-xs-max-bring-the-best-and-biggest-displays-to-iphone/','111880 111881','iPhone X'),
('2018/07/apple-updates-macbook-pro-with-faster-performance-and-new-features-for-pros/','111925 111949','MacBook Pro'),
('2018/03/apple-introduces-new-9-7-inch-ipad-with-apple-pencil-support/','111957','iPad'),
('2017/09/iphone-8-and-iphone-8-plus-a-new-generation-of-iphone/','111950 111976','iPhone 8'),
('2017/09/the-future-is-here-iphone-x/','111864','iPhone X'),
('2017/06/ipad-pro-10-5-and-12-9-inch-models-introduces-worlds-most-advanced-display-breakthrough-performance/','111927 111964','iPad Pro'),
('2016/10/apple-unveils-groundbreaking-new-macbook-pro/','111975 112003','MacBook Pro'),
]
rows=json.load(open('/tmp/goodsdex-round3-published-goods.json'));by={r['id']:r for r in rows};out=[];rejected=[]
for suffix,ids,token in recipes:
 o=get(base+suffix);s=o['text'];keys=['GLOBAL:apple_support:model:'+key for key in ids.split()]
 if o.get('http_status')!=200 or not o.get('captured_at') or token not in s:
  rejected.append(dict(url=base+suffix,ids=keys,reason='capture/date/exact token unavailable'));continue
 m=re.search(r'(20\d{2}) 年 (\d{1,2}) 月 (\d{1,2}) 日',s)
 if not m:rejected.append(dict(url=o['url'],reason='no CN dated announcement'));continue
 date=f'{m[1]}-{int(m[2]):02}'
 # Header and first announcement paragraph, retaining model-specific identity later in body via locator.
 anchor=s.find(token,m.end());end=s.find('。',max(m.end()+700,anchor+len(token)))
 if end<0:end=m.end()+1500
 quote=s[m.start():end+1]
 identity='Chinese Newsroom header '+m[0]+'; reviewed exact model(s): '+', '.join(by[k]['name'] for k in keys)+'; token '+token+'; announcement only, not sale. No SKU/capacity expansion.'
 out.append(dict(url=o['url'],ids=keys,date=date,start=m[0],end=quote[-100:],identity_token=token,identity=identity))
 save('apple-reviewed-recipes.json',out);save('apple-rejected.json',rejected)
print('recipes',len(out),'ids',sum(len(a['ids']) for a in out),'rejected',rejected)
