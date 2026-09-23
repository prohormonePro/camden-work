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
