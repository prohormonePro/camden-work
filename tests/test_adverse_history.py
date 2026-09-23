import contextlib,tempfile,unittest
from unittest.mock import patch
from camden_work.core import Node,Denied

class AdverseHistory(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.n=Node.initialize(self.tmp.name);self.g=self.n.grant(tenant='demo',target='counter')
        self.w=self.n.admit(grant=self.g,tenant='demo',target='counter',delta=1)
        self.n.claim('worker',expected_epoch=0)

    def test_boolean_epoch_is_not_a_typed_owner_version(self):
        with self.assertRaises(Denied):self.n.execute(self.w,worker='worker',epoch=True)
        self.assertEqual(self.n.status()['target_effects'],[])

    def test_stop_between_intent_and_effect_fences_late_worker(self):
        original=self.n.transaction;calls=0
        @contextlib.contextmanager
        def crossing():
            nonlocal calls
            calls+=1
            if calls==2:
                # This is the admitted operator stop transaction before the
                # old worker enters its target transaction.
                with original() as db:db.execute('UPDATE owner SET stopped=1')
            with original() as db:yield db
        with patch.object(self.n,'transaction',crossing):
            with self.assertRaisesRegex(Denied,'WORKER_FENCED'):self.n.execute(self.w,worker='worker',epoch=1)
        self.assertEqual(self.n.status()['target_effects'],[])
        self.assertEqual(self.n.status(self.w)['work']['attempts'],1)

    def test_revocation_between_intent_and_effect_is_current(self):
        original=self.n.transaction;calls=0
        @contextlib.contextmanager
        def crossing():
            nonlocal calls
            calls+=1
            if calls==2:
                with original() as db:db.execute('UPDATE grants SET revoked=1 WHERE id=?',(self.g,))
            with original() as db:yield db
        with patch.object(self.n,'transaction',crossing):
            with self.assertRaisesRegex(Denied,'GRANT_INACTIVE'):self.n.execute(self.w,worker='worker',epoch=1)
        self.assertEqual(self.n.status()['target_effects'],[])

    def test_expired_grant_does_not_erase_or_repeat_accepted_effect(self):
        self.n.execute(self.w,worker='worker',epoch=1)
        expiry=self.n.status()['grants'][0]['expires']
        with patch('camden_work.core.time.time',return_value=expiry+1):
            with self.assertRaisesRegex(Denied,'GRANT_INACTIVE'):self.n.execute(self.w,worker='worker',epoch=1)
            self.assertEqual(self.n.reconcile(self.w,worker='worker',epoch=1)['work']['state'],'VERIFIED')
        self.assertEqual(len(self.n.status()['target_effects']),1)

    def test_parent_and_delivery_receipts_survive_new_controller(self):
        self.n.execute(self.w,worker='worker',epoch=1);self.n.export('result')
        self.n.adopt_result('result',worker='worker',epoch=1)
        self.n.deliver_local('result',worker='worker',epoch=1)
        fresh=Node(self.tmp.name)
        fresh.adopt_result('result',worker='worker',epoch=1)
        fresh.deliver_local('result',worker='worker',epoch=1)
        self.assertTrue(fresh.finalize('result',worker='worker',epoch=1)['ready'])
        events=fresh.status()['events']
        self.assertEqual(sum(e['kind']=='parent_adoption' for e in events),1)
        self.assertEqual(sum(e['kind']=='local_delivery' for e in events),1)
