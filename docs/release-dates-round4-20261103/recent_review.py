import json,re
from capture import *
rows=json.load(open('/tmp/goodsdex-round3-published-goods.json'));a=json.load(open('docs/release-dates-round3-20261103/dji-archive-discovery.json'))
out=[]
for x in a['selected']:
 o=get('https://www.dji.com/cn/media-center/announcements/'+x['slug']);s=o['text'];end=s.find('探索更多');s=s[:end] if end>=0 else s
 starts=[m.start() for m in re.finditer('售价(?:与|及|和)|价格(?:与|及)|发售(?:与|及|和)|发售价格',s)]
 section=s[starts[-1]:] if starts else s
 out.append(dict(entry=x,capture=o,section=section))
save('dji-recent-review.json',out)
for a in out:
 if re.search('sdr-transmission-2|pocket-4p|rs-5|mobile-8-cn|fast-charger|matrice-4|goggles-n3|expansion-battery|75mm|mic-2|8k|power$|transmission-cn|mavic3-pro|rc-motion|o4-air',a['entry']['slug']):print(a['entry']['slug'],'\n',a['section'][:2300],'\n')
