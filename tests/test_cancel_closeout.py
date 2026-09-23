import tempfile,unittest
from camden_work.core import Node,Denied

class CancelCloseout(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.n=Node.initialize(t.name);self.g=self.n.grant(tenant='demo',target='counter');self.n.claim('worker',expected_epoch=0)
    def admit(self,profile='local-atomic'):
        return self.n.admit(grant=self.g,tenant='demo',target='counter',delta=1,profile=profile)
    def test_explicit_undispatched_cancellation_is_accounted_not_success(self):
        w=self.admit('opaque');self.n.cancel(w);result=self.n.export()
        self.assertFalse(result['complete']);self.assertTrue(result['accounted'])
        self.n.adopt_result('result',worker='worker',epoch=1)
        self.n.deliver_local('result',worker='worker',epoch=1)
        self.assertTrue(self.n.finalize('result',worker='worker',epoch=1)['ready'])
        self.assertEqual(self.n.status()['target_effects'],[])
    def test_unknown_opaque_cancellation_does_not_close(self):
        w=self.admit('opaque');self.n.execute(w,worker='worker',epoch=1);self.n.cancel(w)
        self.assertFalse(self.n.export()['accounted'])
        with self.assertRaises(Denied):self.n.adopt_result('result',worker='worker',epoch=1)
    def test_cancelled_label_without_operator_event_does_not_close(self):
        w=self.admit()
        with self.n.transaction() as db:db.execute("UPDATE works SET state='CANCELLED' WHERE id=?",(w,))
        self.assertFalse(self.n.export()['accounted'])
    def test_changed_target_visibility_invalidates_cancelled_result(self):
        w=self.admit();self.n.cancel(w);self.n.export()
        self.n.visibility(False,tenant='demo',target='counter')
        with self.assertRaises(Denied):self.n.adopt_result('result',worker='worker',epoch=1)
