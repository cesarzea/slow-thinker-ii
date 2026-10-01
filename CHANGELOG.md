# Changelog and version register

Owner: Cesar Zea. Updated: 2026-10-01, Europe/Lisbon.

This is the central record of development progress and versioned sprint reports.
Package versions and report versions have separate meanings. No published product
release is recorded here yet.

## Current development versions

| Artifact             | Version       | Authoritative source                                          |
| -------------------- | ------------- | ------------------------------------------------------------- |
| Python application   | `0.1.0.dev1`  | [pyproject.toml](pyproject.toml)                              |
| Frontend application | `0.1.0-dev.1` | [package.json](package.json)                                  |
| Latest sprint report | `0.0.2.3`     | [S02 status report](docs/progress/sprint-02-status-report.md) |

The report identifier follows `<series-major>.<series-minor>.<sprint>.<revision>`:
`0.0.2.1` means report series V0.0, Sprint 2, Revision 1. It does not change package
versions or identify a published software release.

## Unreleased development progress

- Local collaborative execution, independently hosted components, bounded
  proposer/reviewer feedback, saved history, deadlines, budgets and costs:
  [S01 delivery specification](docs/specification/first-cycle-sprint.md).
- Agent-focused canvas, optional model configuration/system markers, English
  presentation and corrected input/output geometry:
  [S02 delivery specification](docs/specification/agent-canvas-sprint.md).
- Mandatory pinned CodeQL in the common local/CI runner, with complete extraction
  checks and verified failure behavior: [verification](docs/verification.md#shared-codeql-verification-and-commit-readiness--2026-10-01).

The [verification record](docs/verification.md) retains tested behavior, checkpoint
chronology and publication prerequisites. Planned future work belongs in the
[sprint roadmap](docs/specification/sprint-roadmap.md).

## Sprint report version history

| Version     | Recorded date | Sprint | Progress status                                                                                                | Report and specification                                                                                                                       |
| ----------- | ------------- | ------ | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **0.0.2.3** | 2026-10-01    | S02    | Shared CodeQL rejection and full local verification passed; updated remote CI not yet run.                     | [Status report](docs/progress/sprint-02-status-report.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md)                  |
| 0.0.2.2     | 2026-10-01    | S02    | Approved CodeQL cleanup and follow-up tests verified; shared-verification integration remains open.            | [Revision 2 snapshot](docs/progress/sprint-02-status-report-0.0.2.2.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md)    |
| **0.0.2.1** | 2026-10-01    | S02    | Local delivery and owner-requested corrections verified; publication prerequisites remained open at recording. | [Original status report](docs/progress/sprint-02-status-report-0.0.2.1.md) · [Sprint specification](docs/specification/agent-canvas-sprint.md) |

## Maintenance

Append each substantive report revision with its version, date, sprint, status and
evidence links. Keep prior entries and the report's dated revision history. Retain
superseded report content in version control or a versioned snapshot before
replacing it. Use the next sprint's identifier for its own reports.

Record product release entries only when the corresponding release exists, with
its actual version, date and evidence. Development checkpoints and reports do not
constitute release approval.
