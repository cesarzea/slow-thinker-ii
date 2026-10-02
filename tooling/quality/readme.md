# Repository verification

Runs the shared local and CI quality gates required by the engineering baseline.

Use the [public entry point](verify.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

The [CodeQL gate](codeql/readme.md) uses the pinned bundle policy in local runs and
CI. Set `CODEQL_EXECUTABLE` to that bundle's CLI, install it in the documented project
cache, or put it on PATH. The runner fails if the required tool is missing; it does
not download or skip it. Reports and logs stay in ignored local verification data.

Vulture scans production code and tests at the unchanged 60% confidence level.
[Dynamic callback references](dynamic_callbacks.py) identify the two
`HTMLParser.feed` callbacks implemented by the tariff parser. Their inherited
signatures and actual parsing behavior are verified separately. This uses
[Vulture's documented false-positive handling](https://github.com/jendrikseipp/vulture#whitelists);
it adds no file exclusion or general name pattern. Deliberate dead-code violations
remain rejection cases in the quality-gate tests.
