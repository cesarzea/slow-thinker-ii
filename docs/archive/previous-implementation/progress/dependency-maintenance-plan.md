# Dependency maintenance — October 2026

| Document control | Value                                             |
| ---------------- | ------------------------------------------------- |
| Owner            | Cesar Zea                                         |
| Method           | M06                                               |
| Baseline         | Main after PR #8 (`e47e6ae`)                      |
| Scope            | Resolve the dependency proposals preceding S03    |
| Status           | Locally verified; remote checks and merge pending |

## Decisions and delivery

Retain Node 24, `@types/node` 24.19.0, TypeScript 6.0.3 and the strict lint profile.
PR #3 (Node 26 types) and PR #5 (TypeScript 7) are closed as incompatible updates.
Combine the remaining proposals into one reviewed maintenance PR against current
main. Close the superseded proposals only after the replacement is merged.

| Proposal | Selected change                                                       | Acceptance                                                                        |
| -------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| #1       | setup-uv 10.2.0, pinned to `c18668ad3cf93ea998bef934396af7bb5c839dc7` | Existing version/Python inputs retained; remote workflow succeeds                 |
| #2       | Vite 8.3.1                                                            | Locked install, build and browser journeys pass                                   |
| #4       | uv 0.12.19                                                            | Development/CI/installer pins agree; exact offline installation remains mandatory |
| #6       | jsdom 30.1.1                                                          | Existing DOM/component tests and coverage pass                                    |
| #7       | Pyright 1.1.414                                                       | Strict analysis passes without disabling deprecation checks                       |

The action's reviewed [v8](https://github.com/astral-sh/setup-uv/releases/tag/v8.0.0),
[v9](https://github.com/astral-sh/setup-uv/releases/tag/v9.0.0) and
[v10](https://github.com/astral-sh/setup-uv/releases/tag/v10.0.0) changes concern
release security and cache defaults. The exact descriptor retains `version` and
`python-version` and uses Node 24. This workflow uses ordinary push/pull_request
triggers, an exact uv version and hosted Ubuntu runners. Remote checks must still
validate the action; local verification cannot execute the hosted action itself.

## Contracts and representative cases

[Component installation](../contracts/component-installation.md) and
`InstallationCatalog.prepare/verify` remain authoritative. New resolutions record
`uv_version: "uv 0.12.19"`; previous records (including `"uv 0.12.17"`) and artifact
identities remain unchanged and verifiable. The installer still rejects an
unexpected executable version before installing and uses exact hashed wheels
without network fallback. No resolution schema or production dependency changes.

For a decorated generator such as `ComponentProcess.connect`, use
`AsyncGenerator[ComponentConnection]` as its generator return annotation;
callers still obtain the same async context manager. Preserve all yields, cleanup,
exception handling and public yielded values. Synchronous `@contextmanager`
implementations use `Generator[YieldedType]` under the same rule.
Ordinary async iterator interfaces
and undecorated generators need no mechanical conversion.

## Exclusive assignments

- Coordinator: root/frontend package metadata and generated locks, workflow,
  CONTRIBUTING, application package generator typing, shared plan, final review,
  verification and publication.
- Installer implementer: the complete installation adapter package and its module
  documents; component-preparation module documents. Update the exact uv pin only.
- Typing implementer: complete process, SQLite and bootstrap packages, host SDK and
  LLMCall package and their module documents. Update decorated generator annotations
  without changing behavior. Test annotations are addressed in the testing phase.

No implementer edits another assignment's files, root locks or shared plan.
Local import formatting and the concrete spelling of annotations remain local
choices. Cross-module behavior and schema changes are outside this maintenance.

## Review and testing

Review the delivered pin and all decorated generators before testing. Then update
the existing preparation and installation expectations for the selected uv version
and any decorated test-support generator annotations rejected by the new analyzer.
Existing failure/integrity, managed-process cancellation and gateway tests provide
behavioral regression coverage; do not add tests that merely mirror annotations.
Establish the pinned Node/Python/uv environment and run a representative offline
installation before `make verify` through the same configured local/CI runner.
All gates, coverage requirements, browser journeys, accounting mutations and
CodeQL remain required. Refresh remote checks on the replacement PR before merging.

## Evidence and limitations

Record local/remote outcomes in the replacement PR and changelog. This maintenance
is separate from S03. No measured productivity gain is claimed, no paid provider
calls are required, and historical improvement evidence is not rewritten.

## Local acceptance — 2026-10-01

The representative offline installation passed. The complete configured
`make verify` runner then passed: 1,421 Python tests, 154 frontend tests and ten
browser journeys. Combined Python coverage was 95.86%; independent line and
branch coverage exceeded 90%. Frontend coverage was 98.34% statements and 92.89%
branches. Both pinned CodeQL suites completed with no warning/error findings;
80 Python notes and no JavaScript notes remain in the local reports. The existing
accounting mutation run completed; surviving baseline mutants are not claimed
as killed. No paid provider call was made.

The first shared attempt stopped at the physical-size gate after an annotation
wrapped a fixture signature. Extracting its existing identity construction into a
private helper restored the 30-line limit without relaxing the gate. The full
runner was resumed through the same configured entry point.

## Publication closure — 2026-10-01

[PR #9](https://github.com/cesarzea/slow-thinker-ii/pull/9) passed all required
remote checks and was merged at 19:52:19 UTC as `604cc5d`. The replacement closes
this maintenance delivery. Later contribution-guide documentation was merged in
[PR #10](https://github.com/cesarzea/slow-thinker-ii/pull/10) at 22:47:17 UTC as
`f10e062`, also with all required checks passing. The pending states above retain
what was known at the earlier checkpoint; neither merge constitutes a product release.
