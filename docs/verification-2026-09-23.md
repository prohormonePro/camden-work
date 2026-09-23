# Camden Work 0.1.0 verification addendum - September 23, 2026

This addendum refers to release commit `f8ffad19a198915564b9816e156b22b3fd4dddee`. It updates the qualification status described in the original versioned limits document without changing that historical snapshot or replacing release assets.

The public [CI run](https://github.com/prohormonePro/camden-work/actions/runs/35888011009) reports successful Ubuntu and Windows jobs on Python 3.11 and 3.12. These are four configurations, not four independent products or exhaustive platform certification.

The release wheel's SHA-256 is `72313506160671730b68bc18769c3e11ed14cc72bfd7711def62e0db4c1134db`. The source archive's SHA-256 is `f4768001f12d5d9e908da713ead012f39aa65e2f9d4c1d356a02a151ad9bb936`. Verify acquired bytes against the published checksums before installation.

Maintainer observations from September 23: anonymous public downloads matched the release digests; a new Windows Python 3.12 environment installed the public wheel and completed the interruption challenge. Eighteen installed CLI, host and MCP checks passed. They overlap the 84-test suite and are not eighteen additional independently certified mechanisms. The complete challenge has seven predicates. Two real worker subprocess exits were observed.

These maintainer observations supersede the earlier statement that public-download verification was pending. The linked CI supersedes the earlier pending Linux qualification statement within those exact tested configurations. These observations are maintainer reports; the linked CI is independently inspectable public evidence.

The target is synthetic SQLite under a trusted operating-system principal. This is not an exactly-once guarantee for arbitrary remote APIs, a hostile-worker sandbox or a model benchmark. macOS, physical mobile devices and exhaustive assistive-technology coverage are not established here. Desktop/mobile-width browser observations are viewport emulation, not device certification.

The catalog contains 283 mechanisms. Eighteen narrow subcases have mapped implementation/test coverage; a catalog entry is not a prevented failure. Acquisition uses the network. The documented local exercise needs no model account, API key, telemetry, listening port or background service.

See the [quickstart](quickstart.html), [limits](limits.html), [coverage](coverage.json) and [release](https://github.com/prohormonePro/camden-work/releases/tag/v0.1.0).
