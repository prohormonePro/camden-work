"""Run real sequential subprocess crashes against an isolated local target."""
import json,sqlite3,subprocess,sys,time
from pathlib import Path
from .core import Node,Denied

def run(directory):
    began=time.time();n=Node.initialize(directory);g=n.grant(tenant='demo',target='counter')
    w=n.admit(grant=g,tenant='demo',target='counter',delta=1)
    n.claim('first',expected_epoch=0)
    command=[sys.executable,'-B','-m','camden_work','--workspace',str(n.root),'execute','--work',w,'--worker','first','--epoch','1','--crash','after-target']
    child=subprocess.run(command,capture_output=True,timeout=30)
    if child.returncode!=72:raise AssertionError(('CRASH_NOT_REACHED',child.returncode,child.stderr))
    n.stop(expected_epoch=1);epoch=n.claim('replacement',expected_epoch=1)
    reconciled=n.reconcile(w,worker='replacement',epoch=epoch)
    if reconciled['work']['state']!='VERIFIED':raise AssertionError('NO_RECONCILIATION')
    g2=n.grant(tenant='demo',target='uncertain');u=n.admit(grant=g2,tenant='demo',target='uncertain',delta=2)
    child2=subprocess.run([sys.executable,'-B','-m','camden_work','--workspace',str(n.root),'execute','--work',u,'--worker','replacement','--epoch',str(epoch),'--crash','after-target'],capture_output=True,timeout=30)
    if child2.returncode!=72:raise AssertionError('SECOND_CRASH_NOT_REACHED')
    n.stop(expected_epoch=epoch);epoch=n.claim('final',expected_epoch=epoch)
    n.visibility(False,tenant='demo',target='uncertain')
    uncertain=n.reconcile(u,worker='final',epoch=epoch)
    try:n.execute(u,worker='final',epoch=epoch)
    except Denied as exc:retry_rejected=str(exc)
    else:raise AssertionError('UNKNOWN_RETRY_ALLOWED')
    g3=n.grant(tenant='demo',target='independent');v=n.admit(grant=g3,tenant='demo',target='independent',delta=3)
    independent=n.execute(v,worker='final',epoch=epoch)
    n.wait(u);n.visibility(True,tenant='demo',target='uncertain')
    serviced=n.service(worker='final',epoch=epoch)
    # Intentionally unsafe baseline: a lost reply triggers a new identity twice.
    baseline=sqlite3.connect(n.root/'unsafe-baseline.sqlite3')
    baseline.execute('CREATE TABLE effects(id INTEGER PRIMARY KEY,amount INTEGER)')
    for _ in range(2):baseline.execute('INSERT INTO effects(amount) VALUES(1)');baseline.commit()
    duplicate_count=baseline.execute('SELECT count(*) FROM effects').fetchone()[0];baseline.close()
    target=sqlite3.connect(n.root/'target.sqlite3')
    count=target.execute('SELECT count(*) FROM effects WHERE id=?',(w,)).fetchone()[0];target.close()
    checks={'crash_after_target_commit':child.returncode==72,'one_original_effect':count==1,'unknown_observed':uncertain['work']['state']=='UNKNOWN','retry_fenced':retry_rejected=='RECONCILE_BEFORE_RETRY','independent_task_verified':independent['work']['state']=='VERIFIED','registered_wait_serviced':serviced[0]['work']['state']=='VERIFIED','unsafe_baseline_duplicates':duplicate_count==2}
    if not all(checks.values()):raise AssertionError(checks)
    report=n.export('challenge-result')
    result={'checks':checks,'elapsed_seconds':time.time()-began,'crash_exit_codes':[child.returncode,child2.returncode],'baseline':'Deliberately naive new-identity retry, not an industry benchmark','implementation_profile':'Trusted local SQLite synthetic target','target_effect_count':len(n.status()['target_effects']),'report':report}
    (n.root/'challenge-evidence.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    return result
