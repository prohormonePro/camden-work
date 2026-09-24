from pathlib import Path
import hashlib,subprocess,sys,json,difflib
R=Path(__file__).resolve().parents[1]
def snapshot():return {p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'docs').rglob('*') if p.is_file()}
before=snapshot()
original={name:(R/name).read_bytes() for name in before}
subprocess.run([sys.executable,'-B',str(R/'tools/build_docs.py'),'--base','https://prohormonepro.github.io/camden-work/'],check=True)
after=snapshot()
if before!=after:
    changed=[name for name in sorted(set(before)|set(after)) if before.get(name)!=after.get(name)]
    print(json.dumps({'generated_drift_files':changed,'before':{n:before.get(n) for n in changed},'after':{n:after.get(n) for n in changed}}),flush=True)
    for name in changed:
        left=original.get(name,b'').decode('utf8','replace').splitlines(True);right=(R/name).read_text(encoding='utf8').splitlines(True) if (R/name).exists() else []
        print(''.join(difflib.unified_diff(left,right,fromfile=name+' before',tofile=name+' generated'))[:4000],flush=True)
    raise SystemExit('GENERATED_DOCUMENTATION_DRIFT')
subprocess.run([sys.executable,'-B',str(R/'tools/check_docs.py')],check=True)
