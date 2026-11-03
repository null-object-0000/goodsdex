import json
from capture import *
out=[]
for u in json.load(open(ROOT/'apple-hardware-plan.json'))['selected']:
 out.append(get(u));save('apple-hardware-articles.json',out)
