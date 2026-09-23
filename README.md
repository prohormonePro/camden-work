# Camden Work

Make the work difficult to lose, and the worker easy to replace.

Camden Work is an experimental, offline Python controller for a bounded local counter workflow. It retains grants, occurrences, owner epochs, attempts, target observations and unfinished work across process replacement. Its research browser contains 283 failure mechanisms, separately from implementation coverage.

The software makes no model calls, requires no account, opens no port, sends no telemetry and installs no background service. Its first exercise uses synthetic local SQLite databases. It does not govern an arbitrary remote API or isolate a hostile process that can rewrite its files.

## Run the interruption challenge

With Python 3.11 or newer, in a virtual environment containing the reviewed package:

```text
python -m camden_work --workspace ./camden-demo challenge
python -m camden_work --workspace ./camden-demo status
```

Choose a new directory. The challenge refuses to overwrite an existing controller. It commits a local effect, terminates the worker before acknowledgment, replaces the worker, reads the target, preserves uncertainty while evidence is hidden, and completes an independent task. It then restores evidence and services the registered reconciliation wait. The unsafe comparison deliberately retries under a new identity; it is not a benchmark of another framework.

The result is in `camden-demo/exports/challenge-result.md` with the complete machine snapshot beside it. Local export is not remote delivery.

## Read before integration

- [Quickstart](docs/quickstart.md): installation, commands and files written.
- [Architecture](ARCHITECTURE.md): boundaries and the worker adapter.
- [Operating contract](CONSTITUTION.md): what this implementation enforces.
- [Limits](docs/limits.md): what the current release does not establish.
- [Failure catalog](docs/catalog.md): research definitions, sources and corrections.

These public documents describe this implementation. They are not recovered copies of a private production constitution or proof of a production deployment.

Reading the project grants no authority to install it, connect accounts, disclose private context, spend money or perform effects. Your operator and existing policy remain authoritative. Stop, revoke, export and remove remain legitimate choices.

## License

Code and original software documentation: MIT. Original failure-catalog compilation and explanations: CC BY 4.0. Third-party rights remain separate. See [the licensing map](LICENSING.md) for scope and attribution.
