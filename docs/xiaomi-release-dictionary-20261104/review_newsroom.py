"""Human-reviewed product/event/market list from bulk official newsroom captures.
Translations are explicit aliases; global launches are excluded from CN matching.
"""
from extract import *

def build():
    articles={a['id']:a for a in read(OUT/'articles.json')}
    def add_group(id,date,items):
      a=articles[id];text=a['text'];cap=a['capture']
      # Dateline and product paragraph remain separate exact original excerpts.
      for name,needle,aliases in items:
       i=text.index(needle);parts=[text[:min(600,len(text))]]
       product=text[max(0,i-65):i+min(650,len(needle)+380)]
       if needle not in parts[0]:parts.append(product)
       path=ROOT/cap['capture_file'];path.with_suffix('.txt').write_text(text)
       e=dict(url=f'https://www.mi.com/global/discover/article/?id={id}',capture_url=cap['url'],
         sha256=cap['sha256'],captured_at=cap['captured_at'],capture_file=cap['capture_file'],
         quote='\n[…]\n'.join(parts),quote_parts=parts,text_file=str(path.with_suffix('.txt').relative_to(ROOT)),
         source_type='official',publisher='xiaomi',verified=True,hash_scope='response_bytes',
         locator='公开新闻正文 data.content；首段发布日期与产品段原文；[…] 分隔非连续片段')
       add(name,date,e,aliases,origin='official_newsroom')
    def simple(id,date,names):add_group(id,date,[(n,n,[]) for n in names])
    simple('6357','2026-09-07',['Xiaomi 18 Fold','Xiaomi Pad 9 Pro Max'])
    add_group('5825','2025-12-25',[
      ('Xiaomi 17 Ultra','Xiaomi 17 Ultra',[]),('Xiaomi 17 Ultra by Leica','Xiaomi 17 Ultra by Leica',['Xiaomi 17 Ultra 徕卡版']),
      ('Xiaomi Watch 5','Xiaomi Watch 5',[]),('Xiaomi Watch 5 eSIM','Xiaomi Watch 5 eSIM',[]),('Xiaomi Buds 6','Xiaomi Buds 6',[]),
      ('Xiaomi Smart Home Screen 11','Xiaomi Smart Home Screen 11',['Xiaomi 智能家庭屏 11']),
      ('Mijia Diffused Ceiling Light','Mijia Diffused Ceiling Light',['米家漫反射吸顶灯']),
      ('Mijia Central Air Conditioner Dual Fan Pro','Mijia Central Air Conditioner Dual Fan Pro',[])])
    simple('5471','2025-09-25',['Xiaomi 17','Xiaomi 17 Pro','Xiaomi 17 Pro Max'])
    # This article announces Pad 8 series without naming every model in its body.
    add_group('5471','2025-09-25',[('Xiaomi Pad 8系列','Xiaomi Pad 8 series',[])])
    add_group('6202','2026-05',[
      ('Xiaomi 17 Max','In May 2026, Xiaomi officially unveiled the Xiaomi 17 Max',[]),
      ('小米手环10 Pro','In May 2026, the Group launched the Xiaomi Smart Band 10 Pro',[])])
    # Earnings report dateline is not used for the May launch assertions above.
    simple('5172','2025-06-26',['Xiaomi MIX Flip 2','Xiaomi Pad 7S Pro 12.5'])
    add_group('5172','2025-06-26',[
      ('Xiaomi AI Glasses','Xiaomi AI Glasses',['小米AI眼镜']),
      ('Xiaomi Smart Band 10','Xiaomi Smart Band 10',[]),
      ('Xiaomi Watch S4 41mm','Xiaomi Watch S4 41mm',[]),
      ('Xiaomi OpenWear Stereo Pro','Xiaomi OpenWear Stereo Pro',['Xiaomi 开放式耳机 Pro'])])
    simple('4926','2025-05-22',['Xiaomi 15S Pro','Xiaomi Pad 7 Ultra'])
    add_group('4926','2025-05-22',[
      ('Xiaomi TV S Mini LED 2025','Xiaomi TV S Mini LED 2025',['小米电视S Mini LED 2025','小米电视S55 Mini LED 2025','小米电视S65 Mini LED 2025','小米电视S75 Mini LED 2025','小米电视S85 Mini LED 2025','小米电视S98 Mini LED 2025']),
      ('Mijia Dual-Drum Washer Dryer Pro 10kg','Mijia Dual-Drum Washer Dryer Pro 10kg',['米家双区洗衣机Pro 双洗烘10kg']),
      ('Mijia Smart Dual-tap Water Purifier Pro 1600G','Mijia Smart Dual-tap Water Purifier Pro 1600G',[])])
    add_group('3776','2024-10-29',[
      ('Xiaomi Smart Band 9 Pro','Xiaomi Smart Band 9 Pro',['小米手环9 Pro']),
      ('Xiaomi Watch S4','Xiaomi Watch S4',[]),
      ('Xiaomi Mesh System BE3600 Pro','Xiaomi Mesh System BE3600 Pro',['Xiaomi全屋路由 BE3600Pro']),
      ('Xiaomi Smart Door Lock M30系列','Xiaomi Smart Door Lock M30 Series',[]),
      ('Xiaomi 165W Power Bank 10000 (Integrated Cable)','Xiaomi 165W Power Bank 10000',['小米自带线充电宝10000 165W']),
      ('Mijia Air Conditioner Top-Outlet Pro 1.5HP Level 1+ Energy Efficiency','Mijia Air Conditioner Top-Outlet Pro 1.5HP Level 1+ Energy Efficiency',[]),
      ('Mijia Multi-zone Refrigerator 4 Glass Door 508L Pro','Mijia Multi-zone Refrigerator 4 Glass Door 508L Pro',[]),
      ('Xiaomi TV S Pro Mini LED 2025','Xiaomi TV S Pro Mini LED 2025',['小米电视S Pro Mini LED 2025']),
      ('Mijia Dual-drum Dual Washer Dryer 10kg','Mijia Dual-drum Dual Washer Dryer 10kg',[]),
      ('Mijia Advanced Washer Dryer 10kg Pro','Mijia Advanced Washer Dryer 10kg Pro',[])])
    simple('3777','2024-10-29',['Xiaomi 15','Xiaomi 15 Pro'])
    add_group('3777','2024-10-29',[
      ('Xiaomi 15 Custom Edition','Xiaomi 15 Custom Edition',['Xiaomi 15 定制版']),
      ('Xiaomi 15 Limited Edition','Xiaomi 15 Limited Edition',[]),
      ('Xiaomi Pad 7系列','Xiaomi Pad 7 Series',[])])
    simple('3464','2024-07-19',['Xiaomi MIX Fold 4','Xiaomi MIX Flip'])
    simple('3048','2023-10-26',['Xiaomi 14','Xiaomi 14 Pro','Xiaomi Watch S3'])
    add_group('3048','2023-10-26',[('Xiaomi S Pro Mini LED TV','Xiaomi S Pro Mini LED TV',[])])
    simple('2998','2023-08-14',['Xiaomi MIX Fold 3','CyberDog 2'])
    add_group('2998','2023-08-14',[
      ('Xiaomi Pad 6 Max 14','Xiaomi Pad 6 Max 14',[]),
      ('Xiaomi Smart Band 8 Pro','Xiaomi Smart Band 8 Pro',[]),
      ('Redmi K60 Ultra','Redmi K60 Ultra',['Redmi K60 至尊版'])])
    simple('2922','2023-04-18',['Xiaomi 13 Ultra'])
    simple('2830','2022-12-11',['Xiaomi 13','Xiaomi 13 Pro','Xiaomi Watch S2','Xiaomi Buds 4','Xiaomi Sound Pro','Xiaomi Router 10000','Xiaomi Mini PC'])
    simple('2802','2022-10-27',['Redmi Note 12 Pro','Redmi Note 12 Pro+','Redmi Note 12 5G','Redmi Note 12 DISCOVERY EDITION','Redmi Note 12 YIBO EDITION','Xiaomi Book Air 13','Mijia DD Combination Washer Dryer 12kg','Mijia Graphene Baseboard Heater'])
    simple('2665','2022-03-17',['Redmi K50','Redmi K50 Pro','Redmi AirDots 3 Pro Genshin Impact Edition'])
    simple('2644','2022-02-16',['Redmi K50G'])
    simple('2603','2021-12-28',['Xiaomi 12','Xiaomi 12 Pro'])
    simple('2458','2021-10-28',['Redmi Note 11 5G','Redmi Note 11 Pro','Redmi Note 11 Pro+'])
    return entries

if __name__=='__main__':
    build();write(OUT/'reviewed-newsroom-entries.json',entries);print(len(entries))
