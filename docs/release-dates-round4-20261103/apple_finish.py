import json
from capture import *
read={o['url'] for fn in ['apple-articles.json','apple-hardware-articles.json','apple-reviewed-recipes.json','apple-cn-reviewed-recipes.json'] for o in json.load(open(ROOT/fn))};out=[]
for u in json.load(open(ROOT/'apple-plan.json'))['selected']:
 if u not in read:out.append(get(u));save('apple-tail-articles.json',out)
print('DONE',len(out))
