# complete-result.md

All admitted local work verified.

Snapshot Unix time: 1790263417.7403235

## Authority and owner

Node 8855468a247944a9aff9cd316d7b8b73; worker controller-2; epoch 2; stopped False.

- Grant c488c735ed1a4678a797e4442ad91420: synthetic/original; revoked False; expiry 1790267017.195329; effect budget 1.
- Grant 919a2529ba984e77a5e9932806069212: synthetic/z-independent; revoked False; expiry 1790267017.2179117; effect budget 1.

## Work and effects

- 0eecc93529864fc88e8d2b548b43f128: VERIFIED; tenant synthetic; target original; delta 1; profile local-atomic; attempts 1/3; deadline 1790263717.2053292; current target check True.
- a9d746f705a1411b9d0b6e775a1ef9ae: VERIFIED; tenant synthetic; target z-independent; delta 1; profile local-atomic; attempts 1/3; deadline 1790263717.227133; current target check True.

Verified target effects: 2. Stored target records: 2.

## Waits and continuation

No background wake is armed. The operator must invoke the foreground service after the condition changes.

No registered waits at freeze.

## Attempts and evidence

- c2f973651d2a44a79adc86f809eccd42: work 0eecc93529864fc88e8d2b548b43f128; phase TARGET_COMMITTED; owner epoch 1.
- d3b34a90c3894361a13e6f2f36243115: work a9d746f705a1411b9d0b6e775a1ef9ae; phase TARGET_COMMITTED; owner epoch 2.

Retained observations: 2; events: 12. Exact evidence remains in the accompanying JSON snapshot.

## Finalization at freeze

This file has not established its own adoption or delivery. The current owner must adopt this exact result, deliver it to the local inbox, then run finalization with fresh target checks. No remote delivery is established.

## Limits

- Local trusted operator and filesystem
- No remote exactly-once guarantee
- Foreground service has no future wake unless invoked

This local export is not a remote delivery receipt.
