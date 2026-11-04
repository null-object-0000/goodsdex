from crawl import capture,OUT
import json
for url in json.loads((OUT/'secondary-urls.json').read_text()):capture(url)
