import tempfile
import unittest
from camden_work.core import Node, Denied


class EffectPreconditions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.n = Node.initialize(self.tmp.name)
        self.g = self.n.grant(tenant='tenant', target='counter')
        self.n.claim('worker', expected_epoch=0)

    def admit(self, delta=1, **kw):
        return self.n.admit(grant=self.g, tenant='tenant', target='counter', delta=delta, **kw)

    def execute(self, work):
        return self.n.execute(work, worker='worker', epoch=1)

    def test_compensation_cannot_be_admitted_twice(self):
        original = self.admit(2)
        self.execute(original)
        reverse = self.admit(-2, expected_version=1, compensates=original)
        self.execute(reverse)
        with self.assertRaisesRegex(Denied, 'COMPENSATION_ALREADY_RESERVED'):
            self.admit(-2, expected_version=2, compensates=original)
        self.assertEqual(len(self.n.status()['target_effects']), 2)

    def test_dependency_target_is_rechecked_before_effect(self):
        original = self.admit()
        self.execute(original)
        other = self.n.grant(tenant='tenant', target='independent')
        dependent = self.n.admit(grant=other, tenant='tenant', target='independent', delta=1, dependencies=[original])
        self.n.visibility(False, tenant='tenant', target='counter')
        with self.assertRaisesRegex(Denied, 'DEPENDENCY_EVIDENCE_UNAVAILABLE'):
            self.execute(dependent)
        self.assertEqual(len(self.n.status()['target_effects']), 1)

    def test_export_cannot_call_stale_cached_verification_complete(self):
        original = self.admit()
        self.execute(original)
        self.n.visibility(False, tenant='tenant', target='counter')
        self.assertFalse(self.n.export()['complete'])

    def test_reading_unexecuted_work_does_not_invent_pending_effect(self):
        original = self.admit()
        self.assertEqual(self.n.reconcile(original, worker='worker', epoch=1)['work']['state'], 'ADMITTED')
        self.assertEqual(self.execute(original)['work']['state'], 'VERIFIED')


if __name__ == '__main__':
    unittest.main()
