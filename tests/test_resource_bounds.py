import tempfile
import unittest
from unittest.mock import patch
from camden_work.core import Node, Denied


class ResourceBounds(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.n=Node.initialize(self.tmp.name)

    def test_new_grants_cannot_escape_node_limit(self):
        with patch('camden_work.core.MAX_GRANTS',2):
            self.n.grant(tenant='x',target='a')
            self.n.grant(tenant='x',target='b')
            with self.assertRaisesRegex(Denied,'NODE_GRANT_LIMIT'):
                self.n.grant(tenant='x',target='c')

    def test_new_grant_cannot_reset_node_work_limit(self):
        with patch('camden_work.core.MAX_WORKS',1):
            first=self.n.grant(tenant='x',target='a')
            second=self.n.grant(tenant='x',target='b')
            self.n.admit(grant=first,tenant='x',target='a',delta=1)
            with self.assertRaisesRegex(Denied,'NODE_WORK_LIMIT'):
                self.n.admit(grant=second,tenant='x',target='b',delta=1)

    def test_log_budget_does_not_disable_stop_or_revocation(self):
        g=self.n.grant(tenant='x',target='a')
        self.n.claim('w',expected_epoch=0)
        with patch('camden_work.core.MAX_EVENTS',2):
            with self.assertRaisesRegex(Denied,'EVENT_BUDGET'):
                self.n.visibility(False,tenant='x',target='a')
            self.n.stop(expected_epoch=1)
            self.n.revoke(g)
            count=len(self.n.status()['events'])
            self.n.stop(expected_epoch=1);self.n.revoke(g)
            self.assertEqual(len(self.n.status()['events']),count)
            self.assertTrue(self.n.status()['owner']['stopped'])

    def test_exports_are_bounded_without_overwriting(self):
        with patch('camden_work.core.MAX_EXPORTS',1):
            self.n.export('first')
            with self.assertRaisesRegex(Denied,'EXPORT_BUDGET'):
                self.n.export('second')


if __name__=='__main__':unittest.main()
