"""Exercise the documented operator interface through real process boundaries."""
import json,subprocess,sys,tempfile,unittest
from pathlib import Path

class CLIJourney(unittest.TestCase):
    def test_commands_preserve_one_occurrence_across_crash_and_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'node'
            def run(*args,code=0):
                p=subprocess.run([sys.executable,'-B','-m','camden_work','--workspace',str(root),*map(str,args)],capture_output=True,text=True,timeout=15)
                self.assertEqual(p.returncode,code,p.stderr)
                return json.loads(p.stdout) if p.stdout.strip() else None
            run('init')
            g=run('grant','--tenant','demo','--target','counter','--max-effects',4)['grant']
            w=run('admit','--grant',g,'--tenant','demo','--target','counter','--delta',2)['work']
            run('claim','--worker','first','--expected-epoch',0)
            run('execute','--work',w,'--worker','first','--epoch',1,'--crash','after-intent',code=71)
            run('stop','--expected-epoch',1)
            run('claim','--worker','second','--expected-epoch',1)
            run('recover-local','--work',w,'--worker','second','--epoch',2)
            run('execute','--work',w,'--worker','second','--epoch',2)
            run('visibility','unavailable','--tenant','demo','--target','counter')
            self.assertEqual(run('reconcile','--work',w,'--worker','second','--epoch',2)['work']['state'],'UNKNOWN')
            run('wait','--work',w,'--attempts',2)
            run('visibility','available','--tenant','demo','--target','counter')
            run('service','--worker','second','--epoch',2)
            run('verify','--work',w,'--worker','second','--epoch',2)
            cancelled=run('admit','--grant',g,'--tenant','demo','--target','counter','--delta',1)['work']
            run('cancel','--work',cancelled)
            run('revoke','--grant',g)
            state=run('status')
            self.assertEqual(len(state['target_effects']),1)
            run('export','--name','journey')
            run('adopt-result','--name','journey','--worker','second','--epoch',2)
            run('deliver-local','--name','journey','--worker','second','--epoch',2)
            self.assertTrue(run('finalize','--name','journey','--worker','second','--epoch',2)['ready'])
            candidates=list((root/'exports').glob('*.json'))
            self.assertEqual(len(candidates),1)
            run('import-review','--source',candidates[0])
            self.assertEqual(len(run('status')['target_effects']),1)
