"""Check generated local links and exact research bytes, without network."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import hashlib,json
R=Path(__file__).resolve().parents[1];D=R/'docs'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set();self.lang=False;self.h1=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='html':self.lang=attrs.get('lang')=='en'
        if tag=='h1':self.h1+=1
        if 'id' in attrs:self.ids.add(attrs['id'])
        for key in ['href','src']:
            if key in attrs:self.links.append(attrs[key])
pages={}
catalog=json.loads((R/'camden_work/data/catalog.json').read_text(encoding='utf8'))
catalog_fragments={e['id'] for e in catalog['entries']}|{a['alias_id'] for a in catalog['aliases']}
def valid_fragment(target,fragment,static_ids):
    return fragment in static_ids or (target==D/'catalog.html' and fragment in catalog_fragments)
for p in D.glob('*.html'):
    parser=Links();parser.feed(p.read_text(encoding='utf8'));pages[p]=parser
errors=[];links=0
for path,page in pages.items():
    if not page.lang or page.h1!=1:errors.append(path.name+': language or primary heading')
    for link in page.links:
        uri=urlsplit(link)
        if uri.scheme or uri.netloc:continue
        links+=1
        target=(path.parent/unquote(uri.path)).resolve() if uri.path else path
        if D.resolve() not in target.parents:errors.append(path.name+': escaping link '+link);continue
        if not target.is_file():errors.append(path.name+': missing '+link)
        elif uri.fragment and target in pages and not valid_fragment(target,unquote(uri.fragment),pages[target].ids):errors.append(path.name+': missing fragment '+link)
expected=(R/'camden_work/data/catalog.json').read_bytes()
if (D/'catalog.json').read_bytes()!=expected:errors.append('Research byte mismatch')
result={'pages':len(pages),'local_links_checked':links,'research_sha256':hashlib.sha256(expected).hexdigest(),'errors':errors,'scope':'Static links and structure only, not browser accessibility or publication acceptance'}
print(json.dumps(result));raise SystemExit(bool(errors))
