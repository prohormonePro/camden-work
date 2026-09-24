"""Dependency-free claim/reference checks; not semantic certification."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[1]
def validate(data,root=R):
    schema=json.loads((root/'docs/claims.schema.json').read_text(encoding='utf8'));item=schema['properties']['claims']['items'];errors=[];ids=set()
    if set(data)!={'schema_version','claims'} or data.get('schema_version')!=1 or not isinstance(data.get('claims'),list):return ['REGISTER_SCHEMA']
    for row in data['claims']:
        cid=row.get('claim_id','MISSING');prefix=cid+': '
        if set(row)!=set(item['required']):errors.append(prefix+'FIELDS')
        if cid in ids:errors.append(prefix+'DUPLICATE_ID')
        ids.add(cid);status=row.get('evidence_status')
        if status not in item['properties']['evidence_status']['enum']:errors.append(prefix+'STATUS')
        for field in ['public_wording','package_version','trust_model','target_boundary','observed_result','falsification_scenario','last_reviewed_at']:
            if not isinstance(row.get(field),str) or not row[field].strip():errors.append(prefix+field)
        for field in ['source_paths','named_tests','evidence_artifact_refs','unsupported_extensions']:
            if not isinstance(row.get(field),list) or not all(isinstance(x,str) and x for x in row[field]):errors.append(prefix+field)
        if status in ['PUBLIC_SOURCE_AND_TEST_MAPPED','PUBLIC_RUN_OBSERVED','MAINTAINER_REPORTED'] and (not row.get('source_paths') or not row.get('named_tests')):errors.append(prefix+'EVIDENCE_REQUIRED')
        if status in ['PUBLIC_RUN_OBSERVED','MAINTAINER_REPORTED'] and (not row.get('run_id') or not row.get('evidence_artifact_refs')):errors.append(prefix+'RUN_REQUIRED')
        for ref in row.get('source_paths',[])+row.get('evidence_artifact_refs',[])+row.get('named_tests',[]):
            path,_,test=ref.partition('::');p=(root/path).resolve()
            if root.resolve() not in p.parents or not p.is_file():errors.append(prefix+'MISSING_OR_ESCAPING '+ref);continue
            if test and test not in {n.name for n in ast.walk(ast.parse(p.read_text(encoding='utf8'))) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}:errors.append(prefix+'TEST_NOT_FOUND '+ref)
        for path,expected in row.get('source_sha256',{}).items():
            p=(root/path).resolve()
            if root.resolve() not in p.parents or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append(prefix+'SOURCE_CHANGED '+path)
    return errors
if __name__=='__main__':
    errors=validate(json.loads((R/'docs/claims.json').read_text(encoding='utf8')))
    print(json.dumps({'errors':errors,'scope':'Reference integrity, not truth certification'}));raise SystemExit(bool(errors))
