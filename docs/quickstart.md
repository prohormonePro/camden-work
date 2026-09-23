# Run the interruption challenge

Use a virtual environment and a new, nonproduction workspace. No account or API key is required. The application uses no network. Installing build tools from an online package index would be a separate network operation; the released wheel can be installed offline.

## Install a reviewed wheel

Download the [version 0.1.0 wheel](https://github.com/prohormonePro/camden-work/releases/download/v0.1.0/camden_work-0.1.0-py3-none-any.whl) and [SHA-256 checksums](https://github.com/prohormonePro/camden-work/releases/download/v0.1.0/SHA256SUMS.txt) from the [release page](https://github.com/prohormonePro/camden-work/releases/tag/v0.1.0). Verify the wheel against the published checksum before installing. Keep the wheel in your working directory for the commands below.

Create a virtual environment with your Python installation:

```text
python -m venv .venv
```

Windows:

```text
.venv\Scripts\python.exe -m pip install --no-index --no-deps ./camden_work-0.1.0-py3-none-any.whl
.venv\Scripts\python.exe -m camden_work --workspace ./camden-demo challenge
```

Linux, once qualified for the released artifact:

```text
.venv/bin/python -m pip install --no-index --no-deps ./camden_work-0.1.0-py3-none-any.whl
.venv/bin/python -m camden_work --workspace ./camden-demo challenge
```

Check the release's actual platform evidence before treating a platform as supported. These commands do not fetch or execute a remote installation script.

## Inspect what happened

```text
python -m camden_work --workspace ./camden-demo status
```

Use the virtual environment's Python, or activate that environment first. The challenge writes `controller.sqlite3`, `target.sqlite3`, `unsafe-baseline.sqlite3`, `challenge-evidence.json` and an `exports` directory inside the selected workspace. SQLite may create journal files during transactions. It writes no application data elsewhere and opens no listening port.

The challenge executes two real subprocess exits after target commit. It retains one original effect, rejects a conflicting retry, completes an independent effect, and later reconciles the unavailable target. Check every returned predicate, the process exit codes, target rows and report. A nonzero command exit is not success.

## Use the controller directly

Start with `init`. Create a `grant` for a tenant and target. `admit` prints the new work ID. Claim the stopped node with `claim --worker NAME --expected-epoch 0`. Use the returned epoch with `execute`, `reconcile` or `verify`. Each subcommand exposes its exact arguments through `--help`.

`stop --expected-epoch N` fences the current worker. A subsequent `claim` must name that same expected epoch and receives a new epoch. `revoke --grant ID` prevents future effects under that grant. It does not pretend an already committed effect disappeared.

After an interrupted local dispatch, `recover-local --work ID --worker NAME --epoch N` can enable the same occurrence again only when its earlier epoch is fenced and the local transaction proves no effect committed. It preserves attempts, budget and deadline. It refuses the opaque profile. `cancel --work ID` fences an uncommitted local operation; committed effects remain recorded, and unknown remote effects remain unknown.

`wait --work ID` registers an unknown effect for a bounded readback. `service --worker NAME --epoch N` actually services due waits once. There is no background wake after it exits. `export --name NAME` freezes a local Markdown report and JSON snapshot without overwriting an earlier report. `import-review --source FILE` imports only inert review evidence.

For completed work, use `adopt-result --name NAME --worker NAME --epoch N`, then `deliver-local` with the same arguments, then `finalize`. Adoption checks current target evidence and the frozen report. Delivery copies the report into this node's `inbox` and reads back its bytes. Finalization requires both records and current work coverage. This is an explicit local inbox exercise, not email, Telegram, or proof that a person read the file. New work or unavailable target evidence invalidates the earlier completion claim.

## Optional read-only MCP

```text
python -m camden_work.mcp
```

Configure this command as a local stdio server only if your operator permits it. By default it exposes the packaged research catalog. Export inspection requires the explicit `--exports` directory option. It has no effect-execution tool, remote transport, telemetry or account connector. A client must initialize the protocol before calling tools.

## Stop and remove

Stop the node before removing its application environment. Uninstalling the Python package does not delete the workspace or revoke credentials belonging to another system. Preserve the exported evidence first. The current release has no automatic workspace deletion command; deleting the operator-selected synthetic workspace is an intentional loss of its retained history. No remote effects are undone by removing local files.
