# complete-result.md

All admitted local work verified.

Snapshot Unix time: 1790263418.4972808

## Authority and owner

Node 8162951fff0b4a709bd29c1b7c7623ed; worker controller-2; epoch 2; stopped False.

- Grant 44f76f905fea45dbad9a1acae4a1bae8: synthetic/original; revoked False; expiry 1790267017.9302115; effect budget 1.
- Grant 694113eb7b3a447f8aaf9b22e31307a3: synthetic/z-independent; revoked False; expiry 1790267017.9593356; effect budget 1.

## Work and effects

- 1b3a3c14159d47deab8b4e5e597231ab: VERIFIED; tenant synthetic; target original; delta 1; profile local-atomic; attempts 1/3; deadline 1790263717.9494812; current target check True.
- 2f4d1d7dd56842bdb447b479973918a3: VERIFIED; tenant synthetic; target z-independent; delta 1; profile local-atomic; attempts 1/3; deadline 1790263717.9698155; current target check True.

Verified target effects: 2. Stored target records: 2.

## Waits and continuation

No background wake is armed. The operator must invoke the foreground service after the condition changes.

No registered waits at freeze.

## Attempts and evidence

- 729362fcd2804cd6b21c41dcd4d3b602: work 1b3a3c14159d47deab8b4e5e597231ab; phase TARGET_COMMITTED; owner epoch 1.
- edc71fc9e5ca4475b858445089df050e: work 2f4d1d7dd56842bdb447b479973918a3; phase TARGET_COMMITTED; owner epoch 2.

Retained observations: 2; events: 12. Exact evidence remains in the accompanying JSON snapshot.

## Finalization at freeze

This file has not established its own adoption or delivery. The current owner must adopt this exact result, deliver it to the local inbox, then run finalization with fresh target checks. No remote delivery is established.

## Limits

- Local trusted operator and filesystem
- No remote exactly-once guarantee
- Foreground service has no future wake unless invoked

This local export is not a remote delivery receipt.
