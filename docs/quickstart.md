# The worker died. The write survived. Should the replacement retry?

Camden Work is an experimental Python/SQLite exercise for that gap. The replacement inspects the target before acting; when evidence is hidden, the conflicting retry stays blocked while unrelated authorized work must still finish.

Make the work difficult to lose, and the worker easy to replace.

## Run the interruption challenge

Use Python 3.11 or newer and a new disposable parent directory. Do not reuse an existing `.venv` or `camden-demo`. No model account or API key is needed. Downloading uses the network; the installed local exercise does not.

Download the [0.1.0 wheel](https://github.com/prohormonePro/camden-work/releases/download/v0.1.0/camden_work-0.1.0-py3-none-any.whl) and [SHA256SUMS.txt](https://github.com/prohormonePro/camden-work/releases/download/v0.1.0/SHA256SUMS.txt) from the [release](https://github.com/prohormonePro/camden-work/releases/tag/v0.1.0). Save both in that new directory. Do not install if the digest differs.

Windows PowerShell, in that directory:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    python -c "import hashlib,pathlib,sys; w=pathlib.Path('camden_work-0.1.0-py3-none-any.whl'); expected='72313506160671730b68bc18769c3e11ed14cc72bfd7711def62e0db4c1134db'; occupied=[p for p in (pathlib.Path('.venv'),pathlib.Path('camden-demo')) if p.exists() or p.is_symlink()]; occupied and sys.exit('Refusing existing .venv or camden-demo'); sys.version_info < (3,11) and sys.exit('Python 3.11 or newer required'); entries=[line.split() for line in pathlib.Path('SHA256SUMS.txt').read_text(encoding='utf8').splitlines()]; matches=[parts[0] for parts in entries if len(parts)==2 and parts[1].lstrip('*')==w.name]; matches != [expected] and sys.exit('Published checksum does not match pinned release'); actual=hashlib.sha256(w.read_bytes()).hexdigest(); actual != expected and sys.exit('Wheel checksum mismatch'); print('Verified wheel SHA-256:',actual)"
    if ($LASTEXITCODE -ne 0) { throw 'Prerequisite or checksum check failed' }
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed' }
    .venv\Scripts\python.exe -m pip install --no-index --no-deps ./camden_work-0.1.0-py3-none-any.whl
    if ($LASTEXITCODE -ne 0) { throw 'Installation failed' }
    .venv\Scripts\python.exe -m camden_work --workspace ./camden-demo challenge
    if ($LASTEXITCODE -ne 0) { throw 'Challenge failed; preserve the output' }
    .venv\Scripts\python.exe -m camden_work --workspace ./camden-demo status
    if ($LASTEXITCODE -ne 0) { throw 'Status failed' }
}
```

Linux, in a new directory containing the same two downloads:

```sh
(
    set -eu
    python3 -c "import hashlib,pathlib,sys; w=pathlib.Path('camden_work-0.1.0-py3-none-any.whl'); expected='72313506160671730b68bc18769c3e11ed14cc72bfd7711def62e0db4c1134db'; occupied=[p for p in (pathlib.Path('.venv'),pathlib.Path('camden-demo')) if p.exists() or p.is_symlink()]; occupied and sys.exit('Refusing existing .venv or camden-demo'); sys.version_info < (3,11) and sys.exit('Python 3.11 or newer required'); entries=[line.split() for line in pathlib.Path('SHA256SUMS.txt').read_text(encoding='utf8').splitlines()]; matches=[parts[0] for parts in entries if len(parts)==2 and parts[1].lstrip('*')==w.name]; matches != [expected] and sys.exit('Published checksum does not match pinned release'); actual=hashlib.sha256(w.read_bytes()).hexdigest(); actual != expected and sys.exit('Wheel checksum mismatch'); print('Verified wheel SHA-256:',actual)"
    python3 -m venv .venv
    .venv/bin/python -m pip install --no-index --no-deps ./camden_work-0.1.0-py3-none-any.whl
    .venv/bin/python -m camden_work --workspace ./camden-demo challenge
    .venv/bin/python -m camden_work --workspace ./camden-demo status
)
```

Linux needs Python's `venv` support available. Copy the complete block, including its wrapper. It stops on a failed check or command. No activation or PowerShell execution-policy change is required. The checksum comparison remains active under Python optimization. If a command fails, preserve the output and use a different new directory after correcting the cause. Do not delete an existing workspace just to retry.

See the [dated verification addendum](verification-2026-09-23.html) for the exact observed platform coverage. macOS is not claimed tested.

## Inspect the result

The new Windows Python 3.12 trial on September 23 returned all seven predicates as `true`:

```text
crash_after_target_commit
one_original_effect
unknown_observed
retry_fenced
independent_task_verified
registered_wait_serviced
unsafe_baseline_duplicates
crash_exit_codes: [72, 72]
target_effect_count: 3
```

This is a shortened text excerpt of actual output, not a terminal recording or a timing claim. The three target rows include other authorized work. The invariant is one **original logical effect**, not one row in the entire target database. The unsafe baseline intentionally creates duplicate effects under fresh identities; it is not an industry-framework benchmark.

Start with `camden-demo/challenge-evidence.json` and `camden-demo/exports/challenge-result.md`. The workspace also contains `controller.sqlite3`, `target.sqlite3` and `unsafe-baseline.sqlite3`. SQLite may create transaction journals. Inspect the original effect, the intentionally unsafe retry, and whether the independent job finished.

The target and unsafe baseline have different schemas. Do not compare their binary files or query a nonexistent `occurrences` table. Use the [read-only inspection example](inspect_challenge.py), saved beside the downloads. It uses SQLite `mode=ro` so a misspelled path cannot silently create a database.

Windows: `.venv\Scripts\python.exe inspect_challenge.py ./camden-demo`

Linux: `.venv/bin/python inspect_challenge.py ./camden-demo`

## Tell us the first unclear step

Use [GitHub Issues](https://github.com/prohormonePro/camden-work/issues). A version/platform, what you tried and a short sanitized excerpt are enough. Successful runs with confusing output are useful too. Do not submit credentials, production databases or private conversations. There is no advertised Discussions destination or invented security inbox.

## Limits and deeper inspection

This trusted-local synthetic target does not provide exactly-once guarantees across arbitrary remote APIs or isolate hostile same-principal code. Read [limits](limits.html), [coverage](coverage.json), architecture and the optional read-only MCP documentation before proposing an integration. The catalog has 283 mechanisms; eighteen narrow subcases have mapped tests, not eighteen fully prevented mechanisms.


## Use the controller directly

Start with `init`. Create a `grant` for a tenant and target. `admit` prints the new work ID. Claim the stopped node with `claim --worker NAME --expected-epoch 0`. Use the returned epoch with `execute`, `reconcile` or `verify`. Each subcommand exposes its exact arguments through `--help`.

`stop --expected-epoch N` fences the current worker. A subsequent `claim` must name that same expected epoch and receives a new epoch. `revoke --grant ID` prevents future effects under that grant. It does not pretend an already committed effect disappeared.

After an interrupted local dispatch, `recover-local --work ID --worker NAME --epoch N` can enable the same occurrence again only when its earlier epoch is fenced and the local transaction proves no effect committed. It preserves attempts, budget and deadline. It refuses the opaque profile. `cancel --work ID` fences an uncommitted local operation; committed effects remain recorded, and unknown remote effects remain unknown.

`wait --work ID` registers an unknown effect for a bounded readback. `service --worker NAME --epoch N` actually services due waits once. There is no background wake after it exits. `export --name NAME` freezes a local Markdown report and JSON snapshot without overwriting an earlier report. `import-review --source FILE` imports only inert review evidence.

For completed work, use `adopt-result --name NAME --worker NAME --epoch N`, then `deliver-local` with the same arguments, then `finalize`. Adoption checks current target evidence and the frozen report. Delivery copies the report into this node's `inbox` and reads back its bytes. Finalization requires both records and current work coverage. This is an explicit local inbox exercise, not email, Telegram, or proof that a person read the file. New work or unavailable target evidence invalidates the earlier completion claim.

## Optional read-only MCP

Windows: `.venv\Scripts\python.exe -m camden_work.mcp`

Linux: `.venv/bin/python -m camden_work.mcp`

Configure this command as a local stdio server only if your operator permits it. By default it exposes the packaged research catalog. Export inspection requires the explicit `--exports` directory option. It has no effect-execution tool, remote transport, telemetry or account connector. A client must initialize the protocol before calling tools.

## Stop and remove

Stop the node before removing its application environment. Uninstalling the Python package does not delete the workspace or revoke credentials belonging to another system. Preserve the exported evidence first. The current release has no automatic workspace deletion command; deleting the operator-selected synthetic workspace is an intentional loss of its retained history. No remote effects are undone by removing local files.


## Challenge versus continuity research

The installed challenge retains its parent recovery sequence and exports its result. It does not exercise the entire adoption/delivery chain. [Evidence](evidence.md) distinguishes its seven predicates from separate finalization tests and the source-tree [cold-process experiment](continuity-gauntlet.md). That experiment counts harness launches and does not install a supervisor. The existing acquisition, grants, stop/revoke, MCP and removal instructions above remain the released interface.
