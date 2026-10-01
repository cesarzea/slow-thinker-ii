# CodeQL verification

Runs the pinned Python and JavaScript/TypeScript `security-and-quality` suites for
first-party source. `make verify` invokes the same gate locally and in CI.
Missing tools, incomplete analysis and error or warning findings fail verification.
Notes remain visible in retained SARIF reports.

## Installation

Install the official [CodeQL bundle](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-the-command-line/set-up-codeql-cli)
for your platform at the version specified in [policy.json](policy.json). Use the
bundle, which includes the required query packs, rather than a standalone CLI.
The gate validates both the CLI and bundled queries.

Set `CODEQL_EXECUTABLE` to the absolute path of its `codeql` executable, or put the
executable on `PATH`. The supported project-cache location is
`.cache/codeql-bundle/<version>/codeql/codeql`.

When using that cache, create `.cache/codeql-bundle/package.json` with:

```json
{"private": true, "type": "commonjs"}
```

This keeps the repository's ES-module setting from affecting CodeQL's Node tools.
The gate does not download tools or skip analysis when prerequisites are missing.

## Run and inspect

Run `make verify` for complete verification. To run this gate on its own, use:

```sh
uv run --locked python -m tooling.quality.codeql
```

Each invocation retains SARIF reports and command logs in a fresh directory under
`.local/verification/codeql/reports`. The output identifies that directory.
Disposable source snapshots and databases are removed on completion or failure.
Database creation and analysis request two threads and 4096 MB of RAM.

CI supplies the same policy version through the SHA-pinned CodeQL action.
The independent remote CodeQL matrix also remains required.
See [specification.md](specification.md) for the gate's contract and failure rules.
