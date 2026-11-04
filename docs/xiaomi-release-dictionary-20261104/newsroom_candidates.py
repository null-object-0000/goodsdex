"""Propose branded product names from launch opening sentences and product headings.
Candidates require explicit dateline + launch wording. Review before dictionary import.
"""
from inspect_newsroom import OUT,ROOT,articles
import re,json,calendar
months={m:i for i,m in enumerate(calendar.month_name) if m}
words='(?:[0-9]+(?:[.][0-9]+)?(?:T|S|X|R|C|A|W|K|G|[a-z])?(?:[0-9]+)?|[A-Z][0-9]+[A-Za-z0-9]*|Pro|Plus|Ultra|Max|Lite|Fold|Flip|Compact|OLED|QLED|FHD|UHD|Mini|LED|RGB|NFC|eSIM|Bluetooth|Wireless|Turbo|Alpha|Book|Pad|Note|Watch|Buds|Band|Sound|Smart|Display|TV|Master|AI|Glasses|OpenWear|Stereo|Speaker|Electric|Scooter|Robot|Vacuum|Air|Purifier|Conditioner|Monitor|Projector|Portable|Instant|Photo|Printer|Hair|Dryer|Water|Kettle|Rice|Cooker|Humidifier|Dehumidifier|Front|Load|Washer|Refrigerator|Side-by-Side|Truclean|Wet|Dry|Fan|Clip|Neo|Play|Desktop|Gaming|Power|Bank|Pen|Keyboard|SU7|YU7|Standard|Leitzphone|powered|by|Anniversary|Edition|Sonic|Oscillation|Toothbrush|Massage|Gun|Outdoor|Camera|Solar|Panel|Router|Mesh|System|Wi-Fi|WiFi|Zoom|S1|S2|S3|S4|S5|GTS|Ceramic|Titanium)'
pattern=re.compile(r'\b(?:Xiaomi|Redmi|REDMI|MIJIA|Mijia|Mi)\s+'+words+r'(?:\s+'+words+r')*')
proposed=[]
for a in articles:
 t=a['text'];m=re.search(r'\b('+'|'.join(months)+r')\s+(\d{1,2})(?:st|nd|rd|th)?[,]?\s+(20\d{2})\b',t[:300])
 if not m:continue
 # Earnings releases describe past launches; never propagate their dateline.
 if not re.search(r'today.{0,70}(?:unveiled|announced|introduced|launched)|officially launched',t[:450],re.I):continue
 date=f'{m[3]}-{months[m[1]]:02}-{int(m[2]):02}'
 opening=t[m.end():];first=re.split(r'(?<=[.!?])\s+(?=[A-Z])',opening,maxsplit=1)[0]
 contexts=[first]+[h for h in a['headings'] if re.match(r'^(?:Xiaomi|Redmi|REDMI|MIJIA|Mijia|Mi) ',h)]
 names=sorted(set(v.group().strip() for ctx in contexts for v in pattern.finditer(ctx)))
 # RMB pricing + no explicit international launch indicates mainland scope.
 market='CN' if re.search(r'RMB|mainland China|Chinese Mainland',t,re.I) and not re.search('international markets|global markets|global market',first,re.I) else 'GLOBAL'
 for name in names:
  if name in ['Xiaomi AI','Xiaomi TV','Xiaomi Watch','Xiaomi Smart','Xiaomi Smart Band','Xiaomi Air','Xiaomi Pad','Redmi Note','Redmi','Xiaomi Power','Xiaomi Book']:continue
  i=t.index(name)
  proposed.append(dict(article_id=a['id'],product_name=name,date=date,market=market,opening=t[:len(t)-len(opening)+len(first)],product_quote=t[max(0,i-30):i+260]))
(OUT/'newsroom-candidates.json').write_text(json.dumps(proposed,ensure_ascii=False,indent=2)+'\n')
print('candidates',len(proposed))
