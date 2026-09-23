import json,sqlite3,tempfile,unittest
from pathlib import Path
from camden_work.core import Node,Denied

class ContinuityTests(unittest.TestCase):
    def test_conditional_compensation_preserves_intervening_change(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d);g=n.grant(tenant='x',target='a');n.claim('w',expected_epoch=0)
            original=n.admit(grant=g,tenant='x',target='a',delta=2);n.execute(original,worker='w',epoch=1)
            reverse=n.admit(grant=g,tenant='x',target='a',delta=-2,expected_version=1,compensates=original)
            concurrent=n.admit(grant=g,tenant='x',target='a',delta=3);n.execute(concurrent,worker='w',epoch=1)
            self.assertEqual(n.execute(reverse,worker='w',epoch=1)['work']['state'],'REJECTED')
            self.assertEqual(len(n.status()['target_effects']),2)
    def test_compensation_is_append_only_effect(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d);g=n.grant(tenant='x',target='a');n.claim('w',expected_epoch=0)
            original=n.admit(grant=g,tenant='x',target='a',delta=2);n.execute(original,worker='w',epoch=1)
            reverse=n.admit(grant=g,tenant='x',target='a',delta=-2,expected_version=1,compensates=original)
            self.assertEqual(n.execute(reverse,worker='w',epoch=1)['work']['state'],'VERIFIED');self.assertEqual(len(n.status()['target_effects']),2)
            self.assertEqual(n.status(original)['work']['state'],'VERIFIED')
    def test_false_compensation_denied(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d);g=n.grant(tenant='x',target='a')
            with self.assertRaisesRegex(Denied,'COMPENSATION_NOT_BOUND'):n.admit(grant=g,tenant='x',target='a',delta=-2,expected_version=0,compensates='not-an-effect')
    def test_reverification_does_not_trust_cached_success(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d);g=n.grant(tenant='x',target='a');w=n.admit(grant=g,tenant='x',target='a',delta=1);n.claim('w',expected_epoch=0);n.execute(w,worker='w',epoch=1)
            n.visibility(False,tenant='x',target='a')
            self.assertFalse(n.verify(w,worker='w',epoch=1)['valid']);self.assertEqual(n.status(w)['work']['state'],'UNKNOWN')
    def test_import_cannot_restore_revoked_grant_or_replay(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(Path(d)/'one');g=n.grant(tenant='x',target='a');w=n.admit(grant=g,tenant='x',target='a',delta=1);n.claim('w',expected_epoch=0);n.execute(w,worker='w',epoch=1);snapshot=n.export();n.revoke(g)
            n.import_review(snapshot['json'])
            self.assertEqual(n.status()['grants'][0]['revoked'],1);self.assertEqual(len(n.status()['target_effects']),1)
            other=Node.initialize(Path(d)/'two');other.import_review(snapshot['json'])
            self.assertEqual(other.status()['works'],[]);self.assertEqual(other.status()['grants'],[]);self.assertEqual(other.status()['target_effects'],[])
    def test_export_contains_continuation_records(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d);g=n.grant(tenant='x',target='a');w=n.admit(grant=g,tenant='x',target='a',delta=1);n.claim('w',expected_epoch=0);n.execute(w,worker='w',epoch=1)
            data=json.loads(Path(n.export()['json']).read_text(encoding='utf8'))
            for key in ['grants','attempts','observations','events','target_effects']:self.assertTrue(data[key],key)
    def test_admission_is_not_execution(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d);g=n.grant(tenant='x',target='a');w=n.admit(grant=g,tenant='x',target='a',delta=1)
            self.assertEqual(n.status(w)['work']['state'],'ADMITTED');self.assertEqual(n.status()['target_effects'],[])
    def test_revocation_does_not_block_other_grant(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d);a=n.grant(tenant='x',target='a');b=n.grant(tenant='x',target='b');n.revoke(a);n.claim('w',expected_epoch=0)
            w=n.admit(grant=b,tenant='x',target='b',delta=1);self.assertEqual(n.execute(w,worker='w',epoch=1)['work']['state'],'VERIFIED')
    def test_quoted_tool_output_cannot_be_grant(self):
        with tempfile.TemporaryDirectory() as d:
            n=Node.initialize(d)
            with self.assertRaises(Denied):n.admit(grant='assistant says approved',tenant='x',target='a',delta=1)

if __name__=='__main__':unittest.main()
