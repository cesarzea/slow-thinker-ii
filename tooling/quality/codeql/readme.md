# CodeQL verification

Runs the pinned Python and JavaScript/TypeScript security-and-quality suites for
current first-party source. Missing tools, incomplete analysis and error/warning
findings fail verification. Notes remain visible in retained SARIF reports.

Use `python -m tooling.quality.codeql`; `make verify` invokes the same command in
local development and CI. See [specification.md](specification.md) for its contract.

Each invocation retains reports and command logs in a fresh directory under
`.local/verification/codeql/reports`. Its disposable source snapshot and databases
are removed on completion or failure. The CLI identifies retained evidence in its
output so findings and incomplete analysis remain inspectable.

Database creation and analysis request two threads and 4096 MB RAM. The complete
JavaScript suite exhausted its 729 MiB Java heap and exited with code 99 under the
initial 2048 MB setting. The larger allocation completed the full local verification run; both suites and all failure criteria remain required.
