import json
from importlib.resources import files
from .core import Denied

def data():return json.loads(files('camden_work').joinpath('data/catalog.json').read_text(encoding='utf8'))

def entry(identity):
    if not isinstance(identity,str) or len(identity)>40:raise Denied('INVALID_CATALOG_ID')
    c=data();resolved=next((a['canonical_id'] for a in c['aliases'] if a['alias_id']==identity),identity)
    row=next((e for e in c['entries'] if e['id']==resolved),None)
    if row is None:raise Denied('CATALOG_ID_NOT_FOUND')
    return {'requested_id':identity,'canonical_id':resolved,'entry':row,'research_not_runtime_proof':True}

def search(query='',family=None,basis=None,outcome=None,offset=0,limit=10):
    if not isinstance(query,str) or len(query)>200 or type(offset)!=int or offset<0 or type(limit)!=int or not 1<=limit<=25:raise Denied('QUERY_BOUNDS')
    if family is not None and (not isinstance(family,str) or len(family)>10):raise Denied('FAMILY_TYPE')
    if basis is not None and basis not in ('R','E','D'):raise Denied('BASIS_INVALID')
    catalog=data()
    if outcome is not None and (not isinstance(outcome,str) or outcome not in catalog['outcome_tags']):raise Denied('OUTCOME_INVALID')
    rows=[e for e in catalog['entries'] if query.casefold() in json.dumps(e,ensure_ascii=False).casefold() and (not family or e['family']==family) and (not basis or e['evidence_basis']==basis) and (not outcome or outcome in e['facets']['primary_outcome_tags'])]
    return {'total':len(rows),'offset':offset,'items':[{'id':e['id'],'title':e['title'],'family':e['family'],'evidence_basis':e['evidence_basis']} for e in rows[offset:offset+limit]],'next_offset':offset+limit if offset+limit<len(rows) else None}
