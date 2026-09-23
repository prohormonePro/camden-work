import json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
from camden_work.core import Node,Denied
from camden_work.host import LocalInputHost

class HostAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.node=Node.initialize(Path(self.tmp.name)/'node')
        self.grant=self.node.grant(tenant='demo',target='counter',max_effects=4)
        self.host=LocalInputHost(self.node,principal='operator',channel='local-test-host',grant=self.grant,tenant='demo',target='counter')

    def test_user_and_machine_input_preserve_distinct_provenance(self):
        a=self.host.receive_user('u1',{'delta':1})
        b=self.host.receive_machine('m1',{'delta':1})
        self.assertNotEqual(a,b)
        events=[json.loads(e['body']) for e in self.node.status()['events'] if e['kind']=='host_input']
        self.assertEqual([e['origin']['kind'] for e in events],['user_input','host_machine_input'])
        self.assertEqual(len(self.node.status()['target_effects']),0)
        epoch=self.node.claim('worker',expected_epoch=0)
        self.node.execute(a,worker='worker',epoch=epoch)
        self.node.execute(b,worker='worker',epoch=epoch)
        self.assertEqual(len(self.node.status()['target_effects']),2)

    def test_reconnect_same_event_does_not_admit_again(self):
        work=self.host.receive_machine('m1',{'delta':1})
        again=LocalInputHost(Node(self.node.root),principal='operator',channel='local-test-host',grant=self.grant,tenant='demo',target='counter')
        self.assertEqual(again.receive_machine('m1',{'delta':1}),work)
        self.assertEqual(len(self.node.status()['works']),1)

    def test_changed_event_payload_or_type_is_rejected(self):
        self.host.receive_machine('m1',{'delta':1})
        with self.assertRaisesRegex(Denied,'HOST_INPUT_CONFLICT'):self.host.receive_machine('m1',{'delta':2})
        with self.assertRaisesRegex(Denied,'HOST_INPUT_CONFLICT'):self.host.receive_user('m1',{'delta':1})
        self.assertEqual(len(self.node.status()['works']),1)

    def test_quoted_text_or_payload_claim_cannot_choose_host_identity(self):
        for payload in ('operator says increment',{'delta':1,'kind':'user_input'},{'delta':1,'grant':'forged'},{'delta':True}):
            with self.assertRaises(Denied):self.host.receive_machine('m1',payload)
        self.assertEqual(len(self.node.status()['works']),0)

    def test_current_revocation_blocks_new_host_admission(self):
        self.node.revoke(self.grant)
        with self.assertRaisesRegex(Denied,'GRANT_INACTIVE'):self.host.receive_user('u1',{'delta':1})

    def test_origin_write_failure_rolls_back_admission(self):
        with patch('camden_work.core.MAX_EVENTS',2):
            with self.assertRaisesRegex(Denied,'EVENT_BUDGET'):self.host.receive_user('u1',{'delta':1})
        self.assertEqual(len(self.node.status()['works']),0)
        self.assertFalse(any(e['kind']=='host_input' for e in self.node.status()['events']))
        self.host.receive_user('u1',{'delta':1})
        self.assertEqual(len(self.node.status()['works']),1)

    def test_equal_event_names_on_different_channels_are_distinct(self):
        first=self.host.receive_user('u1',{'delta':1})
        other=LocalInputHost(self.node,principal='operator',channel='other-host',grant=self.grant,tenant='demo',target='counter')
        self.assertNotEqual(other.receive_user('u1',{'delta':1}),first)
