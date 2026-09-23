"""Separate unchanged research from explicitly scoped runtime test coverage."""
from pathlib import Path
import argparse,ast,hashlib,json,re
R=Path(__file__).resolve().parents[1]
PROFILES={
'TX':('camden_work/core.py','Local effect observations and opaque-target simulation. No HTTP provider, callback transport or replica reader is included.'),
'ID':('camden_work/core.py','Stable local occurrence IDs and target uniqueness. No provider deduplication expiry contract is implemented.'),
'AT':('camden_work/core.py','Attached local SQLite transactions and local result inbox. No multi-provider atomic commit is claimed.'),
'CP':('camden_work/core.py','Versioned synthetic counter inverse. Other business inverses and remote cancellation require a target-specific adapter.'),
'CC':('camden_work/core.py','One admitted API owner with effect-time epoch checks. OS-level hostile callers and remote queues are outside this boundary.'),
'DS':('camden_work/core.py','SQLite journals, immutable exports and bounded database pages. No storage-loss prevention or automatic paired backup service.'),
'RP':('camden_work/core.py','Same-workspace restart and inert import. Unsupported schemas fail; arbitrary migrations and live-handle restoration are not implemented.'),
'LN':('camden_work/core.py','Work rows, dependencies, parent adoption and frozen results. No agent tree or hosted executor dispatch is present.'),
'AU':('camden_work/core.py','Trusted local operator grants, expiry, revocation and budgets. No external identity provider or remote approval service.'),
'BI':('camden_work/core.py','Exact local tenant, target, payload and occurrence checks. Entity-name resolution, physical units and external audiences need separate adapters.'),
'VR':('camden_work/core.py','Independent local target-row checks and current report scope. Arbitrary semantic truth is not decided by this verifier.'),
'MM':('docs/tools.md','No LLM memory or retrieval-planning engine is included. The retained journal is evidence, not behavioral authority.'),
'PL':('docs/tools.md','A fixed synthetic task is admitted by an operator. Model planning, factual reasoning and objective selection are not implemented.'),
'LV':('camden_work/core.py','Explicit bounded foreground servicing. No scheduler or future wake is armed by a wait row.'),
'TM':('camden_work/core.py','Persisted Unix deadlines depend on trusted wall time. Civil recurrence, distributed clock correction and DST scheduling are absent.'),
'EC':('camden_work/core.py','Bounded local work, grants, attempts, events, requests and exports. No account billing or GPU allocation controller.'),
'PX':('camden_work/mcp.py','Finite read-only stdio MCP subset. No A2A, streaming provider connector or hosted session authority.'),
'SE':('SECURITY.md','No network or shell effect tool; trusted local process boundary. Not an OS sandbox or general prompt-injection defense.'),
'SC':('pyproject.toml','Explicit package/build inputs and clean-install checks. Distribution provenance and CI require their own release evidence.'),
'PR':('SECURITY.md','Synthetic default data and explicit local export read grant. No multi-user confidentiality or retention policy engine.'),
'HT':('docs/quickstart.md','Operator-facing CLI and cumulative local report. No authenticated natural-language remote consent workflow.'),
'OB':('camden_work/core.py','Retained events and explicit result limits. No remote monitoring service or inference of root cause from a heartbeat.'),
'EN':('docs/limits.md','Python, SQLite and local filesystem assumptions. Tested platforms must be identified separately from source-level portability.'),
'EV':('docs/limits.md','Named local tests and synthetic adverse histories. No exhaustive model checker or universal correctness claim.'),
'PH':('docs/limits.md','No physical actuator, sensor or coupled control system exists in this package.')}
M={
'AF-TX-01':('test_core.CoreTests.test_real_lost_ack_and_replacement','One local committed effect survives an actual lost-ack process exit and replacement.'),
'AF-TX-02':('test_continuity.ContinuityTests.test_admission_is_not_execution','Admission has no target effect or completion verdict.'),
'AF-TX-03':('test_local_recovery.LocalRecovery.test_opaque_cancel_preserves_unknown','Opaque simulated dispatch remains unknown after cancellation; no real provider cancellation tested.'),
'AF-TX-04':('test_local_recovery.LocalRecovery.test_absence_without_old_epoch_fence_cannot_enable_retry','Local recovery cannot use absence while the dispatch epoch is still current.'),
'AF-ID-02':('test_core.CoreTests.test_distinct_identical_requests','Identical authorized payloads retain distinct occurrence identities.'),
'AF-CP-03':('test_continuity.ContinuityTests.test_conditional_compensation_preserves_intervening_change','Versioned inverse cannot overwrite an intervening local counter effect.'),
'AF-AU-02':('test_core.CoreTests.test_revocation','Current revoked grant blocks the future local effect.'),
'AF-AU-08':('test_core.CoreTests.test_aggregate_reservation','Admission reserves the grant effect budget.'),
'AF-AU-12':('test_continuity.ContinuityTests.test_revocation_does_not_block_other_grant','Revoking one grant does not block unrelated granted local work.'),
'AF-VR-05':('test_effect_preconditions.EffectPreconditions.test_export_cannot_call_stale_cached_verification_complete','Export rechecks target visibility instead of relying on cached verification.'),
'AF-VR-14':('test_finalization.Finalization.test_new_obligation_invalidates_frozen_result','A later admitted obligation invalidates a previous frozen result scope.'),
'AF-LN-04':('test_finalization.Finalization.test_export_alone_cannot_finalize','Local finalization requires parent adoption, separately from export.'),
'AF-PX-01':('test_mcp.MCPTests.test_no_preinit_tool','Read-only MCP tools reject use before initialization.'),
'AF-PX-04':('test_mcp.MCPTests.test_unknown_argument','Unknown tool arguments are rejected before execution.'),
'AF-PX-05':('test_mcp.MCPTests.test_actual_stdio_exchange_and_reconnect','A real stdio subprocess emits parseable protocol responses through two process lifetimes.'),
'AF-EC-05':('test_mcp.MCPTests.test_bad_json_and_oversize','MCP request lines have a bounded size; this is not an LLM context guarantee.'),
'AF-DS-03':('test_continuity.ContinuityTests.test_import_cannot_restore_revoked_grant_or_replay','Inert snapshot import restores no runnable grants or effects.'),
'AF-HT-06':('test_report.Reports.test_report_preserves_completed_and_pending_work','A cumulative report retains both completed and pending local work.')}

def build(run_receipt=None,history=None):
    run=None
    if run_receipt:
        run=json.loads(Path(run_receipt).read_text(encoding='utf8'))
        if run['exit_code']!=0:raise ValueError('Passing run required')
        exercised={k.replace('\\','/'):v for k,v in run['sources'].items()}
        for directory in ('camden_work','tests'):
            for p in (R/directory).glob('*.py'):
                if exercised.get(p.relative_to(R).as_posix())!=hashlib.sha256(p.read_bytes()).hexdigest():raise ValueError('Changed exercised source: '+p.name)
        passed={cls if cls.endswith('.'+method) else cls+'.'+method for method,cls in re.findall(r'^(test_\w+) \(([^)]+)\) \.\.\. ok\r?$',run['stderr'],re.M)}
        # Reject incomplete observations before replacing public evidence.
        missing={test for test,scope in M.values()}-passed
        if missing:raise ValueError('Required tests absent from receipt: '+', '.join(sorted(missing)))
        # Private receipt paths, host directories and task identity are omitted.
        public_run={'schema':'camden.local_test_run.v1','at':run['at'],'runtime':run['runtime'],'exit_code':0,'passed_tests':sorted(passed),'source_sha256':{k:v for k,v in exercised.items() if k.startswith(('camden_work/','tests/'))},'scope':'Windows source-tree unittest run; no provider, hosted security or public-download qualification'}
        if history:
            trials=[]
            for path in sorted(Path(history).glob('*/result.json')):
                prior=json.loads(path.read_text(encoding='utf8'));output=prior.get('stderr','')
                count=re.search(r'Ran (\d+) tests? in ([\d.]+)s',output)
                trials.append({'at':prior.get('at'), 'exit_code':prior.get('exit_code'),'test_count':int(count[1]) if count else None,'elapsed_seconds':float(count[2]) if count else None,'failures':[{'kind':kind,'test':identity} for kind,identity in re.findall(r'^(FAIL|ERROR): (.+)\r?$',output,re.M)],'interpretation':'Historical observation; failure may be implementation or fixture. No retrospective cause inferred.'})
            public_run['trial_history']=trials
        (R/'docs/evaluation.json').write_text(json.dumps(public_run,indent=2)+'\n',encoding='utf8')
    tests={}
    for path in (R/'tests').glob('test_*.py'):
        tree=ast.parse(path.read_text(encoding='utf8'))
        for cls in [x for x in tree.body if isinstance(x,ast.ClassDef)]:
            for fn in [x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name.startswith('test_')]:
                tests[path.stem+'.'+cls.name+'.'+fn.name]={'path':path.relative_to(R).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    catalog=json.loads((R/'camden_work/data/catalog.json').read_text(encoding='utf8'))
    rows=[]
    for entry in catalog['entries']:
        component,scope=PROFILES[entry['family']]
        record={'id':entry['id'],'research_basis':entry['evidence_basis'],'effect_outcomes':entry['facets']['primary_outcome_tags'],'mechanism_title':entry['title'],'applicability':'DESIGN_CONSTRAINT_OR_ADAPTER_EXTENSION','component_or_contract':component,'scope_reason':scope,'required_boundary_capability':entry['mitigation'],'verification':'DOCUMENTED_BOUNDARY_ANALYSIS_NOT_RUNTIME_TEST','result':'UNKNOWN','tests':[],'analysis':{'invariant_reviewed':entry['invariant'],'boundary_statement':scope},'residual_limit':entry['residual_limit'],'release_claim':'No prevention claim for this complete mechanism'}
        if entry['family']=='PH':
            record.update(applicability='OUTSIDE_IMPLEMENTED_TARGET',result='NOT_APPLICABLE',scope_reason=scope)
        if entry['id'] in M:
            test,scope=M[entry['id']]
            if test not in tests:raise ValueError('Missing exact test: '+test)
            record.update(applicability='LOCAL_SUBCASE_ONLY',verification='TEST_DEFINED_REQUIRES_MATCHING_RUN_RECEIPT',tests=[{'test':test,**tests[test]}],scope_reason=scope,release_claim='Only the stated local subcase, conditional on a passing exact-version run')
            if run:
                if test not in passed:raise ValueError('Test not passed in receipt: '+test)
                record.update(verification='MATCHING_SOURCE_TEST_RUN',result='PASS_LOCAL_SUBCASE_ONLY',execution_evidence='evaluation.json',release_claim=scope+' No claim about the full research mechanism.')
        rows.append(record)
    output={'schema':'camden.research_runtime_coverage.v1','package_version':'0.1.0','research_changed':False,'all_mechanisms_prevented':False,'rows':rows,'mechanisms_without_runtime_test':sum(not r['tests'] for r in rows),'analysis_limit':'Boundary analysis is not a full source audit or a claim that every required release capability is finished.'}
    (R/'docs/coverage.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'rows':len(rows),'mapped_local_subcases':len(M),'mechanisms_without_runtime_test':output['mechanisms_without_runtime_test'],'local_subcases_bound_to_run':bool(run),'full_mechanism_pass_claimed':False}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-receipt');parser.add_argument('--history');args=parser.parse_args();build(args.run_receipt,args.history)
