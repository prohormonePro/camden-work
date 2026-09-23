import subprocess
import sys
import tempfile
import unittest
from camden_work.core import Node, Denied


class LocalRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.n = Node.initialize(self.tmp.name)
        self.g = self.n.grant(tenant='demo', target='counter')
        self.w = self.n.admit(grant=self.g, tenant='demo', target='counter', delta=1)
        self.n.claim('old', expected_epoch=0)

    def crash_intent(self):
        result = subprocess.run([sys.executable, '-B', '-m', 'camden_work', '--workspace', self.tmp.name,
            'execute', '--work', self.w, '--worker', 'old', '--epoch', '1', '--crash', 'after-intent'], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 71)

    def test_fenced_local_intent_can_resume_same_occurrence(self):
        self.crash_intent()
        self.n.stop(expected_epoch=1)
        self.n.claim('new', expected_epoch=1)
        result = self.n.recover_local(self.w, worker='new', epoch=2)
        self.assertEqual(result['work']['state'], 'ADMITTED')
        self.assertEqual(result['work']['attempts'], 1)
        with self.assertRaisesRegex(Denied, 'WORKER_FENCED'):
            self.n.execute(self.w, worker='old', epoch=1)
        self.assertEqual(self.n.execute(self.w, worker='new', epoch=2)['work']['state'], 'VERIFIED')
        self.assertEqual(len(self.n.status()['target_effects']), 1)

    def test_absence_without_old_epoch_fence_cannot_enable_retry(self):
        self.crash_intent()
        with self.assertRaisesRegex(Denied, 'ORIGINAL_EPOCH_NOT_FENCED'):
            self.n.recover_local(self.w, worker='old', epoch=1)

    def test_opaque_profile_cannot_claim_local_quiescence(self):
        w = self.n.admit(grant=self.g, tenant='demo', target='counter', delta=1, profile='opaque')
        self.n.execute(w, worker='old', epoch=1)
        self.n.stop(expected_epoch=1)
        self.n.claim('new', expected_epoch=1)
        with self.assertRaisesRegex(Denied, 'LOCAL_PROFILE_REQUIRED'):
            self.n.recover_local(w, worker='new', epoch=2)

    def test_cancel_undispatched_work_is_not_success(self):
        self.assertEqual(self.n.cancel(self.w)['work']['state'], 'CANCELLED')
        with self.assertRaises(Denied):
            self.n.execute(self.w, worker='old', epoch=1)
        self.assertFalse(self.n.export()['complete'])

    def test_cancel_retains_committed_effect(self):
        self.n.execute(self.w, worker='old', epoch=1)
        self.assertEqual(self.n.cancel(self.w)['work']['state'], 'VERIFIED')
        self.assertEqual(len(self.n.status()['target_effects']), 1)

    def test_cancelled_intent_cannot_later_commit(self):
        from contextlib import contextmanager
        original = self.n.transaction
        count = 0
        @contextmanager
        def interleave():
            nonlocal count
            count += 1
            if count == 2:
                self.n.transaction = original
                self.n.cancel(self.w)
            with original() as db:
                yield db
        self.n.transaction = interleave
        with self.assertRaisesRegex(Denied, 'ATTEMPT_NO_LONGER_DISPATCHED'):
            self.n.execute(self.w, worker='old', epoch=1)
        self.assertEqual(self.n.status()['target_effects'], [])

    def test_opaque_cancel_preserves_unknown(self):
        w = self.n.admit(grant=self.g, tenant='demo', target='counter', delta=1, profile='opaque')
        self.n.execute(w, worker='old', epoch=1)
        self.assertEqual(self.n.cancel(w)['work']['state'], 'UNKNOWN')

    def test_recovery_does_not_restore_revoked_authority(self):
        self.crash_intent()
        self.n.stop(expected_epoch=1)
        self.n.claim('new', expected_epoch=1)
        self.n.revoke(self.g)
        with self.assertRaisesRegex(Denied, 'GRANT_INACTIVE'):
            self.n.recover_local(self.w, worker='new', epoch=2)
        self.assertEqual(self.n.status(self.w)['work']['attempts'], 1)


if __name__ == '__main__':
    unittest.main()
