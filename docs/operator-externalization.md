# Measuring operator reconstruction

Specification v1, September 24, 2026. The counts below are evaluation fields, not runtime states or a claim of zero-burden autonomy.

## Freeze the boundary before handoff

Declare scenario/source version, target contract, trusted principals, storage, initial obligations, permitted recovery policy, fault schedule, repetitions, deadlines, attempts, expected outcome and delivery boundary. A declared product supervisor may be inside the system under test. Benchmark decisions and launches outside it must be counted.

| Field | Count or record |
|---|---|
| B_e | Distinct avoidable human reconstruction events after handoff: re-explaining intent, locating state, relaying machine errors, recreating authority already retained. |
| D_e | Genuinely necessary new human decisions or authority. Do not count these as avoidable repair. |
| S_e | Setup/configuration effort, code and time where measured. Unknown time stays NOT_MEASURED. |
| A_e | Harness/evaluator assistance after handoff, including replacement launches or supplied missing context. |
| U_e | Unsupported or unexercised stages. Never silently remove them. |

An event records episode/obligation identity, actor, action, authority basis, before/after references, evidence, timestamp or ordering, burden class and disposition. Publish only synthetic data.

## Passing requires useful progress and truthful return

Report safety (no unauthorized/duplicate effect), usefulness (eligible independent work), liveness (within the declared budget), and return fidelity separately. A blocked conflict need not block an unrelated target. No output is not proof of no effect.

Proposed outcome labels: BUSINESS_COMPLETE, VALID_AUTHORITY_STOP, OWNED_BLOCKED, FAILED, UNSUPPORTED. An owned wait is not completed business work. A correct revocation stop is not a completed effect. Every started episode, timeout and missing artifact belongs in the denominator.

## Current local experiment

The [cold-process runner](continuity-gauntlet.md) predeclares two independent increments. Each child discovers the retained work and local takeover policy. It does not receive remembered IDs. The harness launches two or three children per episode; A_e records all of them, including the initial handoff. B_e and D_e are zero only within these synthetic observed episodes. Setup human time is not measured. Automatic restart, background wake, remote effects and new business decisions remain U_e.

This deliberately conservative assistance count prevents a zero-human figure from being sold as autonomous recovery. Four deterministic episodes are not a production failure-rate estimate or an adoption metric.

## Business-result fidelity fixture

A proposed larger fixture has three obligations: publish a local artifact and complete two declared local verification/distribution simulations. If only publication is verified, return the remaining obligations rather than “Done”; do not republish the artifact. This semantic fixture is SPECIFICATION_ONLY. The executed benchmark uses two counters, not a publishing integration. Changed intent requires an explicit contract revision, not retrospective narrowing.
