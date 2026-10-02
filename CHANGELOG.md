# Changelog and version register

Owner: Cesar Zea. Updated: 2026-10-02, Europe/Lisbon.

This is the central record of development progress and versioned sprint reports.
Package versions and report versions have separate meanings. No published product
release is recorded here yet.

## Current development versions

| Artifact             | Version       | Authoritative source                                          |
| -------------------- | ------------- | ------------------------------------------------------------- |
| Python application   | `0.1.0.dev1`  | [pyproject.toml](pyproject.toml)                              |
| Frontend application | `0.1.0-dev.1` | [package.json](package.json)                                  |
| Latest sprint report | `0.0.3.1`     | [S03 status report](docs/progress/sprint-03-status-report.md) |

The report identifier follows `<series-major>.<series-minor>.<sprint>.<revision>`:
`0.0.2.1` means report series V0.0, Sprint 2, Revision 1. It does not change package
versions or identify a published software release.

## Unreleased development progress

- Personal JSON import/edit/validation, immutable revisions, manual lineage,
  exact selection and saved-definition execution with retained history:
  [S03 delivery specification](docs/specification/personal-experiments-sprint.md).
- SQLite v6 retains earlier data and verified backups; strict authoring boundaries
  and safe uncertain-save recovery pass the complete shared local runner:
  [S03 verification](docs/verification.md#personal-experiment-delivery--2026-10-02).
- Local collaborative execution, independently hosted components, bounded
  proposer/reviewer feedback, saved history, deadlines, budgets and costs:
  [S01 delivery specification](docs/specification/first-cycle-sprint.md).
- Agent-focused canvas, optional model configuration/system markers, English
  presentation and corrected input/output geometry:
  [S02 delivery specification](docs/specification/agent-canvas-sprint.md).
- Mandatory pinned CodeQL in the common local/CI runner, with complete extraction
  checks and verified failure behavior: [verification](docs/verification.md#shared-codeql-verification-and-commit-readiness--2026-10-01).
- Corrected polling journey proves actual agent movement and reset after an
  escaped browser-test defect: [verification](docs/verification.md#browser-polling-regression-and-publication-follow-up--2026-10-01).
- Complete visible-card geometry samples reject initialization/remount states in
  viewport checks: [verification](docs/verification.md#browser-geometry-readiness-follow-up--2026-10-01).

The [verification record](docs/verification.md) retains tested behavior, checkpoint
chronology and publication prerequisites. Planned future work belongs in the
[sprint roadmap](docs/specification/sprint-roadmap.md).

## Publication and dependency maintenance — 2026-10-01

- [PR #8](https://github.com/cesarzea/slow-thinker-ii/pull/8) was merged after
  all required remote checks passed on `2a4726e`; main records `e47e6ae`.
- Node 26 type declarations (#3) and TypeScript 7 (#5) were declined because the
  runtime and lint-toolchain compatibility targets remain Node 24 and TypeScript 6.
- The [maintenance plan](docs/progress/dependency-maintenance-plan.md) combines
  setup-uv 10.2.0, uv 0.12.19, Pyright 1.1.414, Vite 8.3.1 and jsdom 30.1.1.
  Exact installation pins and decorated generator annotations are adapted; all
  local mandatory gates pass. Replacement PR remote verification remains pending.

The later closure is recorded separately: [PR #9](https://github.com/cesarzea/slow-thinker-ii/pull/9)
passed required remote checks and was merged as `604cc5d` on 2026-10-01.
The contribution guide followed in [PR #10](https://github.com/cesarzea/slow-thinker-ii/pull/10),
merged as `f10e062` after required checks passed. Earlier pending states retain
their original checkpoint meaning.

## Sprint report version history

| Version     | Recorded date | Sprint | Progress status                                                                                                         | Report and specification                                                                                                                       |
| ----------- | ------------- | ------ | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **0.0.3.1** | 2026-10-02    | S03    | Personal authoring, immutable revisions and retained execution verified locally; publication and owner review pending.  | [Status report](docs/progress/sprint-03-status-report.md) · [Sprint specification](docs/specification/personal-experiments-sprint.md)          |
| **0.0.2.5** | 2026-10-01    | S02    | Remote polling passed; geometry readiness corrected with focused and complete local verification; remote rerun pending. | [Status report](docs/progress/sprint-02-status-report.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md)                  |
| 0.0.2.4     | 2026-10-01    | S02    | Remote polling failure corrected; focused repetitions and full local verification passed; remote rerun pending.         | [Revision 4 snapshot](docs/progress/sprint-02-status-report-0.0.2.4.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md)    |
| 0.0.2.3     | 2026-10-01    | S02    | Shared CodeQL rejection and full local verification passed; updated remote CI not yet run.                              | [Revision 3 snapshot](docs/progress/sprint-02-status-report-0.0.2.3.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md)    |
| 0.0.2.2     | 2026-10-01    | S02    | Approved CodeQL cleanup and follow-up tests verified; shared-verification integration remains open.                     | [Revision 2 snapshot](docs/progress/sprint-02-status-report-0.0.2.2.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md)    |
| **0.0.2.1** | 2026-10-01    | S02    | Local delivery and owner-requested corrections verified; publication prerequisites remained open at recording.          | [Original status report](docs/progress/sprint-02-status-report-0.0.2.1.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md) |

## Maintenance

Append each substantive report revision with its version, date, sprint, status and
evidence links. Keep prior entries and the report's dated revision history. Retain
superseded report content in version control or a versioned snapshot before
replacing it. Use the next sprint's identifier for its own reports.

Record product release entries only when the corresponding release exists, with
its actual version, date and evidence. Development checkpoints and reports do not
constitute release approval.
