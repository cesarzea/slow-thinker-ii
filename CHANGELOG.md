# Changelog and version register

Owner: Cesar Zea. Updated: 2026-10-05, Europe/Lisbon.

This is the central record of development progress and versioned sprint reports.
Package versions and report versions have separate meanings. No published product
release is recorded here yet.

## Current development versions

| Artifact             | Version       | Authoritative source                                          |
| -------------------- | ------------- | ------------------------------------------------------------- |
| Python application   | `0.1.0.dev1`  | [pyproject.toml](pyproject.toml)                              |
| Frontend application | `0.1.0-dev.1` | [package.json](package.json)                                  |
| Latest sprint report | `0.0.6.7`     | [S06 sprint report](docs/specification/s06/sprint-report.md) |

The report identifier follows `<series-major>.<series-minor>.<sprint>.<revision>`:
`0.0.2.1` means report series V0.0, Sprint 2, Revision 1. It does not change package
versions or identify a published software release.

## Unreleased development progress

- New execution core, S06 (cycle C12, method M07): graphs of Trigger, LLM Call,
  Router and Output nodes built in a visual editor with component-declared dialogs,
  run under supervision with limits and run, daily and monthly budgets, and inspected
  in an activity view; OpenAI, DeepSeek and simulated providers behind the platform's
  LLM service; components installed as separate packages and run as MCP hosts.
  Locally verified and accepted by the owner on 2026-10-07:
  [verification record](docs/specification/s06/verification.md). The previous
  implementation and its documentation are archived; the entries below describe it.
- S06 owner review (2026-10-04 and 05), closed with the complete runner: every edit
  saved with activated versions and branches; a reworked editor with arrangement modes,
  connection styles, port sides, collapsible and resizable panels; Components and Runs
  pages; run mode executing what is on screen in the editor, with observation points
  saved with the graph and a live feed; Memory as an isolated component at a new
  `memory` position of the component protocol. Decisions in ADRs 0024–0026; report:
  [S06 sprint report](docs/specification/s06/sprint-report.md).
- Scope review and replan (2026-10-06 and 07): requirements revision 3 (CR01–CR29),
  roadmap revision 3 with sprints S07–S25, ADRs 0028 (companies, users and workspaces)
  and 0029 (placement of nodes in containers), a complete documentation index checked
  by `make verify`: [scope review](docs/specification/scope-review-2026-10-06.md).
- License changed from Apache 2.0 to the Functional Source License 1.1 with an Apache 2.0
  future license (`FSL-1.1-ALv2`): [ADR 0027](docs/adr/0027-functional-source-license.md).

- S06 is reopened for configurable composition and component-owned dialogs.
  Parallel verification and corrections are active; the earlier receipt does not
  establish this expanded delivery: [current scope](docs/archive/previous-implementation/specification/s06-composition-and-dialogs.md).
- Earlier S06 whole-interface completion was locally verified: coherent collection,
  configuration, resources, versions and runs; real internal Redirector composition;
  focused source/activity views and readable evidence. The unchanged full runner
  passed; subsequent owner review found incomplete component composition:
  [report 0.0.6.5](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.5.md).
- S06 fidelity correction: contextual rail, readable collaboration canvas,
  adjacent prompt/model configuration, progressive component disclosures and
  actual desktop/narrow demonstrations. The unchanged mandatory runner passes;
  subsequent owner review found product completion insufficient:
  [historical report 0.0.6.4](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.4.md).
- Earlier workspace redesign: mandatory local gates passed, followed by owner
  rejection for visual/usability fidelity. Historical evidence is preserved:
  [report 0.0.6.3](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.3.md).

- Earlier S06 completion checkpoint: technically verified, then rejected by owner
  usability review; preserved in the historical report:
  [report 0.0.6.2](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.2.md).

- Provider-neutral OpenAI/DeepSeek model resources, explicit reasoning options,
  reviewed daily tariffs and native usage/evidence: [S04 report](docs/archive/previous-implementation/progress/sprint-04-status-report.md).
- External installed components, bounded calculator and private/shared durable
  key/value memory with managed composition: [S05 report](docs/archive/previous-implementation/progress/sprint-05-status-report.md).
- Structured component/graph configuration, Experiments/Components/Resources/Runs/
  Settings navigation and recoverable bounded budget commands: [S06 report](docs/archive/previous-implementation/progress/sprint-06-status-report.md).
- All shared local gates passed; actual two-provider resource collaboration and
  retained revisions audited within the existing USD 3 allowance:
  [S04–S06 live validation](docs/archive/previous-implementation/progress/s04-s06-live-validation.md).

- Personal JSON import/edit/validation, immutable revisions, manual lineage,
  exact selection and saved-definition execution with retained history:
  [S03 delivery specification](docs/archive/previous-implementation/specification/personal-experiments-sprint.md).
- SQLite v6 retains earlier data and verified backups; strict authoring boundaries
  and safe uncertain-save recovery pass the complete shared local runner:
  [S03 verification](docs/archive/previous-implementation/verification.md#personal-experiment-delivery--2026-10-02).
- S03 functional closure includes a real personal collaboration case, independently
  verified feedback, result and cost, and a recorded reviewer-quality limitation:
  [live validation](docs/archive/previous-implementation/progress/sprint-03-live-validation.md).
- Local collaborative execution, independently hosted components, bounded
  proposer/reviewer feedback, saved history, deadlines, budgets and costs:
  [S01 delivery specification](docs/archive/previous-implementation/specification/first-cycle-sprint.md).
- Agent-focused canvas, optional model configuration/system markers, English
  presentation and corrected input/output geometry:
  [S02 delivery specification](docs/archive/previous-implementation/specification/agent-canvas-sprint.md).
- Mandatory pinned CodeQL in the common local/CI runner, with complete extraction
  checks and verified failure behavior: [verification](docs/archive/previous-implementation/verification.md#shared-codeql-verification-and-commit-readiness--2026-10-01).
- Corrected polling journey proves actual agent movement and reset after an
  escaped browser-test defect: [verification](docs/archive/previous-implementation/verification.md#browser-polling-regression-and-publication-follow-up--2026-10-01).
- Complete visible-card geometry samples reject initialization/remount states in
  viewport checks: [verification](docs/archive/previous-implementation/verification.md#browser-geometry-readiness-follow-up--2026-10-01).

The [verification record](docs/archive/previous-implementation/verification.md) retains tested behavior, checkpoint
chronology and publication prerequisites. Planned future work belongs in the
[sprint roadmap](docs/archive/previous-implementation/specification/sprint-roadmap.md).

## Publication and dependency maintenance — 2026-10-01

- [PR #8](https://github.com/cesarzea/slow-thinker-ii/pull/8) was merged after
  all required remote checks passed on `2a4726e`; main records `e47e6ae`.
- Node 26 type declarations (#3) and TypeScript 7 (#5) were declined because the
  runtime and lint-toolchain compatibility targets remain Node 24 and TypeScript 6.
- The [maintenance plan](docs/archive/previous-implementation/progress/dependency-maintenance-plan.md) combines
  setup-uv 10.2.0, uv 0.12.19, Pyright 1.1.414, Vite 8.3.1 and jsdom 30.1.1.
  Exact installation pins and decorated generator annotations are adapted; all
  local mandatory gates pass. Replacement PR remote verification remains pending.

The later closure is recorded separately: [PR #9](https://github.com/cesarzea/slow-thinker-ii/pull/9)
passed required remote checks and was merged as `604cc5d` on 2026-10-01.
The contribution guide followed in [PR #10](https://github.com/cesarzea/slow-thinker-ii/pull/10),
merged as `f10e062` after required checks passed. Earlier pending states retain
their original checkpoint meaning.

## S03 publication closure — 2026-10-02

[PR #11](https://github.com/cesarzea/slow-thinker-ii/pull/11) was merged as
`1557522` after required checks passed, including its live/closure supplement.
The S04–S06 branch starts from that merged tree. Earlier pending entries remain
historical checkpoint statements; the latest sprint reports describe local delivery.

## Sprint report version history

| Version     | Recorded date | Sprint | Progress status                                                                                                         | Report and specification                                                                                                                            |
| ----------- | ------------- | ------ | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0.0.6.7** | 2026-10-07 | S06 | New execution core, reviewed and accepted by the owner; it replaces the earlier S06 scope. | [Sprint report](docs/specification/s06/sprint-report.md) · [Verification record](docs/specification/s06/verification.md) |
| 0.0.6.6 | 2026-10-03 | S06 | Configurable composition and component-owned dialogs; final verification active. | [Status report](docs/archive/previous-implementation/progress/sprint-06-status-report.md) · [Correction scope](docs/archive/previous-implementation/specification/s06-composition-and-dialogs.md) |
| 0.0.6.5 | 2026-10-03    | S06    | Earlier interface checkpoint; reopened after configurable composition review.         | [Status report](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.5.md) · [Completion scope](docs/archive/previous-implementation/specification/s06-ui-completion.md)                             |
| 0.0.6.4     | 2026-10-03    | S06    | Reference-based correction verified; subsequent owner review required further interface completion.                     | [Revision 4 snapshot](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.4.md) · [Fidelity contract](docs/archive/previous-implementation/reviews/2026-10-03-s06-fidelity/README.md)       |
| 0.0.6.3     | 2026-10-03    | S06    | Redesigned workspace technically verified, then rejected by owner visual/usability review.                              | [Revision 3 snapshot](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.3.md) · [S06-UX specification](docs/archive/previous-implementation/specification/s06-workspace-redesign.md)      |
| 0.0.6.2     | 2026-10-02    | S06    | Earlier product completion technically verified; subsequent owner usability review rejected it.                         | [Revision 2 snapshot](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.2.md) · [Completion contract](docs/archive/previous-implementation/specification/s06-product-completion.md)       |
| 0.0.6.1     | 2026-10-02    | S06    | Structured workspace locally verified; owner interface review and hosted checks pending.                                | [Revision 1 snapshot](docs/archive/previous-implementation/progress/sprint-06-status-report-0.0.6.1.md) · [Delivery block](docs/archive/previous-implementation/specification/s04-s06-delivery.md)                  |
| **0.0.5.1** | 2026-10-02    | S05    | External components, calculator and scoped memory locally verified, including real installed execution.                 | [Status report](docs/archive/previous-implementation/progress/sprint-05-status-report.md) · [Resource contract](docs/archive/previous-implementation/contracts/tools-memory.md)                                     |
| **0.0.4.1** | 2026-10-02    | S04    | Provider-neutral model resources and actual OpenAI/DeepSeek calls verified locally.                                     | [Status report](docs/archive/previous-implementation/progress/sprint-04-status-report.md) · [Model contract](docs/archive/previous-implementation/contracts/model-resources.md)                                     |
| **0.0.3.2** | 2026-10-02    | S03    | Functionally closed after real OpenAI acceptance; closure supplement publication and owner merge remain pending.        | [Status report](docs/archive/previous-implementation/progress/sprint-03-status-report.md) · [Live validation](docs/archive/previous-implementation/progress/sprint-03-live-validation.md)                           |
| 0.0.3.1     | 2026-10-02    | S03    | Personal authoring, immutable revisions and retained execution verified locally; publication and owner review pending.  | [Revision 1 snapshot](docs/archive/previous-implementation/progress/sprint-03-status-report-0.0.3.1.md) · [Sprint specification](docs/archive/previous-implementation/specification/personal-experiments-sprint.md) |
| **0.0.2.5** | 2026-10-01    | S02    | Remote polling passed; geometry readiness corrected with focused and complete local verification; remote rerun pending. | [Status report](docs/archive/previous-implementation/progress/sprint-02-status-report.md) · [Sprint specification](docs/archive/previous-implementation/specification/agent-canvas-sprint.md)                       |
| 0.0.2.4     | 2026-10-01    | S02    | Remote polling failure corrected; focused repetitions and full local verification passed; remote rerun pending.         | [Revision 4 snapshot](docs/archive/previous-implementation/progress/sprint-02-status-report-0.0.2.4.md) · [Sprint specification](docs/archive/previous-implementation/specification/agent-canvas-sprint.md)         |
| 0.0.2.3     | 2026-10-01    | S02    | Shared CodeQL rejection and full local verification passed; updated remote CI not yet run.                              | [Revision 3 snapshot](docs/archive/previous-implementation/progress/sprint-02-status-report-0.0.2.3.md) · [Sprint specification](docs/archive/previous-implementation/specification/agent-canvas-sprint.md)         |
| 0.0.2.2     | 2026-10-01    | S02    | Approved CodeQL cleanup and follow-up tests verified; shared-verification integration remains open.                     | [Revision 2 snapshot](docs/archive/previous-implementation/progress/sprint-02-status-report-0.0.2.2.md) · [Sprint specification](docs/archive/previous-implementation/specification/agent-canvas-sprint.md)         |
| **0.0.2.1** | 2026-10-01    | S02    | Local delivery and owner-requested corrections verified; publication prerequisites remained open at recording.          | [Original status report](docs/archive/previous-implementation/progress/sprint-02-status-report-0.0.2.1.md) · [Sprint specification](docs/archive/previous-implementation/specification/agent-canvas-sprint.md)      |

## Maintenance

Append each substantive report revision with its version, date, sprint, status and
evidence links. Keep prior entries and the report's dated revision history. Retain
superseded report content in version control or a versioned snapshot before
replacing it. Use the next sprint's identifier for its own reports.

Record product release entries only when the corresponding release exists, with
its actual version, date and evidence. Development checkpoints and reports do not
constitute release approval.
