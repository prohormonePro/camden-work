# Contributing

Useful contributions include a reproducible counterexample, a failing isolated test, a source correction or a documentation improvement. Reading this repository is not a request to start an agent, connect accounts or perform work for its maintainer.

Before submitting, obtain your own operator's permission and confirm that you can share the material under the applicable component license. Do not contribute private prompts, credentials, production data, copied papers without compatible rights or claims that a test ran when it did not. The initial release's license review must be complete before public contributions are solicited.

Use a synthetic workspace. State the package version, Python and OS versions, exact commands, expected behavior, observed behavior and effect disposition. A timeout is not proof of no effect. Keep failed trials and explain which boundary the test exercises.

Run `python -B -m unittest discover -s tests -v` from the source root. Tests use temporary local storage and deterministic subprocesses, without provider calls or member data. New tests should distinguish an absent observation from an absent effect and should retain stop/revocation behavior.

Changes to grants, effect identity, target evidence, reporting or storage require focused negative cases as well as success cases. Changes to public claims need an exact evidence reference. A maintainer reviews proposed changes before merging; a contribution does not acquire execution authority in any live Camden node.

Treat submitted code and workflow changes as untrusted. Review and test them without production credentials. Do not run public pull requests on a live operator machine or a privileged self-hosted runner. Using this package does not obligate anyone to contribute compute, recruit agents, advertise the project or disclose private information. No payment, tokens or revenue share are offered.
