# Sprint Status Report — S02

| Document control         | Value                                                                      |
| ------------------------ | -------------------------------------------------------------------------- |
| Report ID                | SPRINT-S02-001                                                             |
| Report version           | **0.0.2.4** — V0.0, Sprint 2, Revision 4                                   |
| Owner                    | Cesar Zea                                                                  |
| Reporting date           | 2026-10-01, Europe/Lisbon                                                  |
| Delivery date            | 2026-09-30                                                                 |
| Sprint                   | S02 — Agent canvas and English presentation                                |
| Delivery status          | Functional scope delivered and verified locally                            |
| Publication readiness    | CI polling regression corrected and verified locally; remote rerun pending |
| Acceptance status        | Owner-requested corrections delivered; final owner sign-off not recorded   |
| Product package versions | Python: `0.1.0.dev1`; frontend: `0.1.0-dev.1`                              |

The four-part report version identifies the report series, sprint and revision.
It is a documentation identifier, not a product release version. The report is
retrospective and summarizes existing evidence; its preparation does not constitute
a new verification run or release.

The [central version register](../../CHANGELOG.md) indexes this report and the
current development package versions.

## Delivery summary

The graph now presents agents and their declared routes, with optional model
configuration and system markers. Resources and execution evidence remain
accessible below the canvas. Product-authored interface text is English.

The owner's review identified hidden input/output connectors and an absent entry
arrow. The approved correction makes both visible and preserves their geometry
after configuration expansion, dragging and layout reset. This sprint changes
presentation; the existing managed execution and accounting behavior is retained.

## Scope and delivered progress

| Scope item                    | Delivered result                                                                                                    | Evidence                                                                                                                                                                                   |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Agent-focused graph           | AI-agent icon, component type and instance name; terminal routes end in open space.                                 | [Sprint specification](../specification/agent-canvas-sprint.md#shared-contracts)                                                                                                           |
| Configuration and provenance  | Optional model/effort display; saved-run configuration takes precedence; unavailable values remain explicit.        | [Graph module contract](../../frontend/src/features/graph-view/specification.md)                                                                                                           |
| System elements and resources | Optional small mediation markers; resources and exact activation/call selections below the canvas.                  | [Canvas verification](../verification.md#agent-canvas-and-english-presentation--2026-09-30)                                                                                                |
| Layout and navigation         | Reciprocal routes, position/viewport retention, reorganization and linked evidence inspection.                      | [Acceptance cases](../specification/agent-canvas-sprint.md#delivery-review-and-testing-phase)                                                                                              |
| English presentation          | Interface, accessible labels and authored messages are English; user content and historical evidence are preserved. | [Canvas verification](../verification.md#agent-canvas-and-english-presentation--2026-09-30)                                                                                                |
| Owner-review correction       | Visible connectors and graph-entry arrow; stable boundary geometry and corrected node initialization.               | [Approved correction](../specification/agent-canvas-sprint.md#approved-inputoutput-correction--2026-09-30) and [verification](../verification.md#agent-inputoutput-correction--2026-09-30) |

## Verification and acceptance evidence

| Checkpoint                      | Recorded result                                                                                                                                                                                                                                        |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Initial canvas delivery         | 1,266 Python/component tests, 139 frontend tests and nine browser journeys passed. Static, boundary, coverage and build checks passed through the recorded corrected/resumed verification sequence.                                                    |
| Connector correction            | 154 frontend tests passed. Coverage: 98.34% statements, 92.89% branches, 99.12% functions and 99.23% lines. Frontend typing, lint, format, dependency, dead-code and build checks passed.                                                              |
| Browser follow-up               | Ten journeys passed before the final node-handling correction; the four affected journeys passed again afterward. The connector regression rejects recurrence of the initialization warning.                                                           |
| Visual review                   | Single-agent and bounded-review entry/exit routes were inspected in the browser. An existing saved execution confirmed actual model/effort metadata. No paid model call was made for this sprint.                                                      |
| Original publication checkpoint | Local CodeQL was not run at the original S02 handoff. No commit, push or remote CI run was performed for that checkpoint. Backend checks were not repeated for the frontend-only correction.                                                           |
| Commit preparation follow-up    | On 2026-10-01, the full local runner passed through a resumed sequence. The approved cleanup then passed 705 integration/LLMCall tests and five installed checks. CodeQL reports zero errors and warnings; 82 Python notes were reviewed and retained. |

The [verification record](../verification.md) retains checkpoint chronology,
verification corrections and limitations. These results establish the stated local
delivery and the dated follow-up; they do not claim an uninterrupted first-pass
verification at the earlier checkpoint, remote CI success or release approval.

## Final local verification follow-up — 2026-10-01

The shared `make verify` runner now includes pinned CodeQL analysis and passed
uninterrupted: 1,421 Python tests, 154 frontend tests, ten browser journeys and all
configured static, build, mutation and independent coverage checks. Both CodeQL
suites completed without errors or warnings; 80 reviewed Python notes remain.
The real negative assertion probe was rejected. The [verification record](../verification.md#shared-codeql-verification-and-commit-readiness--2026-10-01)
details the 155 new gate tests, resource correction and remaining limitations.
No paid model call was made; updated remote CI execution is not yet recorded.

## Publication correction follow-up — 2026-10-01

The published revision passed CodeQL but failed one browser journey in remote CI.
The test attempted to drag an offscreen card and compared unrelated inline styles.
Its corrected assertions prove movement, preserve node/camera transforms across
polling and restore the initial position on reorganization. Product code is unchanged.

One representative case, ten focused repetitions and the complete shared runner
passed after correction, including 1,421 Python tests, 154 frontend tests and all
ten browser journeys. The [verification record](../verification.md#browser-polling-regression-and-publication-follow-up--2026-10-01)
retains the diagnosis and limitations. Remote checks for the correction are pending
at preparation; branch protection, release status and owner sign-off are unchanged.

## Outstanding items and next delivery

| Item                                    | Disposition                                                                                                                         |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Publication verification                | Shared local verification passed; remote CodeQL passed on the prior commit, and the corrected browser test awaits its remote rerun. |
| Final owner sign-off                    | Not recorded; owner-requested corrections are implemented and locally verified.                                                     |
| Marker hover/click inspection           | Intentionally deferred, not an unfulfilled S02 acceptance requirement.                                                              |
| S03 — Personal experiment configuration | Next proposed sprint: import/edit JSON graphs, configure agents, save versions and create variants. Implementation has not started. |

The [global sprint plan](../specification/sprint-roadmap.md) defines subsequent
scope, dependencies and provisional timing. [M06](../continuous-improvement/methods/006-delivery-preparation.md)
is approved for subsequent work. S02's retrospective
[process evaluation](../continuous-improvement/cycles/003-contract-closure/report.md)
records partial M05 application; it is distinct from this product progress report.

## Revision history

| Version | Date       | Change                                                                                                              |
| ------- | ---------- | ------------------------------------------------------------------------------------------------------------------- |
| 0.0.2.1 | 2026-10-01 | Initial formal report, consolidating S02 delivery, owner-review corrections, verification and outstanding items.    |
| 0.0.2.2 | 2026-10-01 | Added owner-approved CodeQL cleanup and follow-up evidence; clarified the remaining shared-verification obligation. |
| 0.0.2.3 | 2026-10-01 | Integrated the shared CodeQL gate, verified rejection and full local checks, and retained remote CI limitations.    |
| 0.0.2.4 | 2026-10-01 | Recorded the remote polling failure, corrected test evidence and complete local verification; remote rerun pending. |

The [original report, revision 0.0.2.1](sprint-02-status-report-0.0.2.1.md), is
retained unchanged as a versioned snapshot, together with [revision 0.0.2.2](sprint-02-status-report-0.0.2.2.md)
and [revision 0.0.2.3](sprint-02-status-report-0.0.2.3.md).

Increment the final version segment for substantive updates to this report and
append their date and purpose here. Reports for subsequent sprints use their own
sprint segment and identity; previous sprint results remain retained.
