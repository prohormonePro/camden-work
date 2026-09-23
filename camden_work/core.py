"""Durable local controller for a bounded synthetic counter target.

Trust boundary: the operator controls this program and its workspace. Workers
use the controller API. An OS principal able to rewrite the database or code
can bypass these checks. This is not a hostile-worker sandbox or remote API.
"""
from __future__ import annotations
import contextlib, hashlib, json, os, sqlite3, time, uuid
from pathlib import Path

SCHEMA = 1
MAX_TEXT = 8192
MAX_GRANTS = 128
MAX_WORKS = 512
MAX_EVENTS = 10000
MAX_EXPORTS = 64
MAX_DATABASE_BYTES = 16*1024*1024

class Denied(RuntimeError):
    pass

def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)

def digest(value):
    return hashlib.sha256(encoded(value).encode('utf8')).hexdigest()

def identifier(value):
    if not isinstance(value, str) or not value or len(value)>120 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.' for c in value):
        raise Denied('INVALID_IDENTIFIER')
    return value

class Node:
    def __init__(self, directory):
        self.root = Path(directory).resolve()
        self.path = self.root/'controller.sqlite3'
        if not self.path.is_file():
            raise Denied('INITIALIZE_REQUIRED')

    @classmethod
    def initialize(cls, directory):
        root = Path(directory).resolve()
        root.mkdir(parents=True, exist_ok=True)
        path = root/'controller.sqlite3'
        target_path=root/'target.sqlite3'
        if os.path.lexists(target_path):raise FileExistsError('Existing target must not be adopted by initialization')
        # Refuse reuse instead of replacing a live ledger.
        fd = os.open(path, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
        os.close(fd)
        # Reserve both files exclusively. A partial initialization remains
        # fail-closed; never adopt or overwrite a pre-existing target.
        fd=os.open(target_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        os.close(fd)
        db = sqlite3.connect(path)
        try:
            db.executescript('''
            PRAGMA journal_mode=DELETE;
            PRAGMA synchronous=FULL;
            CREATE TABLE config(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE grants(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, target TEXT NOT NULL,
              max_delta INTEGER NOT NULL, max_effects INTEGER NOT NULL, expires REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE owner(singleton INTEGER PRIMARY KEY CHECK(singleton=1),epoch INTEGER NOT NULL,worker TEXT, stopped INTEGER NOT NULL);
            CREATE TABLE works(id TEXT PRIMARY KEY,grant_id TEXT NOT NULL,tenant TEXT NOT NULL,target TEXT NOT NULL,
              payload TEXT NOT NULL,payload_hash TEXT NOT NULL,state TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,
              budget INTEGER NOT NULL,deadline REAL NOT NULL,profile TEXT NOT NULL);
            CREATE TABLE dependencies(work TEXT NOT NULL,dependency TEXT NOT NULL,PRIMARY KEY(work,dependency));
            CREATE TABLE attempts(id TEXT PRIMARY KEY,work TEXT NOT NULL,epoch INTEGER NOT NULL,phase TEXT NOT NULL,at REAL NOT NULL);
            CREATE TABLE observations(id INTEGER PRIMARY KEY AUTOINCREMENT,work TEXT NOT NULL,kind TEXT NOT NULL,evidence TEXT NOT NULL,at REAL NOT NULL);
            CREATE TABLE waits(work TEXT PRIMARY KEY,due REAL NOT NULL,deadline REAL NOT NULL,remaining INTEGER NOT NULL,last_serviced REAL,status TEXT NOT NULL);
            CREATE TABLE events(id INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT NOT NULL,body TEXT NOT NULL,at REAL NOT NULL);
            INSERT INTO owner VALUES(1,0,NULL,1);
            ''')
            db.execute('INSERT INTO config VALUES(?,?)',('schema',str(SCHEMA)))
            db.execute('INSERT INTO config VALUES(?,?)',('node',uuid.uuid4().hex))
            db.commit()
        finally:
            db.close()
        target=sqlite3.connect(target_path)
        try:
            target.executescript('''PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL;
            CREATE TABLE effects(id TEXT PRIMARY KEY,tenant TEXT NOT NULL,target TEXT NOT NULL,payload_hash TEXT NOT NULL,delta INTEGER NOT NULL,epoch INTEGER NOT NULL,at REAL NOT NULL);
            CREATE TABLE counters(tenant TEXT NOT NULL,target TEXT NOT NULL,value INTEGER NOT NULL,version INTEGER NOT NULL,PRIMARY KEY(tenant,target));
            CREATE TABLE visibility(tenant TEXT NOT NULL,target TEXT NOT NULL,available INTEGER NOT NULL,PRIMARY KEY(tenant,target));''')
            target.commit()
        finally:
            target.close()
        return cls(root)

    @contextlib.contextmanager
    def transaction(self):
        db=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        db.row_factory=sqlite3.Row
        try:
            db.execute('PRAGMA synchronous=FULL')
            if db.execute("SELECT value FROM config WHERE key='schema'").fetchone()[0]!=str(SCHEMA):
                raise Denied('UNSUPPORTED_SCHEMA')
            db.execute('ATTACH DATABASE ? AS targetdb',(str(self.root/'target.sqlite3'),))
            db.execute('PRAGMA targetdb.synchronous=FULL')
            for schema in ('main','targetdb'):
                page_size=db.execute('PRAGMA '+schema+'.page_size').fetchone()[0]
                db.execute('PRAGMA '+schema+'.max_page_count='+str(MAX_DATABASE_BYTES//page_size))
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def event(self,db,kind,body):
        count=db.execute('SELECT count(*) FROM events').fetchone()[0]
        reserved=kind in ('operator_stop','operator_revoke','operator_cancel','result_reservation','result_frozen','parent_adoption','local_delivery','local_ready')
        ceiling=MAX_EVENTS+(MAX_GRANTS+MAX_WORKS+MAX_EXPORTS*5+1 if reserved else 0)
        if count>=ceiling:raise Denied('EVENT_BUDGET')
        db.execute('INSERT INTO events(kind,body,at) VALUES(?,?,?)',(kind,encoded(body),time.time()))

    def grant(self,*,tenant,target,max_delta=10,max_effects=10,lifetime=3600):
        identifier(tenant);identifier(target)
        if type(max_delta)!=int or type(max_effects)!=int or not 0<max_delta<=10000 or not 0<max_effects<=10000 or not 0<lifetime<=86400*7:
            raise Denied('INVALID_LIMITS')
        gid=uuid.uuid4().hex
        with self.transaction() as db:
            if db.execute('SELECT count(*) FROM grants').fetchone()[0]>=MAX_GRANTS:raise Denied('NODE_GRANT_LIMIT')
            db.execute('INSERT INTO grants VALUES(?,?,?,?,?,?,0)',(gid,tenant,target,max_delta,max_effects,time.time()+lifetime))
            self.event(db,'operator_grant',{'grant':gid,'tenant':tenant,'target':target,'max_effects':max_effects})
        return gid

    def revoke(self,grant):
        with self.transaction() as db:
            previous=db.execute('SELECT revoked FROM grants WHERE id=?',(grant,)).fetchone()
            if previous and previous[0]:return
            if db.execute('UPDATE grants SET revoked=1 WHERE id=?',(grant,)).rowcount!=1:raise Denied('UNKNOWN_GRANT')
            self.event(db,'operator_revoke',{'grant':grant})

    def claim(self,worker,*,expected_epoch):
        identifier(worker)
        if type(expected_epoch)!=int or expected_epoch<0:raise Denied('OWNER_VERSION_TYPE')
        with self.transaction() as db:
            old=db.execute('SELECT * FROM owner').fetchone()
            if old['epoch']!=expected_epoch:raise Denied('OWNER_VERSION_CONFLICT')
            if not old['stopped']:raise Denied('EXPLICIT_STOP_REQUIRED')
            epoch=old['epoch']+1
            db.execute('UPDATE owner SET epoch=?,worker=?,stopped=0',(epoch,worker))
            self.event(db,'claim',{'worker':worker,'epoch':epoch})
        return epoch

    def stop(self,*,expected_epoch):
        if type(expected_epoch)!=int or expected_epoch<0:raise Denied('OWNER_VERSION_TYPE')
        with self.transaction() as db:
            old=db.execute('SELECT * FROM owner').fetchone()
            if old['epoch']!=expected_epoch:raise Denied('OWNER_VERSION_CONFLICT')
            if old['stopped']:return
            if db.execute('UPDATE owner SET stopped=1 WHERE epoch=?',(expected_epoch,)).rowcount!=1:raise Denied('OWNER_VERSION_CONFLICT')
            self.event(db,'operator_stop',{'epoch':expected_epoch})

    def check_owner(self,db,worker,epoch):
        if type(epoch)!=int or epoch<0:raise Denied('OWNER_VERSION_TYPE')
        row=db.execute('SELECT * FROM owner').fetchone()
        if row['stopped'] or row['epoch']!=epoch or row['worker']!=worker:raise Denied('WORKER_FENCED')

    def valid_grant(self,db,gid,tenant,target):
        grant=db.execute('SELECT * FROM grants WHERE id=?',(gid,)).fetchone()
        if not grant or grant['revoked'] or grant['expires']<=time.time():raise Denied('GRANT_INACTIVE')
        if (grant['tenant'],grant['target'])!=(tenant,target):raise Denied('GRANT_SCOPE_MISMATCH')
        return grant

    def admit(self,*,grant,tenant,target,delta,budget=3,deadline_seconds=3600,dependencies=(),profile='local-atomic',expected_version=None,compensates=None,_host_origin=None):
        identifier(tenant);identifier(target)
        if type(delta)!=int or type(budget)!=int or not 0<budget<=20 or not 0<deadline_seconds<=86400 or profile not in ('local-atomic','opaque'):
            raise Denied('INVALID_TASK')
        if expected_version is not None and (type(expected_version)!=int or expected_version<0):raise Denied('INVALID_EXPECTED_VERSION')
        work=uuid.uuid4().hex;payload={'operation':'increment','delta':delta}
        if expected_version is not None:payload['expected_version']=expected_version
        if compensates:payload['compensates']=identifier(compensates)
        deps=list(dependencies)
        origin=None;input_binding=None
        if _host_origin is not None:
            if type(_host_origin)!=dict or set(_host_origin)!={'principal','channel','event_id','kind'} or _host_origin['kind'] not in ('user_input','host_machine_input'):raise Denied('HOST_INPUT_ORIGIN')
            origin=dict(_host_origin)
            for key in ('principal','channel','event_id'):identifier(origin[key])
            input_binding=digest({'origin':origin,'grant':grant,'tenant':tenant,'target':target,'payload':payload,'budget':budget,'deadline_seconds':deadline_seconds,'dependencies':deps,'profile':profile})
        with self.transaction() as db:
            g=self.valid_grant(db,grant,tenant,target)
            if origin is not None:
                for event in db.execute("SELECT body FROM events WHERE kind='host_input'"):
                    prior=json.loads(event[0]);old=prior['origin']
                    if all(old[k]==origin[k] for k in ('principal','channel','event_id')):
                        if prior['binding']!=input_binding:raise Denied('HOST_INPUT_CONFLICT')
                        return prior['work']
            if db.execute('SELECT count(*) FROM works').fetchone()[0]>=MAX_WORKS:raise Denied('NODE_WORK_LIMIT')
            if abs(delta)>g['max_delta'] or delta==0:raise Denied('DELTA_LIMIT')
            if compensates:
                original=db.execute('SELECT * FROM targetdb.effects WHERE id=?',(compensates,)).fetchone()
                if not original or (original['tenant'],original['target'],original['delta'])!=(tenant,target,-delta) or expected_version is None:raise Denied('COMPENSATION_NOT_BOUND')
                if any(json.loads(r[0]).get('compensates')==compensates for r in db.execute('SELECT payload FROM works')):raise Denied('COMPENSATION_ALREADY_RESERVED')
            # Admission reserves the aggregate effect budget, including unknown effects.
            if db.execute('SELECT count(*) FROM works WHERE grant_id=?',(grant,)).fetchone()[0]>=g['max_effects']:raise Denied('GRANT_BUDGET')
            if len(deps)>100 or len(set(deps))!=len(deps):raise Denied('INVALID_DEPENDENCIES')
            for dep in deps:
                row=db.execute('SELECT tenant FROM works WHERE id=?',(dep,)).fetchone()
                if not row or row['tenant']!=tenant:raise Denied('DEPENDENCY_SCOPE')
            db.execute('INSERT INTO works VALUES(?,?,?,?,?,?,?,0,?,?,?)',(work,grant,tenant,target,encoded(payload),digest(payload),'ADMITTED',budget,time.time()+deadline_seconds,profile))
            db.executemany('INSERT INTO dependencies VALUES(?,?)',[(work,d) for d in deps])
            self.event(db,'admitted',{'work':work,'payload_hash':digest(payload),'grant':grant,'profile':profile})
            if origin is not None:self.event(db,'host_input',{'origin':origin,'binding':input_binding,'work':work,'scope':'Trusted local host assertion, not remote-provider authentication'})
        return work

    def work(self,db,wid):
        row=db.execute('SELECT * FROM works WHERE id=?',(wid,)).fetchone()
        if not row:raise Denied('UNKNOWN_WORK')
        return row

    def target_evidence_valid(self,db,w):
        visible=db.execute('SELECT available FROM targetdb.visibility WHERE tenant=? AND target=?',(w['tenant'],w['target'])).fetchone()
        effect=db.execute('SELECT * FROM targetdb.effects WHERE id=?',(w['id'],)).fetchone()
        return bool((not visible or visible[0]) and effect and w['profile']=='local-atomic' and (effect['tenant'],effect['target'],effect['payload_hash'],effect['delta'])==(w['tenant'],w['target'],w['payload_hash'],json.loads(w['payload'])['delta']))

    def check_dependencies(self,db,wid):
        for dep in db.execute('SELECT dependency FROM dependencies WHERE work=?',(wid,)):
            w=self.work(db,dep[0])
            if w['state']!='VERIFIED':raise Denied('DEPENDENCY_UNVERIFIED')
            if not self.target_evidence_valid(db,w):raise Denied('DEPENDENCY_EVIDENCE_UNAVAILABLE')

    def execute(self,wid,*,worker,epoch,crash=None):
        # Crash hooks are local synthetic test modes, not arbitrary callbacks.
        if crash not in (None,'after-intent','after-target'):raise Denied('UNKNOWN_CRASH_POINT')
        with self.transaction() as db:
            self.check_owner(db,worker,epoch);w=self.work(db,wid)
            self.valid_grant(db,w['grant_id'],w['tenant'],w['target'])
            if w['state']=='VERIFIED':return self._status(db,wid)
            if w['state']!='ADMITTED':raise Denied('RECONCILE_BEFORE_RETRY')
            if w['deadline']<=time.time() or w['attempts']>=w['budget']:raise Denied('WORK_BUDGET_OR_DEADLINE')
            self.check_dependencies(db,wid)
            if db.execute("SELECT count(*) FROM works WHERE tenant=? AND target=? AND id!=? AND state IN ('DISPATCHED','UNKNOWN')",(w['tenant'],w['target'],wid)).fetchone()[0]:raise Denied('CONFLICTING_UNKNOWN_EFFECT')
            attempt=uuid.uuid4().hex
            db.execute("UPDATE works SET state='DISPATCHED',attempts=attempts+1 WHERE id=?",(wid,))
            db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)',(attempt,wid,epoch,'INTENT_DURABLE',time.time()))
            self.event(db,'dispatch_intent',{'work':wid,'attempt':attempt,'epoch':epoch})
        if crash=='after-intent':os._exit(71)
        with self.transaction() as db:
            # Effect-time owner and revocation checks share the local target transaction.
            self.check_owner(db,worker,epoch);w=self.work(db,wid)
            if w['state']!='DISPATCHED':raise Denied('ATTEMPT_NO_LONGER_DISPATCHED')
            self.valid_grant(db,w['grant_id'],w['tenant'],w['target'])
            if w['deadline']<=time.time():raise Denied('DEADLINE_AT_EFFECT_BOUNDARY')
            self.check_dependencies(db,wid)
            payload=json.loads(w['payload'])
            if digest(payload)!=w['payload_hash']:raise Denied('PAYLOAD_CHANGED')
            if w['profile']!='local-atomic':
                db.execute("UPDATE works SET state='UNKNOWN' WHERE id=?",(wid,));self.event(db,'unsupported_target',{'work':wid})
                return self._status(db,wid)
            counter=db.execute('SELECT * FROM targetdb.counters WHERE tenant=? AND target=?',(w['tenant'],w['target'])).fetchone()
            version=counter['version'] if counter else 0
            if 'expected_version' in payload and payload['expected_version']!=version:
                db.execute("UPDATE works SET state='REJECTED' WHERE id=?",(wid,))
                db.execute("UPDATE attempts SET phase='REJECTED_PRE_EFFECT' WHERE id=?",(attempt,))
                self.event(db,'condition_rejected',{'work':wid,'expected':payload['expected_version'],'observed':version,'effect':'NONE_AT_LOCAL_ATOMIC_BOUNDARY'})
                return self._status(db,wid)
            prior=db.execute('SELECT * FROM targetdb.effects WHERE id=?',(wid,)).fetchone()
            if prior and (prior['tenant'],prior['target'],prior['payload_hash'])!=(w['tenant'],w['target'],w['payload_hash']):raise Denied('TARGET_IDENTITY_CONFLICT')
            if not prior:
                db.execute('INSERT INTO targetdb.effects VALUES(?,?,?,?,?,?,?)',(wid,w['tenant'],w['target'],w['payload_hash'],payload['delta'],epoch,time.time()))
                db.execute('INSERT INTO targetdb.counters VALUES(?,?,?,1) ON CONFLICT(tenant,target) DO UPDATE SET value=value+excluded.value,version=version+1',(w['tenant'],w['target'],payload['delta']))
            db.execute("UPDATE attempts SET phase='TARGET_COMMITTED' WHERE id=?",(attempt,))
        if crash=='after-target':os._exit(72)
        return self.reconcile(wid,worker=worker,epoch=epoch)

    def reconcile(self,wid,*,worker,epoch):
        with self.transaction() as db:
            self.check_owner(db,worker,epoch);w=self.work(db,wid)
            # Readback is allowed after grant revocation; no target mutation occurs.
            if w['state'] in ('ADMITTED','REJECTED','CANCELLED'):return self._status(db,wid)
            visibility=db.execute('SELECT available FROM targetdb.visibility WHERE tenant=? AND target=?',(w['tenant'],w['target'])).fetchone()
            visible=visibility[0] if visibility else True
            effect=db.execute('SELECT * FROM targetdb.effects WHERE id=?',(wid,)).fetchone() if visible else None
            if visible and effect and w['profile']=='local-atomic':
                if (effect['tenant'],effect['target'],effect['payload_hash'],effect['delta'])!=(w['tenant'],w['target'],w['payload_hash'],json.loads(w['payload'])['delta']):raise Denied('EVIDENCE_IDENTITY_MISMATCH')
                state='VERIFIED';proof=dict(effect)
            else:
                # Absence never resets a possibly dispatched effect to retryable.
                state='UNKNOWN';proof={'visible':bool(visible),'effect_found':bool(effect),'not_proof_of_quiescence':True}
            db.execute('UPDATE works SET state=? WHERE id=?',(state,wid))
            db.execute('INSERT INTO observations(work,kind,evidence,at) VALUES(?,?,?,?)',(wid,state,encoded(proof),time.time()))
            self.event(db,'reconciled',{'work':wid,'state':state})
            return self._status(db,wid)

    def recover_local(self,wid,*,worker,epoch):
        """Retry only after the old local effect-time epoch is fenced.

        The proof uses the same locked local target and controller. It does
        not apply to a remote queue, worker-controlled target, or opaque API.
        """
        with self.transaction() as db:
            self.check_owner(db,worker,epoch);w=self.work(db,wid)
            if w['profile']!='local-atomic':raise Denied('LOCAL_PROFILE_REQUIRED')
            if w['state'] not in ('DISPATCHED','UNKNOWN'):raise Denied('RECOVERY_STATE_REQUIRED')
            attempts=list(db.execute('SELECT * FROM attempts WHERE work=?',(wid,)))
            if not attempts or any(a['epoch']>=epoch for a in attempts):raise Denied('ORIGINAL_EPOCH_NOT_FENCED')
            visible=db.execute('SELECT available FROM targetdb.visibility WHERE tenant=? AND target=?',(w['tenant'],w['target'])).fetchone()
            if visible and not visible[0]:raise Denied('TARGET_EVIDENCE_UNAVAILABLE')
            effect=db.execute('SELECT * FROM targetdb.effects WHERE id=?',(wid,)).fetchone()
            if effect:
                if not self.target_evidence_valid(db,w):raise Denied('EVIDENCE_IDENTITY_MISMATCH')
                state='VERIFIED';proof=dict(effect)
            else:
                self.valid_grant(db,w['grant_id'],w['tenant'],w['target'])
                if w['deadline']<=time.time() or w['attempts']>=w['budget']:raise Denied('WORK_BUDGET_OR_DEADLINE')
                state='ADMITTED';proof={'old_epochs':[a['epoch'] for a in attempts],'current_epoch':epoch,'target_absent_under_local_lock':True}
                db.execute("UPDATE attempts SET phase='FENCED_NO_EFFECT' WHERE work=?",(wid,))
            db.execute('UPDATE works SET state=? WHERE id=?',(state,wid))
            db.execute('INSERT INTO observations(work,kind,evidence,at) VALUES(?,?,?,?)',(wid,'LOCAL_RECOVERY',encoded(proof),time.time()))
            db.execute("UPDATE waits SET status='RESOLVED' WHERE work=?",(wid,))
            self.event(db,'local_recovery',{'work':wid,'state':state,'epoch':epoch})
            return self._status(db,wid)

    def cancel(self,wid):
        """Operator cancellation fences an uncommitted local attempt.

        An opaque dispatched effect remains unknown. Cancellation never
        removes a committed target effect or represents compensation.
        """
        with self.transaction() as db:
            w=self.work(db,wid)
            effect=db.execute('SELECT * FROM targetdb.effects WHERE id=?',(wid,)).fetchone()
            if effect:
                if not self.target_evidence_valid(db,w):raise Denied('TARGET_EVIDENCE_UNAVAILABLE_OR_MISMATCH')
                state='VERIFIED'
            elif w['profile']=='local-atomic' or w['state'] in ('ADMITTED','CANCELLED','REJECTED'):
                state='CANCELLED'
            else:
                state='UNKNOWN'
            db.execute('UPDATE works SET state=? WHERE id=?',(state,wid))
            if state=='CANCELLED':db.execute("UPDATE waits SET status='CANCELLED' WHERE work=?",(wid,))
            prior_cancel=any(json.loads(r[0]).get('work')==wid for r in db.execute("SELECT body FROM events WHERE kind='operator_cancel'"))
            if not prior_cancel:self.event(db,'operator_cancel',{'work':wid,'state':state,'remote_cancellation_proved':False})
            return self._status(db,wid)

    def visibility(self,available,*,tenant,target):
        if type(available)!=bool:raise Denied('BOOLEAN_REQUIRED')
        identifier(tenant);identifier(target)
        with self.transaction() as db:
            db.execute('INSERT INTO targetdb.visibility VALUES(?,?,?) ON CONFLICT(tenant,target) DO UPDATE SET available=excluded.available',(tenant,target,int(available)))
            self.event(db,'synthetic_target_visibility',{'available':available,'tenant':tenant,'target':target})

    def wait(self,wid,*,due_seconds=0,attempts=3):
        if not 0<=due_seconds<=86400 or type(attempts)!=int or not 0<attempts<=20:raise Denied('INVALID_WAIT')
        with self.transaction() as db:
            w=self.work(db,wid)
            if w['state']!='UNKNOWN':raise Denied('WAIT_REQUIRES_UNKNOWN')
            # Repeated registration cannot reset deadline or budget.
            db.execute('INSERT OR IGNORE INTO waits VALUES(?,?,?,?,NULL,?)',(wid,time.time()+due_seconds,w['deadline'],attempts,'REGISTERED_FOREGROUND'))
            self.event(db,'wait_registered',{'work':wid,'wake':'explicit camden-work service invocation; no background daemon'})

    def service(self,*,worker,epoch):
        with self.transaction() as db:
            self.check_owner(db,worker,epoch)
            rows=[dict(r) for r in db.execute("SELECT * FROM waits WHERE status='REGISTERED_FOREGROUND' AND due<=?",(time.time(),))]
        results=[]
        for row in rows:
            with self.transaction() as db:
                self.check_owner(db,worker,epoch)
                current=db.execute('SELECT * FROM waits WHERE work=?',(row['work'],)).fetchone()
                if current['status']!='REGISTERED_FOREGROUND' or current['due']>time.time():continue
                if current['remaining']<=0 or current['deadline']<=time.time():
                    db.execute("UPDATE waits SET status='EXHAUSTED',last_serviced=? WHERE work=?",(time.time(),row['work']));continue
                db.execute('UPDATE waits SET remaining=remaining-1,last_serviced=?,due=? WHERE work=?',(time.time(),time.time()+1,row['work']))
            result=self.reconcile(row['work'],worker=worker,epoch=epoch);results.append(result)
            if result['work']['state']=='VERIFIED':
                with self.transaction() as db:db.execute("UPDATE waits SET status='RESOLVED' WHERE work=?",(row['work'],))
        return results

    def _status(self,db,wid=None):
        if wid:
            w=dict(self.work(db,wid));return {'work':w,'attempts':[dict(x) for x in db.execute('SELECT * FROM attempts WHERE work=?',(wid,))],'observations':[dict(x) for x in db.execute('SELECT * FROM observations WHERE work=?',(wid,))]}
        return {'schema':SCHEMA,'node':db.execute("SELECT value FROM config WHERE key='node'").fetchone()[0],'owner':dict(db.execute('SELECT * FROM owner').fetchone()),'works':[dict(x) for x in db.execute('SELECT * FROM works')],'grants':[dict(x) for x in db.execute('SELECT * FROM grants')],'attempts':[dict(x) for x in db.execute('SELECT * FROM attempts')],'observations':[dict(x) for x in db.execute('SELECT * FROM observations')],'dependencies':[dict(x) for x in db.execute('SELECT * FROM dependencies')],'waits':[dict(x) for x in db.execute('SELECT * FROM waits')],'events':[dict(x) for x in db.execute('SELECT * FROM events')],'target_effects':[dict(x) for x in db.execute('SELECT * FROM targetdb.effects')],'limits':['Local trusted operator and filesystem','No remote exactly-once guarantee','Foreground service has no future wake unless invoked']}

    def status(self,wid=None):
        with self.transaction() as db:return self._status(db,wid)

    def disposition_accounted(self,db,w):
        if w['state']=='VERIFIED':return self.target_evidence_valid(db,w)
        if w['state']!='CANCELLED':return False
        # A cancelled label alone is not authority or absence evidence.
        cancelled=any(json.loads(r[0]).get('work')==w['id'] and json.loads(r[0]).get('state')=='CANCELLED' for r in db.execute("SELECT body FROM events WHERE kind='operator_cancel'"))
        if not cancelled:return False
        if db.execute('SELECT 1 FROM targetdb.effects WHERE id=?',(w['id'],)).fetchone():return False
        visible=db.execute('SELECT available FROM targetdb.visibility WHERE tenant=? AND target=?',(w['tenant'],w['target'])).fetchone()
        if visible and not visible[0]:return False
        # Local cancellation is checked under the same effect-time lock.
        # Opaque cancellation is terminal only before any dispatch attempt.
        return w['profile']=='local-atomic' or (w['attempts']==0 and not db.execute('SELECT 1 FROM attempts WHERE work=?',(w['id'],)).fetchone())

    def export(self,name='result'):
        identifier(name)
        with self.transaction() as db:
            if (self.root/'exports'/(name+'.json')).exists() or (self.root/'exports'/(name+'.md')).exists():raise FileExistsError('Frozen export already exists')
            reservations=[json.loads(r[0]) for r in db.execute("SELECT body FROM events WHERE kind='result_reservation'")]
            if any(r['name']==name for r in reservations):raise Denied('RESULT_NAME_RESERVED')
            if len(reservations)>=MAX_EXPORTS:raise Denied('EXPORT_BUDGET')
            self.event(db,'result_reservation',{'name':name})
            snapshot=self._status(db)
            fresh={w['id']:self.target_evidence_valid(db,w) for w in snapshot['works']}
            accounted={w['id']:bool(self.disposition_accounted(db,w)) for w in snapshot['works']}
        snapshot['export_target_checks']=fresh
        complete=bool(snapshot['works']) and all(w['state']=='VERIFIED' and fresh[w['id']] for w in snapshot['works'])
        disposed=bool(snapshot['works']) and all(accounted.values())
        snapshot.update(all_required_work_verified=complete,all_required_work_accounted=disposed,disposition_checks=accounted,export_is_remote_delivery=False,snapshot_at=time.time())
        directory=self.root/'exports';directory.mkdir(exist_ok=True)
        json_path=directory/(name+'.json');md_path=directory/(name+'.md')
        body='# '+md_path.name+'\n\n'+('All admitted local work verified.' if complete else 'All local work is accounted for, including explicit cancellations. Cancelled outcomes were not performed.' if disposed else 'Work remains incomplete. Unknown effects stay fenced.')+'\n\n'
        body+='Snapshot Unix time: '+str(snapshot['snapshot_at'])+'\n\n## Authority and owner\n\n'
        owner=snapshot['owner']
        body+='Node '+snapshot['node']+'; worker '+str(owner['worker'])+'; epoch '+str(owner['epoch'])+'; stopped '+str(bool(owner['stopped']))+'.\n\n'
        for grant in snapshot['grants']:
            body+='- Grant '+grant['id']+': '+grant['tenant']+'/'+grant['target']+'; revoked '+str(bool(grant['revoked']))+'; expiry '+str(grant['expires'])+'; effect budget '+str(grant['max_effects'])+'.\n'
        body+='\n## Work and effects\n\n'
        for w in snapshot['works']:
            payload=json.loads(w['payload'])
            body+='- '+w['id']+': '+w['state']+'; tenant '+w['tenant']+'; target '+w['target']+'; delta '+str(payload['delta'])+'; profile '+w['profile']+'; attempts '+str(w['attempts'])+'/'+str(w['budget'])+'; deadline '+str(w['deadline'])+'; current target check '+str(fresh[w['id']])+'.\n'
        body+='\nVerified target effects: '+str(sum(bool(v) for v in fresh.values()))+'. Stored target records: '+str(len(snapshot['target_effects']))+'.\n'
        for dependency in snapshot['dependencies']:body+='- Dependency: '+dependency['work']+' requires '+dependency['dependency']+'.\n'
        body+='\n## Waits and continuation\n\nNo background wake is armed. The operator must invoke the foreground service after the condition changes.\n\n'
        for wait in snapshot['waits']:
            body+='- '+wait['work']+': '+wait['status']+'; due '+str(wait['due'])+'; original deadline '+str(wait['deadline'])+'; remaining attempts '+str(wait['remaining'])+'; last serviced '+str(wait['last_serviced'])+'.\n'
        if not snapshot['waits']:body+='No registered waits at freeze.\n'
        body+='\n## Attempts and evidence\n\n'
        for attempt in snapshot['attempts']:body+='- '+attempt['id']+': work '+attempt['work']+'; phase '+attempt['phase']+'; owner epoch '+str(attempt['epoch'])+'.\n'
        body+='\nRetained observations: '+str(len(snapshot['observations']))+'; events: '+str(len(snapshot['events']))+'. Exact evidence remains in the accompanying JSON snapshot.\n'
        body+='\n## Finalization at freeze\n\nThis file has not established its own adoption or delivery. The current owner must adopt this exact result, deliver it to the local inbox, then run finalization with fresh target checks. No remote delivery is established.\n'
        body+='\n## Limits\n\n'+'\n'.join('- '+x for x in snapshot['limits'])+'\n\nThis local export is not a remote delivery receipt.\n'
        # Never overwrite a frozen report or pretend its receipt is already known.
        with json_path.open('x',encoding='utf8') as f:f.write(encoded(snapshot)+'\n')
        with md_path.open('x',encoding='utf8') as f:f.write(body)
        with self.transaction() as db:
            self.event(db,'result_frozen',{'name':name,'artifact_sha256':hashlib.sha256(md_path.read_bytes()).hexdigest(),'snapshot_sha256':hashlib.sha256(json_path.read_bytes()).hexdigest()})
        return {'json':str(json_path),'markdown':str(md_path),'sha256':hashlib.sha256(md_path.read_bytes()).hexdigest(),'complete':complete,'accounted':disposed,'remote_delivery':False}

    def _result(self,db,name):
        identifier(name)
        records=[json.loads(r[0]) for r in db.execute("SELECT body FROM events WHERE kind='result_frozen'")]
        records=[r for r in records if r['name']==name]
        if len(records)!=1:raise Denied('FROZEN_RESULT_REQUIRED')
        record=records[0];md=self.root/'exports'/(name+'.md');js=self.root/'exports'/(name+'.json')
        if not md.is_file() or not js.is_file():raise Denied('RESULT_FILES_MISSING')
        if hashlib.sha256(md.read_bytes()).hexdigest()!=record['artifact_sha256'] or hashlib.sha256(js.read_bytes()).hexdigest()!=record['snapshot_sha256']:raise Denied('FROZEN_RESULT_CHANGED')
        snapshot=json.loads(js.read_text(encoding='utf8'))
        current=[dict(r) for r in db.execute('SELECT * FROM works')]
        if {w['id'] for w in current}!={w['id'] for w in snapshot['works']}:raise Denied('RESULT_SCOPE_STALE')
        if not current or not snapshot.get('all_required_work_accounted',snapshot.get('all_required_work_verified')) or any(not self.disposition_accounted(db,w) for w in current):raise Denied('CURRENT_WORK_UNVERIFIED')
        return record,md

    def _result_event(self,db,kind,record):
        return any(json.loads(r[0]).get('result')==record for r in db.execute('SELECT body FROM events WHERE kind=?',(kind,)))

    def adopt_result(self,name,*,worker,epoch):
        """Parent-owned fresh check of a frozen result, not an assistant claim."""
        with self.transaction() as db:
            self.check_owner(db,worker,epoch);record,_=self._result(db,name)
            if not self._result_event(db,'parent_adoption',record):
                self.event(db,'parent_adoption',{'result':record,'worker':worker,'epoch':epoch,'scope':'Local synthetic target evidence'})
            return {'adopted':True,'result':record,'scope':'LOCAL_SYNTHETIC'}

    def deliver_local(self,name,*,worker,epoch):
        """Copy immutable bytes to this node's explicit local result inbox.

        Readback can reconcile a copy committed before the receipt event.
        This is local filesystem delivery, never a Telegram/provider receipt.
        """
        with self.transaction() as db:
            self.check_owner(db,worker,epoch);record,source=self._result(db,name)
            if not self._result_event(db,'parent_adoption',record):raise Denied('ADOPTION_REQUIRED')
            inbox=self.root/'inbox';inbox.mkdir(exist_ok=True)
            received=inbox/(name+'.md')
            if not received.exists():
                staging=inbox/(name+'.pending')
                with staging.open('wb') as stream:
                    stream.write(source.read_bytes());stream.flush();os.fsync(stream.fileno())
                # The controller lock serializes admitted local deliveries.
                # Interrupted staging is never mistaken for an accepted file.
                staging.replace(received)
            if hashlib.sha256(received.read_bytes()).hexdigest()!=record['artifact_sha256']:raise Denied('DELIVERY_BYTES_CHANGED')
            if not self._result_event(db,'local_delivery',record):
                self.event(db,'local_delivery',{'result':record,'recipient':'LOCAL_NODE_INBOX','readback':True})
            return {'received_path':str(received),'artifact_sha256':record['artifact_sha256'],'readback':True,'remote_delivery':False}

    def finalize(self,name,*,worker,epoch):
        with self.transaction() as db:
            self.check_owner(db,worker,epoch);record,_=self._result(db,name)
            if not self._result_event(db,'parent_adoption',record):raise Denied('ADOPTION_REQUIRED')
            if not self._result_event(db,'local_delivery',record):raise Denied('DELIVERY_REQUIRED')
            received=self.root/'inbox'/(name+'.md')
            if not received.is_file() or hashlib.sha256(received.read_bytes()).hexdigest()!=record['artifact_sha256']:raise Denied('DELIVERY_BYTES_CHANGED')
            if not self._result_event(db,'local_ready',record):self.event(db,'local_ready',{'result':record,'epoch':epoch})
            return {'ready':True,'result':record,'delivery_scope':'LOCAL_NODE_INBOX','remote_delivery':False,'checked_at':time.time()}

    def verify(self,wid,*,worker,epoch):
        """Recheck target evidence even if a cached local result says verified."""
        with self.transaction() as db:
            self.check_owner(db,worker,epoch);w=self.work(db,wid)
            effect=db.execute('SELECT * FROM targetdb.effects WHERE id=?',(wid,)).fetchone()
            visible=db.execute('SELECT available FROM targetdb.visibility WHERE tenant=? AND target=?',(w['tenant'],w['target'])).fetchone()
            valid=bool((not visible or visible[0]) and effect and w['profile']=='local-atomic' and (effect['tenant'],effect['target'],effect['payload_hash'],effect['delta'])==(w['tenant'],w['target'],w['payload_hash'],json.loads(w['payload'])['delta']))
            proof={'work':wid,'target_read':bool(not visible or visible[0]),'valid':valid,'at':time.time(),'scope':'Exact synthetic occurrence, not arbitrary semantic truth'}
            db.execute('INSERT INTO observations(work,kind,evidence,at) VALUES(?,?,?,?)',(wid,'REVERIFY',encoded(proof),time.time()))
            if not valid:db.execute("UPDATE works SET state='UNKNOWN' WHERE id=?",(wid,))
            return proof

    def import_review(self,source):
        """Preserve a snapshot as inert review data, never restore live grants."""
        path=Path(source)
        if not path.is_file() or path.stat().st_size>8*1024*1024:raise Denied('IMPORT_SIZE_OR_PATH')
        data=json.loads(path.read_text(encoding='utf8'))
        if data.get('schema')!=SCHEMA or not isinstance(data.get('works'),list) or not isinstance(data.get('grants'),list):raise Denied('IMPORT_SCHEMA')
        # Imports deliberately cannot populate work/owner/grant/target tables.
        # Newer revocation and deletion decisions therefore remain authoritative.
        identity=digest(data)
        with self.transaction() as db:
            self.event(db,'import_for_review',{'snapshot_digest':identity,'snapshot':data,'runnable':False,'requires':'Current operator policy and external effect reconciliation before any new admission'})
        return {'snapshot_digest':identity,'runnable':False,'grants_imported':0,'effects_replayed':0}
