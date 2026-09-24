"""Cold-process experiment v1. Harness launches are counted as assistance.

Run from reviewed source: python -B -m benchmarks.continuity NEW_DIRECTORY
No network, credentials, background supervisor, or remote effects.
"""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,time
from camden_work.core import Node,Denied

def save(path,value):
    with path.open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2);stream.write('\n')

def controller(root,phase):
    # Only durable workspace and declared fault phase arrive from the harness.
    # No work ID, epoch, grant, or in-memory continuation is handed over.
    n=Node(root);policy=json.loads((root/'policy.json').read_text())
    if policy!={'schema':1,'allow_serial_takeover':True,'result':'complete-result'}:
        raise ValueError('UNREVIEWED_POLICY')
    prior=n.status()['owner']
    n.stop(expected_epoch=prior['epoch'])
    worker='controller-'+str(prior['epoch']+1);epoch=n.claim(worker,expected_epoch=prior['epoch'])
    if phase!='initial':
        for w in n.status()['works']:
            if w['state'] in ('DISPATCHED','UNKNOWN'):
                n.reconcile(w['id'],worker=worker,epoch=epoch)
        if phase=='recovery-crash':os._exit(73)
    for w in sorted(n.status()['works'],key=lambda w:w['target']):
        if w['state']=='ADMITTED':
            n.execute(w['id'],worker=worker,epoch=epoch,
                      crash='after-target' if phase=='initial' else None)
    if any(w['state']!='VERIFIED' for w in n.status()['works']):
        raise RuntimeError('WORK_INCOMPLETE_NO_SUCCESS_RETURN')
    n.export(policy['result']);n.adopt_result(policy['result'],worker=worker,epoch=epoch)
    n.deliver_local(policy['result'],worker=worker,epoch=epoch)
    result=n.finalize(policy['result'],worker=worker,epoch=epoch)
    # No host path in published evidence.
    save(root/'closure.json',result)

def episode(root,scenario):
    root.mkdir();n=Node.initialize(root/'workspace');workspace=n.root
    save(workspace/'policy.json',{'schema':1,'allow_serial_takeover':True,'result':'complete-result'})
    for target in ('original','z-independent'):
        grant=n.grant(tenant='synthetic',target=target,max_effects=1)
        n.admit(grant=grant,tenant='synthetic',target=target,delta=1,budget=3,deadline_seconds=300)
    before=n.status();save(root/'before.json',before)
    result={'schema':1,'scenario_version':'cold-process-v1','episode_id':root.name,'scenario':scenario,
            'status':'STARTED','B_e':0,'D_e':0,'S_e':{'fixture_setup':'two grants, two obligations, takeover policy','human_minutes':'NOT_MEASURED'},
            'A_e':0,'U_e':['automatic_restart','background_wake','remote_effects','new_business_decision'],
            'events':[],'process_exits':[],'started_at':time.time()}
    save(root/'started.json',result)
    phases=['initial','recovery-crash','finish'] if scenario=='recovery-of-recovery' else ['initial','finish']
    start=time.monotonic()
    try:
        for index,phase in enumerate(phases):
            result['A_e']+=1
            result['events'].append({'event_id':str(index),'episode_id':root.name,'obligation':'workspace/works',
                'actor':'benchmark_harness','event_type':'launch_clean_controller','authority_basis':'predeclared serial takeover policy',
                'before_reference':'before.json' if index==0 else 'durable workspace','after_reference':'after.json',
                'evidence_pointer':'process_exits','order':index,'burden_class':'A_e','disposition':phase})
            proc=subprocess.run([sys.executable,'-B','-m','benchmarks.continuity',str(workspace),'--controller',phase],
                                capture_output=True,text=True,timeout=15)
            result['process_exits'].append(proc.returncode)
            if proc.returncode!=({'initial':72,'recovery-crash':73,'finish':0}[phase]):
                raise RuntimeError('UNEXPECTED_CONTROLLER_EXIT: '+proc.stderr[-1000:])
        after=n.status();save(root/'after.json',after)
        originals={w['id']:w for w in before['works']};effects=after['target_effects']
        old=before['owner'];stale_denied=False
        try:n.execute(next(iter(originals)),worker='controller-1',epoch=1)
        except Denied as exc:stale_denied=str(exc)=='WORKER_FENCED'
        checks={'same_obligations':set(originals)=={w['id'] for w in after['works']},
                'exactly_one_effect_per_obligation':len(effects)==2 and {e['id'] for e in effects}==set(originals),
                'independent_verified':all(w['state']=='VERIFIED' for w in after['works']),
                'budget_deadline_preserved':all((w['budget'],w['deadline'])==(originals[w['id']]['budget'],originals[w['id']]['deadline']) for w in after['works']),
                'attempts_not_reset':all(w['attempts']==1 for w in after['works']),
                'stale_owner_denied':stale_denied,
                'local_return_complete':json.loads((workspace/'closure.json').read_text())['ready'],
                'delivered_bytes_match':(workspace/'exports/complete-result.md').read_bytes()==(workspace/'inbox/complete-result.md').read_bytes()}
        result['checks']=checks;result['status']='BUSINESS_COMPLETE' if all(checks.values()) else 'FAILED'
        result['closure']=json.loads((workspace/'closure.json').read_text())
    except Exception as exc:
        result['status']='FAILED';result['error']=type(exc).__name__+': '+str(exc)
    result['elapsed_seconds']=time.monotonic()-start
    save(root/'result.json',result);return result

def run(directory,repetitions=2):
    root=Path(directory).resolve();root.mkdir(exist_ok=False)
    sources=['camden_work/core.py','benchmarks/continuity.py']
    manifest={'schema':1,'scenario_version':'cold-process-v1','runtime':{'python':platform.python_version(),'os':platform.system()},
              'seed':'deterministic fault schedule; UUID identities vary','repetitions':repetitions,
              'storage':'SQLite DELETE journal, synchronous FULL, trusted local filesystem',
              'deadline_seconds':300,'per_process_timeout_seconds':15,
              'system_under_test':'unchanged 0.1.0 core plus separately identified benchmark controller; harness restart assistance counted',
              'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources},'episodes':[]}
    save(root/'plan.json',manifest)
    for scenario in ['cold-controller','recovery-of-recovery']:
        for i in range(repetitions):
            result=episode(root/(scenario+'-'+str(i+1)),scenario);manifest['episodes'].append(result)
            # Durable cumulative record after every episode, including failures.
            temporary=root/'manifest.pending';temporary.write_text(json.dumps(manifest,indent=2)+'\n');temporary.replace(root/'manifest.json')
    manifest['started_episodes']=len(manifest['episodes']);manifest['completed_episodes']=sum(e['status']=='BUSINESS_COMPLETE' for e in manifest['episodes'])
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory');parser.add_argument('--controller',choices=['initial','recovery-crash','finish']);args=parser.parse_args()
    if args.controller:controller(Path(args.directory),args.controller)
    else:
        result=run(args.directory);print(json.dumps({'started':result['started_episodes'],'complete':result['completed_episodes']}))
        raise SystemExit(result['started_episodes']!=result['completed_episodes'])
