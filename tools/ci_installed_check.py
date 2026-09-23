"""Build locally, run from a clean environment, preserve workspace on uninstall.

Requires the declared build tool already installed. No network, secrets,
production paths or service registration. All application effects are temporary.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile

root=Path(__file__).resolve().parents[1]
env={k:v for k,v in os.environ.items() if k.upper() in ('SYSTEMROOT','WINDIR','PATH','TEMP','TMP','TMPDIR','COMSPEC','PATHEXT','HOME')}
env.update(PYTHONNOUSERSITE='1',PYTHONIOENCODING='utf-8',PIP_NO_INDEX='1',PIP_DISABLE_PIP_VERSION_CHECK='1')
def run(args,cwd):
    subprocess.run([str(x) for x in args],cwd=cwd,env=env,check=True,timeout=90)

with tempfile.TemporaryDirectory(prefix='camden-ci-') as directory:
    stage=Path(directory);wheels=stage/'wheels';wheels.mkdir()
    run([sys.executable,'-B','-m','pip','wheel','--no-index','--no-deps','--no-build-isolation','--wheel-dir',wheels,root],stage)
    wheel=next(wheels.glob('camden_work-*.whl'))
    run([sys.executable,'-B','-m','venv',stage/'venv'],stage)
    py=stage/'venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    run([py,'-B','-m','pip','install','--no-index','--no-deps',wheel],stage)
    run([py,'-B','-m','camden_work','--workspace',stage/'exercise','challenge'],stage)
    state=stage/'exercise/controller.sqlite3';before=hashlib.sha256(state.read_bytes()).hexdigest()
    run([py,'-B','-m','pip','uninstall','-y','camden-work'],stage)
    absent=subprocess.run([str(py),'-B','-c','import camden_work'],cwd=stage,env=env,capture_output=True,timeout=10)
    assert absent.returncode!=0 and b'ModuleNotFoundError' in absent.stderr
    assert hashlib.sha256(state.read_bytes()).hexdigest()==before
    print(json.dumps({'installed_challenge':'passed','uninstall_preserved_workspace':True,'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),'python':sys.version,'platform':sys.platform,'remote_effects':False}))
