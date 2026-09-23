# Security boundaries

Camden Work is a local experimental controller, not an authentication service or hostile-worker sandbox. The operator, Python installation, package, filesystem and OS principal are trusted. A process able to rewrite controller files can bypass the API's checks.

The bundled exercise uses synthetic data. Do not place credentials, production exports, private conversations or customer records in a public issue, test fixture or shared report. Reports contain tenant/target identifiers and retained work evidence. Review their audience before sharing them.

The read-only MCP server opens no network listener and runs no shell commands. Its optional export directory is a deliberate local read grant. Parsed content remains untrusted data. A client must not interpret a catalog trace or imported snapshot as permission to act.

## Stop and revocation

An explicit stop increments no authority and prevents the old worker from acting through the API. A new claim requires the expected stopped epoch. Grant revocation blocks future effects without erasing committed effects. Local cancellation does not establish remote cancellation. Keep unknown outcomes fenced until supported evidence resolves them.

## Storage and resource assumptions

SQLite uses full synchronization and rollback journals. Filesystem and hardware behavior still matter. Database page limits and bounded work, grant, event and export counts limit application growth; they do not reserve disk space or prevent the operating system from exhausting resources. Clock rollback, malicious file edits, loss of both databases and untrusted mounted filesystems are outside the current guarantee.

Do not expose the CLI or Python API as an unauthenticated remote service. A real provider adapter needs its own authorization, isolation, idempotency, evidence and secret-management boundary.

## Reporting a vulnerability

Do not publish exploit details containing secrets or private records. Use the repository's private security reporting feature only if it is actually enabled. Otherwise provide a minimal non-sensitive reproduction through an available maintainer contact. No private contact or response-time commitment is invented by this file.
