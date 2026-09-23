import json,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
from camden_work.core import Node,Denied

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.n=Node.initialize(Path(self.tmp.name)/'node')
        self.g=self.n.grant(tenant='demo',target='counter')
        self.epoch=self.n.claim('worker1',expected_epoch=0)

    def admit(self,**kw):
        return self.n.admit(**{'grant':self.g,'tenant':'demo','target':'counter','delta':1,**kw})

    def execute(self,w,**kw):return self.n.execute(w,worker='worker1',epoch=self.epoch,**kw)

    def crash(self,w,point='after-target'):
        r=subprocess.run([sys.executable,'-B','-m','camden_work','--workspace',str(self.n.root),'execute','--work',w,'--worker','worker1','--epoch',str(self.epoch),'--crash',point],capture_output=True)
        self.assertEqual(r.returncode,72 if point=='after-target' else 71,r.stderr)

    def test_real_lost_ack_and_replacement(self):
        w=self.admit();self.crash(w)
        self.assertEqual(self.n.status(w)['work']['state'],'DISPATCHED')
        # Target evidence is read independently from a separate database connection.
        db=sqlite3.connect(self.n.root/'target.sqlite3')
        self.assertEqual(db.execute('select count(*) from effects').fetchone()[0],1);db.close()
        self.n.stop(expected_epoch=1);e=self.n.claim('worker2',expected_epoch=1)
        r=self.n.reconcile(w,worker='worker2',epoch=e)
        self.assertEqual(r['work']['state'],'VERIFIED')
        with self.assertRaisesRegex(Denied,'WORKER_FENCED'):self.execute(w)
        self.assertEqual(len(self.n.status()['target_effects']),1)

    def test_unknown_independent_progress_and_servicing(self):
        w=self.admit();self.crash(w);self.n.visibility(False,tenant='demo',target='counter')
        self.assertEqual(self.n.reconcile(w,worker='worker1',epoch=1)['work']['state'],'UNKNOWN')
        with self.assertRaisesRegex(Denied,'RECONCILE'):self.execute(w)
        conflict=self.admit()
        with self.assertRaisesRegex(Denied,'CONFLICTING_UNKNOWN'):self.execute(conflict)
        g=self.n.grant(tenant='demo',target='independent')
        other=self.admit(grant=g,target='independent')
        self.assertEqual(self.execute(other)['work']['state'],'VERIFIED')
        self.n.wait(w);self.n.visibility(True,tenant='demo',target='counter')
        self.assertEqual(self.n.service(worker='worker1',epoch=1)[0]['work']['state'],'VERIFIED')
        self.assertEqual(self.n.status()['waits'][0]['status'],'RESOLVED')
        self.assertEqual(self.execute(conflict)['work']['state'],'VERIFIED')

    def test_absence_does_not_allow_retry(self):
        w=self.admit();self.crash(w,'after-intent')
        self.assertEqual(self.n.reconcile(w,worker='worker1',epoch=1)['work']['state'],'UNKNOWN')
        with self.assertRaisesRegex(Denied,'RECONCILE'):self.execute(w)

    def test_stop_is_explicit(self):
        with self.assertRaisesRegex(Denied,'EXPLICIT_STOP'):self.n.claim('worker2',expected_epoch=1)
        self.n.stop(expected_epoch=1)
        with self.assertRaisesRegex(Denied,'WORKER_FENCED'):self.execute(self.admit())

    def test_wrong_owner_version(self):
        with self.assertRaisesRegex(Denied,'OWNER_VERSION'):self.n.stop(expected_epoch=0)

    def test_revocation(self):
        w=self.admit();self.n.revoke(self.g)
        with self.assertRaisesRegex(Denied,'GRANT_INACTIVE'):self.execute(w)
        self.assertEqual(len(self.n.status()['target_effects']),0)

    def test_wrong_scope(self):
        for field in ('tenant','target'):
            with self.subTest(field=field),self.assertRaisesRegex(Denied,'SCOPE'):self.admit(**{field:'other'})

    def test_distinct_identical_requests(self):
        a=self.admit();b=self.admit();self.assertNotEqual(a,b);self.execute(a);self.execute(b)
        self.assertEqual(len(self.n.status()['target_effects']),2)

    def test_dependency(self):
        a=self.admit();b=self.admit(dependencies=[a])
        with self.assertRaisesRegex(Denied,'DEPENDENCY_UNVERIFIED'):self.execute(b)
        self.execute(a);self.assertEqual(self.execute(b)['work']['state'],'VERIFIED')

    def test_aggregate_reservation(self):
        g=self.n.grant(tenant='demo',target='small',max_effects=1)
        self.admit(grant=g,target='small')
        with self.assertRaisesRegex(Denied,'GRANT_BUDGET'):self.admit(grant=g,target='small')

    def test_bad_input_not_authority(self):
        for value in [True,'approved',0,10001]:
            with self.subTest(value=value),self.assertRaises(Denied):self.admit(delta=value)

    def test_intact_claim_hash_not_target_evidence(self):
        w=self.admit()
        self.assertEqual(self.n.reconcile(w,worker='worker1',epoch=1)['work']['state'],'ADMITTED')
        self.assertFalse(self.n.export()['complete'])

    def test_wrong_target_receipt(self):
        w=self.admit();self.crash(w)
        db=sqlite3.connect(self.n.root/'target.sqlite3');db.execute("update effects set tenant='other'");db.commit();db.close()
        with self.assertRaisesRegex(Denied,'EVIDENCE_IDENTITY'):self.n.reconcile(w,worker='worker1',epoch=1)

    def test_export_immutable_and_local(self):
        w=self.admit();self.execute(w);r=self.n.export()
        self.assertTrue(r['complete']);self.assertFalse(r['remote_delivery'])
        with self.assertRaises(FileExistsError):self.n.export()

    def test_export_path_escape(self):
        with self.assertRaises(Denied):self.n.export('../other')

    def test_empty_result_not_complete(self):self.assertFalse(self.n.export()['complete'])

    def test_wait_budget_not_reset(self):
        w=self.admit(profile='opaque');self.execute(w);self.n.wait(w,attempts=1)
        self.n.service(worker='worker1',epoch=1);self.n.wait(w,attempts=20)
        self.assertEqual(self.n.status()['waits'][0]['remaining'],0)

    def test_schema_rejected(self):
        db=sqlite3.connect(self.n.path);db.execute("update config set value='99' where key='schema'");db.commit();db.close()
        with self.assertRaisesRegex(Denied,'UNSUPPORTED_SCHEMA'):self.n.status()

if __name__=='__main__':unittest.main()
