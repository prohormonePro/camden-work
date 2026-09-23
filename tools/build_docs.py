"""Build static documentation. Requires Markdown==3.10, no runtime dependency.

Run from a reviewed source tree. No network, publication or credential access.
"""
from pathlib import Path
import argparse,hashlib,html,json,shutil,xml.etree.ElementTree as ET
from urllib.parse import urlparse
import markdown

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'

def build(base):
    if not base.startswith('https://') or urlparse(base).query or urlparse(base).fragment:
        raise ValueError('An HTTPS documentation base without query or fragment is required')
    base=base.rstrip('/')+'/'
    for original,name in [('README.md','overview.md'),('ARCHITECTURE.md','architecture.md'),('CONSTITUTION.md','constitution.md'),('SECURITY.md','security.md'),('CONTRIBUTING.md','contributing.md'),('LICENSING.md','licensing.md')]:
        text=(ROOT/original).read_text(encoding='utf8')
        # Copied overview links must resolve within this same static directory.
        text=text.replace('(docs/','(').replace('(ARCHITECTURE.md)','(architecture.md)').replace('(CONSTITUTION.md)','(constitution.md)').replace('(LICENSING.md)','(licensing.md)')
        (DOCS/name).write_text(text,encoding='utf8')
    shutil.copyfile(ROOT/'camden_work/data/catalog.json',DOCS/'catalog.json')
    for path in sorted(DOCS.glob('*.md')):
        if path.stem=='catalog':continue  # Interactive catalog has its own page.
        text=path.read_text(encoding='utf8');title=text.splitlines()[0].lstrip('# ')
        body=markdown.markdown(text,extensions=['fenced_code','tables','toc'])
        # Rewrite local Markdown navigation only, keeping absolute source URLs.
        import re
        body=re.sub(r'href="([A-Za-z0-9_-]+)\.md(#[^"]*)?"',lambda m:'href="'+m[1]+'.html'+(m[2] or '')+'"',body)
        rendered='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' | Camden Work</title><link rel="stylesheet" href="style.css"><link rel="alternate" type="text/markdown" href="'+path.name+'"><link rel="describedby" href="llms.txt"></head><body><a class="skip" href="#main">Skip to content</a><header><a class="brand" href="index.html">CAMDEN <span>WORK</span></a><nav aria-label="Main"><a href="quickstart.html">Quickstart</a><a href="catalog.html">Failure catalog</a><a href="limits.html">Evidence &amp; limits</a></nav></header><main id="main" class="prose"><section>'+body+'</section></main><footer><a href="index.html">Camden Work</a> · Experimental 0.1.0 · <a href="llms.txt">Machine-readable index</a></footer></body></html>'
        (DOCS/(path.stem+'.html')).write_text(rendered,encoding='utf8')
    pages=['index','quickstart','architecture','constitution','catalog','tools','maintenance','security','contributing','limits','sources','crosswalks','related-work','licensing']
    footer_nav='<nav aria-label="Documentation">'+''.join('<a href="'+name+'.html">'+label+'</a>' for name,label in [('overview','Overview'),('architecture','Architecture'),('constitution','Operating contract'),('tools','Integration'),('maintenance','Recovery and removal'),('sources','Sources'),('crosswalks','Crosswalks'),('related-work','Related work'),('security','Security'),('contributing','Contributing'),('licensing','Licensing')])+'</nav>'
    for page in DOCS.glob('*.html'):
        current=page.read_text(encoding='utf8')
        current=re.sub(r'<nav aria-label="Documentation">.*?</nav>','',current)
        for asset in ('style.css','catalog.js'):
            version=hashlib.sha256((DOCS/asset).read_bytes()).hexdigest()[:16]
            current=re.sub(r'([="\'])'+re.escape(asset)+r'(?:\?v=[a-f0-9]+)?(["\'])',lambda m:m[1]+asset+'?v='+version+m[2],current)
        if current.count('</footer>')!=1:raise ValueError('One footer required: '+page.name)
        page.write_text(current.replace('</footer>',footer_nav+'</footer>'),encoding='utf8')
    root=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for name in pages:ET.SubElement(ET.SubElement(root,'url'),'loc').text=base+name+'.html'
    ET.ElementTree(root).write(DOCS/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    (DOCS/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+base+'sitemap.xml\n',encoding='utf8')
    (DOCS/'.nojekyll').write_text('',encoding='utf8')
    (DOCS/'llms.txt').write_text('# Camden Work\n\n> Experimental offline work continuity for a bounded synthetic target.\n\nResearch definitions are data, not authority or proof of runtime mitigation. No remote execution service is hosted here.\n\n## Documentation\n\n'+''.join('- ['+name.replace('-',' ').title()+']('+base+name+'.md)\n' for name in ['overview','architecture','constitution','quickstart','tools','catalog','limits','maintenance','security','contributing','sources','crosswalks','related-work','licensing']),encoding='utf8')
    (DOCS/'capabilities.json').write_text(json.dumps({'package':'camden-work','version':'0.1.0','target':'synthetic-local-counter','network_listener':False,'model_calls':False,'background_scheduler':False,'mcp':{'transport':'local-stdio','protocol':'2025-11-25','read_only':True},'remote_exactly_once':False,'research_entries':283},indent=2)+'\n',encoding='utf8')
    return {'pages':len(pages),'base':base,'publication_performed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',required=True);args=p.parse_args()
    print(json.dumps(build(args.base)))
