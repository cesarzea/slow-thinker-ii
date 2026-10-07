# Repository verification

Runs the shared local and CI quality gates required by the engineering baseline.

Use the [public entry point](verify.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

The [CodeQL gate](codeql/readme.md) uses the pinned bundle policy in local runs and
CI. Set `CODEQL_EXECUTABLE` to that bundle's CLI, install it in the documented project
cache, or put it on PATH. The runner fails if the required tool is missing; it does
not download or skip it. Reports and logs stay in ignored local verification data.

Before any command, the runner also checks that every maintained Markdown document is
listed in the [documentation index](../../docs/README.md) and that links between
documents resolve.
