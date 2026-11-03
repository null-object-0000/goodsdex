import json,re
from capture import *
rows=json.load(open('/tmp/goodsdex-round4-before.json'));by={r['id']:r for r in rows};out=[]
def recipe(suffix,parts,token,proof):
 o=get('https://www.apple.com.cn/newsroom/'+suffix);s=o['text'];ids=['CN:apple_cn:commodity:'+p+'/A' for p in parts.split()]
 for key in ids:assert key in by and not by[key].get('release')
 m=re.search(r'(20\d{2}) 年 (\d{1,2}) 月 (\d{1,2}) 日',s);assert m and token in s
 # Include the configuration-specific price/availability section as well as the header.
 end=s.find('分享文章',m.end());end=end if end>=0 else len(s)
 quote=s[m.start():end].strip();out.append(dict(url=o['url'],date=f'{m[1]}-{int(m[2]):02}',ids=ids,start=m[0],end=quote[-100:],identity_token=token,identity=proof,event='announcement'))
recipe('2024/09/apple-introduces-iphone-16-iphone-16-plus/','MYEV3CH MYEW3CH MYEX3CH MYEY3CH MYF03CH','128GB、256GB、512GB','All five exact IDs are iPhone 16 128GB in the five explicitly enumerated colors; article explicitly enumerates 128GB and these colors. No other capacities or iPhone Plus copied. CN dated announcement only.')
recipe('2026/03/apple-introduces-airpods-max-2-powered-by-h2/','MHWK4CH MHWL4CH MHWM4CH MHWN4CH MHWP4CH','AirPods Max 2','Exact AirPods Max 2 and five explicitly named colors midnight/starlight/blue/orange/purple. March announcement; April shipping promise is not recorded as March sale.')
recipe('2026/10/apple-announces-the-next-generation-of-homepod-mini/','MGHJ4CH MGHK4CH MGHL4CH MGHM4CH MGKR4CH','HomePod mini 2','Exact second-generation mini and five explicitly named colors: midnight/white/green/blue/pink; not earlier HomePod mini or full HomePod. Announcement only.')
recipe('2025/09/introducing-airpods-pro-3-the-ultimate-audio-experience-cn/','MFHP4CH','AirPods Pro 3','Exact current product name AirPods Pro 3, no storage/color/package variants; September CN announcement only.')
# Current exact display variants are explicitly offered in every named glass/stand combination.
recipe('2026/03/apple-introduces-stunning-studio-display-xdr/','MFEL4CH MFEN4CH MFEP4CH MFEQ4CH MFEW4CH MFEX4CH MFEY4CH MFF04CH MFF14CH MFF24CH','VESA','2026 display generation; XDR: height/tilt or VESA, standard/nano glass; Studio Display: tilt or height/tilt or VESA, standard/nano glass. All choices explicitly enumerated in pricing section; excludes previous display generation. Announcement only.')
save('apple-cn-reviewed-recipes.json',out);print('CN exact IDs',sum(len(a['ids']) for a in out))
