# CodeQL verification: specification

## Public boundary

[**init**.py](__init__.py) declares `CodeQLFailure`, immutable `AnalysisResult` and
`verify_codeql(root, executable, languages=("python", "javascript"))`. Each result
contains the language, note/warning/error counts and the retained SARIF path.
Failures raise `CodeQLFailure`; the CLI prints a useful error and exits nonzero.
The CLI uses the repository root and both languages, resolving `CODEQL_EXECUTABLE`,
then the project cache `.cache/codeql-bundle/<version>/codeql/codeql`, then PATH.
It never installs tools or silently skips analysis.

## Pinned dependencies

[policy.json](policy.json) is the shared CLI/query-pack version policy. Version
2.27.1 bundles Python queries 1.8.11 and JavaScript queries 2.4.6. Verify the CLI
version, resolve the exact bundled `codeql-suites/<language>-security-and-quality.qls`
files and fail if any is missing. CI initializes this same bundle through the
already SHA-pinned CodeQL action, using the policy version in its release URL.

## Source and execution

Copy current working-tree versions of tracked and non-ignored untracked files
reported by `git ls-files --cached --others --exclude-standard -z`. This must include
unstaged edits. Exclude dependency/build/private directories explicitly, including
`.git`, `.cache`, `.local`, `.venv`, `node_modules`, `site-packages`, `vendor`,
`bower_components`, `__pycache__`, `dist`, `build`, `coverage`, `mutants` and IDE files.
Do not copy credentials, `.env` files or private keys; reject source symlinks.
Use a disposable source/database directory under `.local/verification/codeql`;
retain reports and command logs separately. Clean scratch directories on failure.

Create each database with `--build-mode=none` and bounded threads/RAM; propagate
subprocess failures. Analyze Python and JavaScript against the exact bundled suites
with SARIF 2.1.0 output. No queries, notes or source findings may be suppressed.

## Report contract and completeness

Validate SARIF objects/arrays, tool version, nonempty successful invocations and
known severities (`none`, `note`, `warning`, `error`). Fail on error/warning analysis
notifications. Use a result's explicit severity or its referenced rule's default
severity; fail if a rule or severity is absent/unknown. Retain notes, but fail on
any error/warning result. Do not mistake a CLI exit of zero for a clean report.

For the selected language, read notification descriptors
`py/baseline/expected-extracted-files` / `js/baseline/expected-extracted-files` and
`py/diagnostics/successfully-extracted-files` /
`js/diagnostics/successfully-extracted-files`. Their
`locations[].physicalLocation.artifactLocation.uri` fields are source-relative
paths (an artifact index may reference `run.artifacts` instead). Require every
owned source file of that language to appear in the baseline and successful
extraction set; fail on missing files or malformed evidence. Python owns `.py`;
JavaScript owns `.js`, `.cjs`, `.mjs`, `.ts`, `.tsx`. Reject unsupported/duplicate
languages. Each requested language must have source files.

## Acceptance

- Changed/untracked owned source is analyzed; ignored dependencies/private files
  and prior results cannot influence a passing outcome.
- Missing/wrong tools, missing suites, failed commands, malformed/incomplete SARIF,
  missing extraction evidence and error/warning findings fail. Notes are retained.
- Local and CI run the same module and version policy through `make verify`.
- Public-contract tests use isolated fixtures and simulated CLI responses; a
  separate real-CLI smoke probe demonstrates that a deliberate side effect inside
  an assertion is rejected. No LLM/provider calls are involved.
