# complete-result.md

All admitted local work verified.

Snapshot Unix time: 1790263419.3756607

## Authority and owner

Node e8e9c1c31226417dbc73f8d4028aa813; worker controller-3; epoch 3; stopped False.

- Grant 24e34e28eb1d4995b61d606233ba4005: synthetic/original; revoked False; expiry 1790267018.680738; effect budget 1.
- Grant 340192b577f544c68b09eea19f02e808: synthetic/z-independent; revoked False; expiry 1790267018.702483; effect budget 1.

## Work and effects

- fc96a8d014d74508835dc0dfd30eaf27: VERIFIED; tenant synthetic; target original; delta 1; profile local-atomic; attempts 1/3; deadline 1790263718.691524; current target check True.
- 258a59dee1254532bb3e232fc9d55f73: VERIFIED; tenant synthetic; target z-independent; delta 1; profile local-atomic; attempts 1/3; deadline 1790263718.7125585; current target check True.

Verified target effects: 2. Stored target records: 2.

## Waits and continuation

No background wake is armed. The operator must invoke the foreground service after the condition changes.

No registered waits at freeze.

## Attempts and evidence

- c5d27f50529644bcbe6e47dd0bf0c080: work fc96a8d014d74508835dc0dfd30eaf27; phase TARGET_COMMITTED; owner epoch 1.
- 09ed4bc120bc4f4c84aaf1d75c1b3c26: work 258a59dee1254532bb3e232fc9d55f73; phase TARGET_COMMITTED; owner epoch 3.

Retained observations: 2; events: 14. Exact evidence remains in the accompanying JSON snapshot.

## Finalization at freeze

This file has not established its own adoption or delivery. The current owner must adopt this exact result, deliver it to the local inbox, then run finalization with fresh target checks. No remote delivery is established.

## Limits

- Local trusted operator and filesystem
- No remote exactly-once guarantee
- Foreground service has no future wake unless invoked

This local export is not a remote delivery receipt.
