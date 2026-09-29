# Repository verification: specification

Runs the shared local and CI quality gates required by the engineering baseline.

## Public boundary

The [public entry point](verify.py) is authoritative for exported names and signatures.

- python -m tooling.quality.verify is the verification entry point used by make verify.
- Source, dependency, typing, dead-code, coverage and test checks enforce the configured repository rules.

## Required behavior

- Return failure when a mandatory gate fails; do not silently exempt generated or adapter code.
- Restrict source locations and validate module boundaries in addition to style.
- Keep accounting mutation checks and independent coverage thresholds effective.

## Dependencies and ownership

Pinned development tools and the repository location manifest; never imported by production modules.

## Acceptance criteria

- Deliberate boundary, typing, size and coverage violations fail the corresponding gates.
- Local and CI execution use the same verification entry point.

## Shared contracts

- [README](../../README.md)
- [module-boundaries](../../docs/architecture/module-boundaries.md)
