"""Parse DJI public HTML without executing JavaScript (adapted from verified 2026-10-25 probe)."""
import html
import json
import re
from html.parser import HTMLParser

def plain(s):
    s = re.sub(r'<(?:br\b[^>]*|/p|/li|/h\d)>', '\n', s, flags=re.I)
    return re.sub(r'[ \t]+',' ',html.unescape(re.sub(r'<[^>]+>','',s))).strip()

class Scripts(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.items=[]; self.current=None; self.feed(source)
    def handle_starttag(self, tag, attrs):
        if tag=='script': self.current=[dict(attrs),'']
    def handle_data(self, data):
        if self.current is not None: self.current[1]+=data
    def handle_endtag(self, tag):
        if tag=='script' and self.current is not None:
            self.items.append(self.current); self.current=None

def embedded(source):
    ld=[]; state={}; markers=[]
    for attrs, body in Scripts(source).items:
        if attrs.get('type')=='application/ld+json':
            try: ld.append(json.loads(body))
            except ValueError: pass
        for name in ['__NUXT__','__INITIAL_STATE__','__PRELOADED_STATE__','__NEXT_DATA__']:
            if name in body or attrs.get('id')==name: markers.append(name)
        m=re.search(r'window\.__PRELOADED_STATE__\s*=\s*',body)
        if m:
            try: state=json.JSONDecoder().raw_decode(body[m.end():])[0]
            except ValueError: pass
    return ld,state,sorted(set(markers))

def parameters(source):
    # Keep order and duplicate labels: values belong to distinct components.
    result=[]
    group=''
    tokens=re.finditer(r'<h3\b[^>]*>.*?</h3>|<ul\b[^>]*class="[^"]*detailed-parameter-list[^"]*"[^>]*>.*?</ul>',source,re.S)
    for token in tokens:
        block=token.group()
        if block.startswith('<h3'): group=plain(block); continue
        key=re.search(r'<h4\b[^>]*>(.*?)</h4>',block,re.S)
        value=re.search(r'<div\b[^>]*class="detailed-parameter-value"[^>]*>(.*?)</div>',block,re.S)
        if key and value:
            result.append({'section':group or None,'key':plain(key[1]),'value':plain(value[1])})
    if not result:
        for group in re.split(r'<h4[^>]*class="[^"]*specs-group-title[^"]*"[^>]*>', source)[1:]:
            title=plain(group.split('</h4>',1)[0])
            for key,value in re.findall(r'<strong[^>]*class="[^"]*specs-detail-key[^"]*"[^>]*>(.*?)</strong><div[^>]*>(.*?)</div>',group,re.S):
                result.append({'section':title,'key':plain(key),'value':plain(value)})
    return result
