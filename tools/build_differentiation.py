from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
def build():
    catalog=R/'camden_work/data/catalog.json';data=json.loads((R/'tools/data/differentiation-v1.json').read_text());ids={e['id'] for e in json.loads(catalog.read_text())['entries']}
    if data['catalog_sha256']!=hashlib.sha256(catalog.read_bytes()).hexdigest():raise ValueError('CATALOG_CHANGED')
    mapped=[r['canonical_id'] for r in data['entries']]
    if len(mapped)!=len(set(mapped)) or not set(mapped)<=ids:raise ValueError('MAPPING_IDS')
    (R/'docs/differentiation.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf8',newline='\n')
    return {'mapped':len(mapped),'unknown':len(ids)-len(mapped)}
if __name__=='__main__':print(json.dumps(build()))
