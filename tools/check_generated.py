from pathlib import Path
import hashlib,subprocess,sys
R=Path(__file__).resolve().parents[1]
def snapshot():return {p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'docs').rglob('*') if p.is_file()}
before=snapshot()
subprocess.run([sys.executable,'-B',str(R/'tools/build_docs.py'),'--base','https://prohormonepro.github.io/camden-work/'],check=True)
if before!=snapshot():raise SystemExit('GENERATED_DOCUMENTATION_DRIFT')
subprocess.run([sys.executable,'-B',str(R/'tools/check_docs.py')],check=True)
