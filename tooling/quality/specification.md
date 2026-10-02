# Repository verification: specification

Runs the shared local and CI quality gates required by the engineering baseline.

## Public boundary

The [public entry point](verify.py) is authoritative for exported names and signatures.

- python -m tooling.quality.verify is the verification entry point used by make verify.
- Source, dependency, typing, dead-code, coverage and test checks enforce the configured repository rules.
- The [CodeQL gate](codeql/specification.md) is a mandatory command in the same runner, before functional tests.

## Required behavior

- Return failure when a mandatory gate fails; do not silently exempt generated or adapter code.
- Restrict source locations and validate module boundaries in addition to style.
- S03 exposes `application.library` to adapters and bootstrap as an exact public
  entry point. Its descendants remain protected, including from sibling
  application modules. Explicit exceptions must never cover private targets.
- Keep accounting mutation checks and independent coverage thresholds effective.
- Standard-library dynamic callbacks may be documented with exact checked symbol
  references, following Vulture's false-positive procedure. The tariff parser's
  two HTMLParser callbacks have override signature checking and functional tests.
  Do not exclude files, add name patterns or change the confidence threshold.
- Run CodeQL locally and in CI with the shared bundle policy; missing tools, incomplete analysis or warning/error findings must stop the runner.

## Dependencies and ownership

Pinned development tools and the repository location manifest; never imported by production modules.

## Acceptance criteria

- Deliberate boundary, typing, size and coverage violations fail the corresponding gates.
- Local and CI execution use the same verification entry point.

## Shared contracts

- [README](../../README.md)
- [module-boundaries](../../docs/architecture/module-boundaries.md)
