import tempfile
import unittest
from pathlib import Path
from camden_work.core import Node, Denied


class Finalization(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.n = Node.initialize(self.tmp.name)
        self.g = self.n.grant(tenant='demo', target='counter')
        self.w = self.n.admit(grant=self.g, tenant='demo', target='counter', delta=1)
        self.n.claim('worker', expected_epoch=0)
        self.n.execute(self.w, worker='worker', epoch=1)
        self.n.export('result')

    def test_export_alone_cannot_finalize(self):
        with self.assertRaisesRegex(Denied, 'ADOPTION_REQUIRED'):
            self.n.finalize('result', worker='worker', epoch=1)

    def test_adoption_requires_actual_local_delivery(self):
        self.n.adopt_result('result', worker='worker', epoch=1)
        with self.assertRaisesRegex(Denied, 'DELIVERY_REQUIRED'):
            self.n.finalize('result', worker='worker', epoch=1)

    def test_actual_inbox_receipt_is_idempotent_and_local(self):
        self.n.adopt_result('result', worker='worker', epoch=1)
        first = self.n.deliver_local('result', worker='worker', epoch=1)
        again = self.n.deliver_local('result', worker='worker', epoch=1)
        self.assertEqual(first['artifact_sha256'], again['artifact_sha256'])
        self.assertTrue(Path(first['received_path']).is_file())
        result = self.n.finalize('result', worker='worker', epoch=1)
        self.assertTrue(result['ready'])
        self.assertEqual(result['delivery_scope'], 'LOCAL_NODE_INBOX')
        self.assertFalse(result['remote_delivery'])

    def test_new_obligation_invalidates_frozen_result(self):
        self.n.adopt_result('result', worker='worker', epoch=1)
        self.n.deliver_local('result', worker='worker', epoch=1)
        self.n.admit(grant=self.g, tenant='demo', target='counter', delta=1)
        with self.assertRaisesRegex(Denied, 'RESULT_SCOPE_STALE'):
            self.n.finalize('result', worker='worker', epoch=1)

    def test_altered_inbox_cannot_satisfy_delivery(self):
        self.n.adopt_result('result', worker='worker', epoch=1)
        delivery = self.n.deliver_local('result', worker='worker', epoch=1)
        Path(delivery['received_path']).write_text('changed', encoding='utf8')
        with self.assertRaisesRegex(Denied, 'DELIVERY_BYTES_CHANGED'):
            self.n.finalize('result', worker='worker', epoch=1)

    def test_lost_target_visibility_invalidates_return(self):
        self.n.adopt_result('result', worker='worker', epoch=1)
        self.n.deliver_local('result', worker='worker', epoch=1)
        self.n.visibility(False, tenant='demo', target='counter')
        with self.assertRaisesRegex(Denied, 'CURRENT_WORK_UNVERIFIED'):
            self.n.finalize('result', worker='worker', epoch=1)

    def test_copied_file_without_receipt_is_reconciled(self):
        self.n.adopt_result('result', worker='worker', epoch=1)
        inbox=Path(self.tmp.name)/'inbox';inbox.mkdir()
        body=(Path(self.tmp.name)/'exports'/'result.md').read_bytes()
        (inbox/'result.md').write_bytes(body)
        self.n.deliver_local('result', worker='worker', epoch=1)
        self.assertEqual((inbox/'result.md').read_bytes(),body)
        self.assertTrue(self.n.finalize('result', worker='worker', epoch=1)['ready'])

    def test_pending_copy_does_not_become_a_partial_received_file(self):
        self.n.adopt_result('result', worker='worker', epoch=1)
        inbox=Path(self.tmp.name)/'inbox';inbox.mkdir()
        (inbox/'result.pending').write_bytes(b'partial interrupted staging')
        self.n.deliver_local('result', worker='worker', epoch=1)
        self.assertFalse((inbox/'result.pending').exists())
        self.assertTrue(self.n.finalize('result', worker='worker', epoch=1)['ready'])


if __name__ == '__main__':
    unittest.main()
