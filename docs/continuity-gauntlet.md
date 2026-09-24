# Continuity gauntlet

Specification v1 and separate source-tree experiment, September 24, 2026. The released seven-predicate challenge is unchanged. This is not a new installed CLI or automatic background supervisor.

## Run the bounded experiment

From a reviewed source checkout with Python 3.11 or newer, using its isolated interpreter:

```text
python -B -m benchmarks.continuity ../new-continuity-run
```

The output parent must not exist. The runner refuses reuse. It uses only synthetic local files, no credentials/network/model. It records a plan before starting, every episode before faults, cumulative results after each episode, and before/after controller snapshots. Allow up to 15 seconds per child; each admitted obligation has a 300-second deadline and three-attempt ceiling. Two repetitions of each scenario are declared, with deterministic fault locations and variable UUIDs.

| Scenario | Fault schedule | Expected exit codes | Required outcome |
|---|---|---|---|
| Cold controller | Controller exits after original target commit | 72, 0 | Clean successor discovers both obligations, reconciles original, executes independent work, adopts/delivers/finalizes local result. |
| Recovery of recovery | Same fault, then recovery controller exits after reconciliation | 72, 73, 0 | Another cold successor preserves IDs, attempts, deadlines and effects through complete local return. |

The controller receives a workspace and fault phase only. Durable policy explicitly permits serial stop/claim and names the result. The harness verifies predecessor exit before replacement. Launches are A_e assistance, not a product-owned wake. This model does not establish concurrent controller safety or recovery from arbitrary export/adoption fault points.

## Larger matrix and proof gaps

| Failure | Existing exact evidence | Larger status |
|---|---|---|
| Lost acknowledgment | `tests/test_core.py::test_real_lost_ack_and_replacement` and release challenge | Narrow local coverage. |
| Hidden evidence plus independent progress | `test_unknown_independent_progress_and_servicing` | Current challenge parent supplies transitions. |
| Cold controller / second recovery crash | `tests/test_cold_controller.py::test_cold_process_and_recovery_of_recovery_reach_local_return` | Executable separate benchmark; harness-assisted. |
| Stale epoch | `test_wrong_owner_version`; benchmark stale-owner rejection | Local API boundary only. |
| Revocation / identical legitimate requests | `test_revocation`, `test_distinct_identical_requests` | Separate tests, not all joined into benchmark episode. |
| Stale compensation | `tests/test_continuity.py::test_conditional_compensation_preserves_intervening_change` | Narrow inverse-counter primitive. |
| Wait budget / controller loss / future wake | `test_wait_budget_not_reset` | Budget mapped; autonomous wake UNSUPPORTED_THIS_RELEASE. |
| Export without adoption / missing delivery | `tests/test_finalization.py::test_export_alone_cannot_finalize`, `test_adoption_requires_actual_local_delivery` | Dedicated negative tests; benchmark joins successful closure. |
| Lost delivery acknowledgment / altered bytes | `test_copied_file_without_receipt_is_reconciled`, `test_altered_inbox_cannot_satisfy_delivery` | Local inbox only. |
| Enlarged scope / lost visibility | `test_new_obligation_invalidates_frozen_result`, `test_lost_target_visibility_invalidates_return` | Separate adverse tests, no cached-success shortcut. |
| New business decision / general repair planning | No public implementation | SPECIFICATION_ONLY. |
| Arbitrary remote ambiguous effect | No public adapter | UNSUPPORTED_THIS_RELEASE. |

The benchmark verifies safety, independent completion, deadline/budget preservation, one attempt per obligation, stale-owner denial and exact local return bytes. [Evidence](evidence.md) links the actual four-episode manifest. Separate tests are not represented as a single larger end-to-end run. Competitor evaluation remains NOT_ASSESSED.
