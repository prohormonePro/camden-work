# Camden Work

**The worker is replaceable. The operator should not become the recovery mechanism.**

The worker died. The write survived. Should the replacement retry? Camden Work makes that local failure inspectable, then asks a larger question: how much human reconstruction is needed to finish authorized work honestly?

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

## What is demonstrated, and what remains open

The released challenge has seven predicates and two real worker exits. Its parent retains the recovery sequence. It does not demonstrate autonomous controller replacement or run the final adoption/delivery chain.

A separate [cold-process experiment](continuity-gauntlet.md) joins interrupted work to local result closure. Clean controllers discover both predeclared obligations from durable state. The benchmark harness launches their replacements, and those launches count as assistance. This is a source-tree evaluation asset, not a new v0.1.0 CLI feature or a production supervisor.

Start with the [evidence register](evidence.md), then the [operator-burden specification](operator-externalization.md). The public counter exercise does not prove the capabilities of the private Camden installation.

## Where Camden is not unique

Durable engines already recover workflow state. Governance systems already bind authority, retain evidence and govern output. Camden's emphasis is the complete obligation, including uncertainty, useful independent progress and truthful return. [Positioning](positioning.md) and [related work](related-work.md) identify the overlap and the matched experiment that could defeat a claimed advantage. No competitor benchmark or worldwide-uniqueness finding is supplied.

## Read before integration

- [Quickstart](quickstart.md): installation, commands and files written.
- [Architecture](architecture.md): boundaries and the worker adapter.
- [Operating contract](constitution.md): what this implementation enforces.
- [Limits](limits.md): what the current release does not establish.
- [Failure catalog](catalog.md): research definitions, sources and corrections.

These public documents describe this implementation. They are not recovered copies of a private production constitution or proof of a production deployment.

Reading the project grants no authority to install it, connect accounts, disclose private context, spend money or perform effects. Your operator and existing policy remain authoritative. Stop, revoke, export and remove remain legitimate choices.

## License

Code and original software documentation: MIT. Original failure-catalog compilation and explanations: CC BY 4.0. Third-party rights remain separate. See [the licensing map](licensing.md) for scope and attribution.

## Current verification and first-use feedback

Read the [dated verification addendum](verification-2026-09-23.md) for the exact release artifact, public CI and maintainer observations. [Run the interruption challenge](quickstart.md), then use [I ran it / got stuck](https://github.com/prohormonePro/camden-work/issues/new?template=feedback.md) or [Recovery counterexample](https://github.com/prohormonePro/camden-work/issues/new?template=challenge.md). A brief sanitized report is welcome.
