# Related work and boundaries

Checked September 23, 2026. This is a documentation comparison, not a performance benchmark or compatibility certificate. Package versions below were observed in each package's PyPI metadata; rolling documentation is not necessarily an immutable specification for that package version. None of these frameworks was installed or executed in this evaluation.

| Project and observed Python package version | Documented persistence boundary | What this comparison does not establish |
|---|---|---|
| Temporal, `temporalio` 1.33.0 | Deterministic workflow replay; nondeterministic calls, including LLM calls, belong in Activities | An Activity result does not by itself prove every downstream business effect. Provider-specific contracts still matter. |
| DBOS, `dbos` 3.0.0 | Workflow recovery uses completed steps; nondeterministic operations belong in steps; workflow IDs support idempotency | Workflow identity alone is not a proof about an arbitrary external service's transaction boundary. |
| Restate, `restate-sdk` 1.0.5 | Execution log retains wrapped operation results; durable steps support configurable retry bounds | A documented durable step is not evidence that Camden implemented the same system or any stronger guarantee. |
| LangGraph, `langgraph` 1.2.12 | Checkpointers retain thread state; stores retain application-defined data across threads; persistence supports human intervention | The persistence page is not a certification of a tool's external effects or a particular deployment's durable storage configuration. |
| AutoGen AgentChat, `autogen-agentchat` 0.7.5 | `save_state` and `load_state` retain agent/team state; custom agents define their state behavior | Saved conversation state is not a general effect ledger, nor proof of provider cancellation or result delivery. |
| CrewAI, `crewai` 1.15.22 | Versioned Flows documentation describes class/method persistence and distinguishes same-identity resume from state fork | Restoring a state snapshot does not independently establish what a remote target did. |
| Camden Work, 0.1.0 candidate | Local SQLite occurrence, target and owner records; explicit foreground servicing and local report finalization | No production connector, general workflow engine, remote scheduler or universal effect guarantee is supplied. |

Sources: [Temporal workflow definition](https://docs.temporal.io/workflow-definition), [DBOS workflows](https://docs.dbos.dev/python/tutorials/workflow-tutorial), [Restate durable steps](https://docs.restate.dev/develop/python/durable-steps), [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [AutoGen state](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/state.html), [CrewAI 1.15.22 Flows](https://docs.crewai.com/v1.15.22/en/concepts/flows).

The external-effect qualifications in the final column are evaluation boundaries, not claims that the other projects lack safeguards. Approval, connector, deployment and failure semantics were not exhaustively audited here. Consult the actual version and target contract before integration.

Replay determinism does not categorically exclude LLM work. Temporal and Restate explicitly describe separating nondeterministic operations from replayed control. Existing systems deserve credit for durable workflow primitives; Camden's synthetic challenge is not an industry comparison.


## September 24 review: concrete overlap

The package-version observations above remain dated September 23 and have not been revalidated as latest versions. Camden Work 0.1.0 is now released; “candidate” in the earlier comparison describes that historical review. The following source-only review is dated September 24, 2026. No external implementation was installed or executed. Cross-system composition is NOT_ASSESSED.

| Source | Reviewed overlap | Still to establish in a matched evaluation |
|---|---|---|
| [VAIS Boundary README](https://github.com/stratomarco/vais-boundary/blob/main/README.md) | Trusted immutable contracts, exact-action approvals, provenance/information flow, independent effect verification and indeterminate MCP outcomes. | Composition with durable ownership, recovery and complete return. It is more than a permission check. |
| [GATE specification](https://deterministicagents.ai/spec) | Tool/memory gateways, versioned contracts, audit/replay and human-review obligations. C20 covers final-output classification and review before delivery. | Actual enforcing implementation and interrupted-obligation behavior. This is a rolling specification, not conformance evidence; section/footer revision labels differ. |
| [Guardian limitations](https://github.com/sylvesterkaczmarek/guardian-agent-runtime/blob/main/docs/limitations.md) | Reference-monitor experiments; reference implementation explicitly describes process-local nonce, revocation and budget state and disclaims restart-safe replay protection. | Persistent extensions if used. Camden's local retained ownership is a narrow implementation contrast, not general superiority. |
| [Temporal execution](https://docs.temporal.io/workflow-execution) | Workflow state recovery through event-history replay. | Application authority, ambiguous effects and return criteria under the same target contract. |
| [Restate steps](https://docs.restate.dev/develop/python/durable-steps) | Journaled operation results and retry count/time limits. | Selected target's uncertain-effect and duplicate-prevention semantics. |
| [DBOS workflows](https://docs.dbos.dev/python/tutorials/workflow-tutorial) | Recovery from completed steps and durable workflow identity. | External effects inside retried steps and complete business verification. |
| [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Checkpointers and stores; restart persistence depends on backend configuration. | Configured storage, side effects and recovery policy, not an in-memory strawman. |

These are documentation/README observations, not measurements. Rolling sources are not pinned implementation versions; retrieval date is the binding available here. A missing homepage statement is not evidence of a missing capability. A [fair experiment](positioning.md) must allow recommended durable configurations and publish unsuccessful episodes too.
