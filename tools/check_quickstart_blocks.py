"""Execute the exact documented setup block in disposable directories.

Downloads only the fixed public 0.1.0 wheel and checksum file. No credentials,
source-package install, production workspace or cleanup of existing paths.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request

root = Path(__file__).resolve().parents[1]
windows = os.name == 'nt'
language = 'powershell' if windows else 'sh'
document = (root / 'docs/quickstart.md').read_text(encoding='utf8')
blocks = re.findall(r'```' + language + r'\n(.*?)```', document, re.S)
if len(blocks) != 1:
    raise SystemExit('Expected one complete setup block for this platform')
block = blocks[0]
parent = Path(tempfile.mkdtemp(prefix='camden-docs-check-'))
downloads = parent / 'downloads'
downloads.mkdir()
wheel_name = 'camden_work-0.1.0-py3-none-any.whl'
expected = '72313506160671730b68bc18769c3e11ed14cc72bfd7711def62e0db4c1134db'
for name in (wheel_name, 'SHA256SUMS.txt'):
    with urllib.request.urlopen('https://github.com/prohormonePro/camden-work/releases/download/v0.1.0/' + name, timeout=60) as response:
        (downloads / name).write_bytes(response.read())
if hashlib.sha256((downloads / wheel_name).read_bytes()).hexdigest() != expected:
    raise SystemExit('Public wheel digest mismatch')
rows = []
for case in ('positive', 'wrong_checksum', 'missing_wheel', 'existing_workspace', 'existing_venv', 'installation_failure'):
    target = parent / case
    target.mkdir()
    shutil.copyfile(downloads / 'SHA256SUMS.txt', target / 'SHA256SUMS.txt')
    if case != 'missing_wheel':
        shutil.copyfile(downloads / wheel_name, target / wheel_name)
    if case == 'wrong_checksum':
        (target / wheel_name).write_bytes(b'wrong synthetic bytes')
    marker = None
    if case in ('existing_workspace', 'existing_venv'):
        occupied = target / ('camden-demo' if case == 'existing_workspace' else '.venv')
        occupied.mkdir()
        marker = occupied / 'preserve.txt'
        marker.write_text('preserve', encoding='utf8')
    allowed = {'SYSTEMROOT', 'WINDIR', 'PATH', 'PATHEXT', 'TEMP', 'TMP', 'COMSPEC', 'LOCALAPPDATA', 'USERPROFILE', 'HOME', 'LANG'}
    env = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    env.update(PYTHONDONTWRITEBYTECODE='1', PIP_NO_INDEX='1', PIP_DISABLE_PIP_VERSION_CHECK='1')
    if case == 'installation_failure':
        env['PIP_REQUIRE_HASHES'] = '1'
    command = ['pwsh', '-NoProfile', '-NonInteractive', '-Command', block] if windows else ['sh', '-c', block]
    result = subprocess.run(command, cwd=target, env=env, capture_output=True, timeout=150)
    (target / 'output.txt').write_bytes(result.stdout + b'\n' + result.stderr)
    passed = result.returncode == 0 if case == 'positive' else result.returncode != 0
    if case == 'positive':
        evidence = json.loads((target / 'camden-demo/challenge-evidence.json').read_text(encoding='utf8'))
        passed = passed and all(evidence['checks'].values())
    else:
        if case != 'existing_workspace':
            passed = passed and not (target / 'camden-demo').exists()
        if case not in ('existing_venv', 'installation_failure'):
            passed = passed and not (target / '.venv').exists()
        if marker:
            passed = passed and marker.read_text() == 'preserve'
        if case == 'installation_failure':
            passed = passed and not list((target / '.venv').glob('**/site-packages/camden_work*'))
    rows.append({'case': case, 'exit': result.returncode, 'passed': passed})
    print(json.dumps(rows[-1]), flush=True)
print(json.dumps({'platform': language, 'block_sha256': hashlib.sha256(block.encode()).hexdigest(), 'all_passed': all(x['passed'] for x in rows)}))
if not all(x['passed'] for x in rows):
    raise SystemExit(1)
