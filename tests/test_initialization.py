import sqlite3,tempfile,unittest
from pathlib import Path
from camden_work.core import Node

class Initialization(unittest.TestCase):
    def test_existing_target_is_not_modified_or_adopted(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'target.sqlite3'
            db=sqlite3.connect(p);db.execute('CREATE TABLE unrelated(value TEXT)');db.commit();db.close()
            before=p.read_bytes()
            with self.assertRaises(FileExistsError):Node.initialize(tmp)
            self.assertEqual(p.read_bytes(),before)
            self.assertFalse((Path(tmp)/'controller.sqlite3').exists())
