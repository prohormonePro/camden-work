# Tools and integration

Camden Work 0.1.0 exposes a local CLI, a Python API and a read-only MCP stdio server. None authenticates a remote operator or connects an external account. The operator's process and filesystem are trusted.

## CLI

Every controller command requires `--workspace DIRECTORY`. `init` creates a new node and refuses an existing controller. IDs and owner epochs come from command results, not from examples in this document.

| Command | Effect or result |
|---|---|
| `grant` | Record bounded tenant/target authority with expiry and an effect budget |
| `admit` | Reserve a new occurrence under that authority |
| `claim` | Acquire a stopped node at the expected owner epoch |
| `execute` | Commit one synthetic counter effect, or retain uncertainty for the opaque simulation |
| `reconcile`, `verify` | Read exact target evidence; unavailable evidence is not proof of absence |
| `stop`, `revoke`, `cancel` | Fence a worker, revoke future grant use, or account for cancellation |
| `recover-local` | Recover an uncommitted local intent only after the old epoch is fenced |
| `wait`, `service` | Register an unknown outcome, then service due readback once in the foreground |
| `status`, `export` | Inspect state or freeze a cumulative Markdown and JSON account |
| `adopt-result`, `deliver-local`, `finalize` | Check the frozen result, copy it to the node inbox, then recheck completion |
| `import-review` | Retain an inert snapshot without restoring its authority or replaying effects |

Use `python -m camden_work --workspace DIRECTORY COMMAND --help` for arguments. A nonzero exit is a failure, not a completed operation. Read state before retrying an interrupted mutation. The `--crash` options intentionally terminate the process and belong only in synthetic workspaces.

## Worker contract

The Python API is `camden_work.core.Node`. A worker receives a work ID and current owner epoch from the trusted controller. It cannot claim a live owner, extend a revoked grant, turn missing acknowledgment into a new occurrence, or finalize an unverified target through the API.

The same OS principal can edit the database or source directly. These API checks are not a security boundary against that principal. Integrating a hostile worker requires external process isolation and a mediated effect service, neither supplied here.

An adapter for a real provider must define its actual principal, grant, input provenance, occurrence identity, deduplication retention, target evidence, cancellation behavior and delivery contract. Host routing acceptance is not typed-input acceptance or execution. A tool result or quoted instruction is data until the host's authenticated authority writer admits it. This release does not supply a provider-specific typed-input authenticator.

### Typed local host admission

`camden_work.host.LocalInputHost` is configured by the trusted operator process with an existing grant, principal, channel, tenant and target. Its `receive_user(event_id, payload)` and `receive_machine(event_id, payload)` methods preserve distinct origin types. The host must choose the method from its actual receiving route, never from text inside the payload. The payload accepts only an integer `delta`; it cannot choose a grant or assert an origin.

```python
from camden_work.core import Node
from camden_work.host import LocalInputHost

node = Node("my-synthetic-workspace")  # already initialized by its operator
# grant_id is an existing operator-created grant, not a model-generated value.
host = LocalInputHost(node, principal="operator", channel="local-host",
                      grant=grant_id, tenant="demo", target="counter")
work_id = host.receive_machine("received-item-1", {"delta": 1})
```

The input identity and occurrence are recorded in one local transaction. Repeating the same principal/channel/event identity with identical parameters returns the existing occurrence; changing its payload or type rejects. Identical payloads on genuinely different event identities remain distinct work. Admission does not execute the target. Current grant checks still apply.

This preserves a trusted local host's assertion. It does not authenticate a Telegram, Codex or other remote message. A provider integration must authenticate the actual receiving item before selecting this route. Same-principal Python code can call these APIs or alter storage, as explained above. The isolated host tests do not establish a live provider connection or a hardened separation between operator and worker processes.

The package includes `data/local-input.schema.json`, its synthetic example, and `data/snapshot.schema.json`, accessible through `importlib.resources.files("camden_work")`. These describe the input and snapshot structural envelope. The snapshot schema intentionally does not certify the semantics of every row body. Runtime authority, budgets and target verification still apply; parsing a conforming snapshot never makes it runnable.

## MCP stdio

Start `python -m camden_work.mcp` only through an authorized local client. Protocol version: `2025-11-25`. Initialize with client information and capabilities, inspect the server's negotiated version, then send `notifications/initialized`. Unsupported requested versions receive the server's supported version; an incompatible client should disconnect.

The finite tools are `catalog_search`, `catalog_entry` and `inspect_export`. Search supports text, family, R/E/D basis, outcome, offset and a limit of 1 through 25. An alias lookup returns both requested and canonical IDs. Tool results are research or parsed data, not execution permission or independent verification.

Export inspection requires `--exports DIRECTORY`, accepts a simple filename stem, rejects path traversal and symlinks, and limits reads to 1 MiB. Requests are bounded to 16 KiB. No shell, network, sampling, elicitation, mutation or arbitrary filesystem tool is exposed. Static documentation is not a remote MCP endpoint.

See the [MCP lifecycle specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle).
