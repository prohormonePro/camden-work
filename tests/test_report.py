import tempfile,unittest
from pathlib import Path
from camden_work.core import Node

class Reports(unittest.TestCase):
    def test_blocked_report_stands_alone(self):
        with tempfile.TemporaryDirectory() as directory:
            n=Node.initialize(directory)
            g=n.grant(tenant='demo',target='counter')
            w=n.admit(grant=g,tenant='demo',target='counter',delta=2,profile='opaque')
            n.claim('worker',expected_epoch=0)
            n.execute(w,worker='worker',epoch=1)
            n.wait(w)
            report=n.export('blocked')
            body=Path(report['markdown']).read_text(encoding='utf8')
            for expected in ['# blocked.md','## Authority and owner','## Work and effects','## Waits and continuation','## Attempts and evidence','## Finalization at freeze',g,'No background wake is armed','delta 2','UNKNOWN']:
                self.assertIn(expected,body)
            self.assertFalse(report['complete'])

    def test_report_preserves_completed_and_pending_work(self):
        with tempfile.TemporaryDirectory() as directory:
            n=Node.initialize(directory);g=n.grant(tenant='demo',target='counter')
            done=n.admit(grant=g,tenant='demo',target='counter',delta=2)
            pending=n.admit(grant=g,tenant='demo',target='counter',delta=3)
            n.claim('worker',expected_epoch=0);n.execute(done,worker='worker',epoch=1)
            body=Path(n.export('partial')['markdown']).read_text(encoding='utf8')
            for expected in [done,pending,'VERIFIED','ADMITTED','Verified target effects: 1','No remote delivery is established']:
                self.assertIn(expected,body)
