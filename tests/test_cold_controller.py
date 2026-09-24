import json,tempfile,unittest
from pathlib import Path
from benchmarks.continuity import run

class ColdControllerTests(unittest.TestCase):
    def test_cold_process_and_recovery_of_recovery_reach_local_return(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=run(Path(tmp)/'run',repetitions=1)
            self.assertEqual(result['started_episodes'],2)
            self.assertEqual(result['completed_episodes'],2)
            self.assertEqual([e['process_exits'] for e in result['episodes']],[[72,0],[72,73,0]])
            self.assertEqual([e['A_e'] for e in result['episodes']],[2,3])
            self.assertTrue(all(not e['closure']['remote_delivery'] for e in result['episodes']))
    def test_existing_run_refused_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            sentinel=Path(tmp)/'sentinel';sentinel.write_text('preserve')
            with self.assertRaises(FileExistsError):run(tmp)
            self.assertEqual(sentinel.read_text(),'preserve')
