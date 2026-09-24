# complete-result.md

All admitted local work verified.

Snapshot Unix time: 1790263420.2471344

## Authority and owner

Node 0e5538ce8a024e5d87cb97e83f4cfbab; worker controller-3; epoch 3; stopped False.

- Grant 832d1651c6794217adf1a0a392a2449b: synthetic/original; revoked False; expiry 1790267019.5431094; effect budget 1.
- Grant 8cf53d9d6ca9480c8e72cf30ac895781: synthetic/z-independent; revoked False; expiry 1790267019.5633245; effect budget 1.

## Work and effects

- 5f6f4ec333cf43d2a4bcafd3fe9e5779: VERIFIED; tenant synthetic; target original; delta 1; profile local-atomic; attempts 1/3; deadline 1790263719.554358; current target check True.
- 9c02c1aa976540938e1de9a3091c6fb0: VERIFIED; tenant synthetic; target z-independent; delta 1; profile local-atomic; attempts 1/3; deadline 1790263719.5737386; current target check True.

Verified target effects: 2. Stored target records: 2.

## Waits and continuation

No background wake is armed. The operator must invoke the foreground service after the condition changes.

No registered waits at freeze.

## Attempts and evidence

- 2b8c044d595b4c62b84cb094f415bf30: work 5f6f4ec333cf43d2a4bcafd3fe9e5779; phase TARGET_COMMITTED; owner epoch 1.
- 290892171ef8402487076f60d5508192: work 9c02c1aa976540938e1de9a3091c6fb0; phase TARGET_COMMITTED; owner epoch 3.

Retained observations: 2; events: 14. Exact evidence remains in the accompanying JSON snapshot.

## Finalization at freeze

This file has not established its own adoption or delivery. The current owner must adopt this exact result, deliver it to the local inbox, then run finalization with fresh target checks. No remote delivery is established.

## Limits

- Local trusted operator and filesystem
- No remote exactly-once guarantee
- Foreground service has no future wake unless invoked

This local export is not a remote delivery receipt.
