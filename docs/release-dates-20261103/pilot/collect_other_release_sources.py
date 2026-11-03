import sys,concurrent.futures,hashlib,json
from pathlib import Path
sys.path.insert(0,'/tmp');from release_probe import get
urls=['https://www.hpstore.cn/hp-245-14-inch-notebook-pc-7y0y4pc.html','https://www.ithome.com/0/695/691.htm','https://www.gsmarena.com/apple_iphone_14-11861.php','https://www.fujifilm.com/ae/en/news/hq/9421','https://www.fujifilm.com/jp/ja/news/list/9421','https://support.apple.com/zh-cn/111850','https://www.mi.com/xiaomi-14/specs','https://item.jd.com/100053477906.html','https://search.jd.com/Search?keyword=7Y0Y4PC','https://www.fujifilm-x.com/global/products/cameras/x-s20/specifications/']
for o in concurrent.futures.ThreadPoolExecutor(5).map(get,urls):
 p=Path('docs/release-dates-20261103/evidence')/(hashlib.sha256(o['url'].encode()).hexdigest()[:16]+'.json');p.write_text(json.dumps(o,ensure_ascii=False,indent=1));print(o['url'],o.get('error',o.get('bytes')),flush=True)
