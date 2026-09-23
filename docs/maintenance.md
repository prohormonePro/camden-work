# Upgrade, recovery and removal

Stop the local worker before changing its installed package. Preserve the complete workspace, including both SQLite databases and exports, with no process writing it. A copied report is evidence, not a runnable database backup.

Version 0.1.0 uses controller schema 1. Unsupported schema versions are rejected. This release does not implement an arbitrary historical schema migration or a cross-provider restore. Keep the previous environment available until the new version has been checked against an isolated copy. Never downgrade a live database merely to satisfy a tool.

`import-review` accepts a bounded schema-1 export as inert review data. It does not restore grants, owner leases or effects. This prevents an old export from silently resurrecting revoked authority. Resuming a real retained node uses its original durable workspace and current owner transition.

For an interrupted local intent, read current state, stop the old epoch, claim the stopped node and use `recover-local` on the same occurrence. It checks local absence while the old epoch is fenced. The opaque profile has no equivalent remote-quiescence proof and cannot use this route.

An explicit cancellation can satisfy local closeout accounting when the controller verifies its cancellation event and effect absence under the local lock. This does not mark the cancelled outcome successful. An opaque dispatched outcome remains unknown and blocks closeout; cancelling its local record cannot establish remote absence.

If a frozen report is incomplete, preserve its bytes and create a new named report after the work changes. Do not overwrite the old report or treat a queued copy as delivery. A local inbox copy with a lost receipt can be reconciled by exact byte readback. Changed received bytes fail finalization.

Uninstall with the selected virtual environment's `python -m pip uninstall camden-work`. This removes the package, not its workspaces or external credentials. No daemon, scheduled task or global service is installed. Delete an operator-selected synthetic workspace only after accepting the loss of its evidence; no automatic deletion command is provided. Removing files cannot reverse an external effect.
