# Architecture

This is an implementation-specific public edition, not a reconstruction of unavailable historical architecture drafts.

## One controlled local effect boundary

`Node` opens a controller database and attaches a separate synthetic target database. Local writes use SQLite transactions, rollback journals and synchronous FULL. A target increment and its occurrence marker commit together. The acknowledgment is a later observation, so an actual process exit between commit and acknowledgment leaves recoverable uncertainty.

The operator grants a tenant, target, maximum increment, maximum admitted effects and expiry. Admission reserves the aggregate effect budget, including unknown work. Identical legitimate requests receive different occurrence IDs. Retries of a retained occurrence keep its identity and payload binding.

An exclusive owner consists of a worker label and monotonically increasing epoch. Replacement requires an explicit stop and the expected current epoch. The effect transaction checks current ownership, current grant, deadline, payload identity and dependency evidence again. A stopped predecessor cannot use its old epoch through this API.

## Worker adapter

An operator-controlled worker can call the Python API or the CLI. The operator creates the grant and admits the work; the worker receives only the retained work ID and its claimed epoch. It calls `execute`, then inspects the structured result. On uncertain outcome it calls `reconcile`, never a fresh `admit` masquerading as retry. `verify` obtains a fresh target observation. A successor uses existing records and an explicitly transferred epoch.

These are API roles, not operating-system isolation. A process with unrestricted access to the same account, program and ledger can call operator methods or alter files. Do not give an untrusted worker that access and call it a sandbox. No production credentials or remote effect adapters are included.

## Effects and observations

Admission, dispatch intent, target commit and verification are distinct records. A missing acknowledgment does not mean no effect. An unavailable target keeps a possibly dispatched occurrence unknown and fences conflicting work on that tenant and target. Other granted targets remain eligible. Reconciliation is read-only against the synthetic target and remains possible after a grant is revoked.

Compensation is a separately admitted, version-conditioned inverse increment bound to an observed original effect. It retains both effects and refuses a second compensation reservation. It does not erase history or undo consequences outside this synthetic counter. A rejected condition remains a rejected obligation requiring an operator disposition.

## Continuation and retention

Waits retain their original deadline and attempt budget. `service` is an explicit, bounded foreground reconciliation pass. Registration alone does not arm a background wake. The status and exported result state that limitation. No scheduled worker is installed implicitly.

State remains in the chosen workspace until the operator removes it. `import-review` retains a bounded snapshot as inert evidence, without reviving grants, executing effects or changing current revocations. A runnable migration to an unrelated target is not implemented.

Frozen exports bind their Markdown and structured snapshot. Parent adoption checks those identities against the complete current work set and fresh local target evidence. The local delivery adapter stages, syncs and renames bytes into the node's explicit inbox, then records a separate readback receipt. A crash after copying can be reconciled without copying again. Finalization rechecks adoption, delivery and current target evidence. This local chain does not attest to human attention or any remote provider.

## Research interface

The opt-in local MCP server uses stdio and exposes catalog search, entry lookup and explicitly scoped export inspection. It cannot dispatch effects, execute a shell, fetch URLs or obtain credentials. It implements the documented subset of the pinned MCP protocol; it is not an A2A service or a hosted public execution endpoint.


## The complete obligation and the public boundary

Desired outcome → scoped grant → admitted occurrence → owner/epoch → attempt → target effect or uncertainty → reconciliation → eligible work → fresh verification → adoption → local delivery/readback → finalization.

This chain branches. Fresh visibility can invalidate cached success. A hash binds bytes, not business meaning. The public semantic contract is an increment on a synthetic target; natural-language intent compilation and general repair planning are outside it.

| Stage | Actual record / method | Boundary |
|---|---|---|
| Authority | `grants`, `grant`, `revoke`, `valid_grant` | Trusted local operator; no OS sandbox. |
| Admission | `works`, payload hash, dependencies, `admit` | Legitimate identical requests have separate IDs; attempts do not. |
| Ownership | `owner`, `stop`, `claim`, `check_owner` | Explicit transfer, no autonomous takeover service. |
| Effect and uncertainty | `attempts`, target `effects`, `execute`, `reconcile` | Atomic local occurrence marker; unavailable evidence stays UNKNOWN. |
| Repair | `recover_local`, version-conditioned compensation | Local fence/lock proof; no arbitrary-provider retry authorization. |
| Continuation | `waits`, `wait`, `service` | Preserved budget/deadline, foreground caller required. |
| Verification | `observations`, `verify` | Exact local predicate, not universal semantic correctness. |
| Return | `result_frozen`, `parent_adoption`, `local_delivery`, `local_ready` events | Complete current scope and exact inbox bytes, not human reading. |
| Learning and meaning | No general public runtime counterpart | Research catalog and private-system objectives are not implementation proof. |

`challenge.py` holds IDs and recovery order in its parent. The separate `benchmarks/continuity.py` controller receives only a workspace and declared fault phase, reads durable obligations/policy, and completes both tasks before result closure. The harness still supplies process launches. See [the fault matrix](continuity-gauntlet.md) for that assistance and unexercised stages.
