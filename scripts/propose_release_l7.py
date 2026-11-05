"""Identity-only LLM proposals. Output is untrusted until captured and reviewed."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
from goodsdex.vision_extract import GATEWAY, _api_key

ROOT = Path('docs/release-coverage/L7')
PROMPT = '''逐型号提供中国大陆首次发布年月候选和可核验新闻链接。只能用官方站、IT之家、快科技、新浪科技/财经、中关村在线、太平洋电脑网、维基百科；亚朵亦可官方公众号。禁止猜月份、编URL和引文。没有确知URL就留空。不得把系列日期给单型号，不得跨代际/Pro/SE/季节，不得把评测/促销/旧款上架当首次发布。仅年份不够。输出严格JSON数组，每项 {"id":"输入id","name":"原名","date":"YYYY-MM或null","url":"完整URL或null","quote":"确知原文或null","reason":"依据或弃权原因"}。只处理输入身份，不使用任何内部已有日期。输入：'''

def work(batch):
    prompt = PROMPT + json.dumps(batch, ensure_ascii=False)
    key = hashlib.sha256(prompt.encode()).hexdigest()[:20]
    path = ROOT/'proposals'/f'{key}.json'
    if path.exists(): return
    path.parent.mkdir(parents=True, exist_ok=True)
    (path.parent/f'{key}.prompt.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2))
    body = dict(model='flowlet-flash', messages=[dict(role='user', content=prompt)], temperature=0,
                max_tokens=7000, reasoning_effort='none', enable_thinking=False)
    try:
        req = urllib.request.Request(GATEWAY.rstrip('/')+'/v1/chat/completions',data=json.dumps(body).encode(),
            headers={'Authorization':'Bearer '+(_api_key() or ''),'Content-Type':'application/json'})
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=180) as response:
            result=json.load(response)
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2))
        print(key,'ok',flush=True)
    except Exception as error:
        path.with_suffix('.error.json').write_text(json.dumps(dict(error=str(error))))
        print(key,str(error),flush=True)

if __name__=='__main__':
    rows=json.loads((ROOT/'targets.json').read_text())
    # Exact names only; no family expansion and no date-containing input fields.
    unique=list({(r['id'],r['name']):r for r in rows}.values())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(work,[unique[i:i+10] for i in range(0,len(unique),10)]))
