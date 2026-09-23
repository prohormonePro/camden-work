"""Read only: python inspect_challenge.py ./camden-demo"""
from pathlib import Path
import json
import sqlite3
import sys

workspace = Path(sys.argv[1] if len(sys.argv) > 1 else './camden-demo').resolve()
evidence = json.loads((workspace / 'challenge-evidence.json').read_text())
print('Predicates:', json.dumps(evidence['checks'], sort_keys=True))
for name, query in [
    ('target.sqlite3', 'SELECT id, tenant, target, delta FROM effects ORDER BY target'),
    ('unsafe-baseline.sqlite3', 'SELECT id, amount FROM effects ORDER BY id'),
]:
    connection = sqlite3.connect((workspace / name).as_uri() + '?mode=ro', uri=True)
    try:
        print(name, json.dumps(connection.execute(query).fetchall()))
    finally:
        connection.close()
print('Compare the demo/counter original effect with the two unsafe baseline rows; other target rows are separate authorized work.')
