from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];D=R/'docs'
c=json.loads((R/'camden_work/data/catalog.json').read_text(encoding='utf8'))
def ids(values):return ', '.join('['+v+'](catalog.html#'+v+')' for v in values) or 'Unmapped'
source=['# Sources and retained corrections','','This is the supplied research register, preserved separately from the newer source-review layer. A citation is not runtime verification. [Review observations](source-review.json) retain unresolved access and support limits.','']
review=json.loads((D/'source-review.json').read_text(encoding='utf8'))
source+=['## Current review differences','','These findings qualify the retained register below. Original input bytes and historical inspection statements remain unchanged.','']
for item in review['errata']:
    source+=['- **'+item['source_id']+'** ('+item['scope']+'): '+item['finding']]
source+=['','Remaining review: '+review['still_required']+'.','']
for s in c['sources']:
    source+=['## '+s['id'], '', '['+s['title']+']('+s['url']+')','',s['scope_and_limit'],'','Type: '+s['type']+'. Supplied access date: '+s.get('access_date','not supplied')+'.','']
    for item in review['errata']:
        if item['source_id']==s['id']:source+=['**Current review qualification:** '+item['finding'],'']
source+=['## The 22 supplied corrections','','These original corrections retain the source packet\'s stated inspection scope. Current review observations remain distinct.','']
for n,a in enumerate(c['source_audit'],1):
    source+=['### '+str(n)+'. '+a['claim_area'],'',a['correction'],'','Sources: '+', '.join(a['sources'])+'.','']
(D/'sources.md').write_text('\n'.join(source),encoding='utf8')
mapping=['# Research crosswalks','','Mappings are mechanism-level relations, not proof of equivalence or prevention. Unmapped labels remain explicit.','', '## Retained aliases','']
for a in c['aliases']:mapping+=['- **'+a['alias_id']+'**: '+a['alias_title']+'. Resolves to '+ids([a['canonical_id']])+'. '+a['reason']]
mapping+=['','## Source labels','']
for x in c['source_crosswalk']:mapping+=['### '+x['source']+': '+x['source_label'],'',ids(x['canonical_ids']),'',x.get('mapping_scope',''),'',x.get('note',''),'']
mapping+=['## Supplied labels','']
for x in c['supplied_label_crosswalk']:mapping+=['- **'+x['supplied_label']+'**: '+ids(x['canonical_ids'])+'. '+x.get('note','')]
(D/'crosswalks.md').write_text('\n'.join(mapping),encoding='utf8')
print(json.dumps({'sources':len(c['sources']),'corrections':len(c['source_audit']),'source_crosswalks':len(c['source_crosswalk']),'supplied_crosswalks':len(c['supplied_label_crosswalk']),'aliases':len(c['aliases'])}))
