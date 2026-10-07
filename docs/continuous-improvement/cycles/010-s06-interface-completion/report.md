# C10 — Complete S06 product interface

| Document control  | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| Document ID       | C10                                                            |
| Status            | Locally verified; owner usability acceptance pending           |
| Owner             | Cesar Zea                                                      |
| Date and timezone | 2026-10-03, Europe/Lisbon                                      |
| Method            | M06, unchanged                                                 |
| Product scope     | [S06-UI-COMPLETE](../../../archive/previous-implementation/specification/s06-ui-completion.md) |

## Context and hypothesis

Owner review after C09 found that the collection remained technical, inspector
grouping was inconsistent, graph routes were confusing, legacy sequence controls
were unavailable, and technical graph/definition panels remained below Design.
The owner authorized completing every existing interface area and demonstrating
actual agent composition with Redirector. Prior test counts did not establish
product completeness. These are escaped product/design defects, not failures
of the user's review or retrospective changes to the earlier test results.

This cycle retains M06. Preparation covers the complete destination/workflow
matrix before assigning whole modules, and review must exercise all destinations
before concluding readiness. No new working-method version is approved here.

## Measurement basis

Goal activation is recorded at 2026-10-03 05:03:43 UTC (06:03:43 Europe/Lisbon).
The first post-delegation clock observation is 05:13:34 UTC. That is a checkpoint
span including preparation and initial environment inspection, not a classified
activity total. No active-time/participant-time audit is claimed. Final mandatory verification was confirmed at 06:57:11 UTC: a goal-to-verification
span of 1 h 53 min 28 s. This includes execution/waiting intervals and excludes
subsequent closing documentation; it is not classified active time or participant
effort. No duration estimate is presented as an observed result.

## Delivery and process results

Three source assignments have exclusive whole-module ownership: product shell,
shared UI, editor and library; workspace configuration; graph, execution and
evidence. Coordinator owns contracts, descriptor annotations and demonstration
composition. Source implementation precedes combined review and functional tests.
The existing unsaved owner draft was preserved separately before review navigation.

The baseline UI fixture simulates agent execution. A separate demonstration
composition is being prepared using production services, installed processes and
MCP, with model traffic confined to a deterministic loopback upstream. Distinguish
these evidence classes explicitly; neither represents a new paid-provider run.

At 05:25 UTC the separate production-service demonstration server had started.
Its initial sandboxed launch could not bind a loopback socket; the authorized
local-server launch succeeded with the required execution permission. This was
environment preparation, not a product test failure. Component execution and
browser verification remained pending at this checkpoint.

One shared presentation question arose during implementation: the existing run
panel API could not place the admitted graph and inspector before history. The
coordinator approved one optional React children slot, jointly implemented by the
app and execution owners. Review placed it at full width after result/setup,
rather than inside a narrow result column. This is a bounded handoff omission and
correction; it does not change execution, state ownership or backend contracts.

The configuration owner delivered source with scoped static checks passing.
Coordinator review found stale completion claims in accumulated module README
sections and requested concise current status with historical evidence linked
separately. Functional testing had not been released at this checkpoint.

All three owners subsequently delivered source receipts. Combined code and visual
review covered collection, Design/inspector, Resources, Versions, Runs, experiment
settings, workspace settings and component library. Corrections were grouped by
owner: scope selected-run evidence to its admitted run; compact scalar editors;
remove the orphan global configuration disclosure; clarify graph-visible resource
counts; classify the RoutedCall router as an internal composition slot; expose
run-state retry and session creation; suppress untouched input-error noise.

Configured Node 24 typing, dependency boundaries and unused-code checks passed.
An initial coordinator command omitted the configured Node path and the static
tool loading the browser configuration could not bind a sandboxed loopback port.
Both checks were rerun with the established environment and required permission.
These were invocation/environment failures, not source defects; no gate changed.

Functional verification began at approximately 05:47 UTC after the source and
whole-page review. The first composed-agent browser case passed before parallel
module regression expansion: four activations, rejection/acceptance routes,
keyboard selection at 390 pixels, provenance and final result. The browser owner
initially lacked the complete cache environment in the handoff; restoring the
Makefile-defined local browser cache resolved startup without installation.
Installed bounded-review checks separately passed both acceptance and exhaustion
(2 tests, 136.20 seconds); production presentation discovery passed 2 tests.

The first manual production-service demonstration completed with four activations
but retained pending cost reservations because the local synthetic provider omitted
the required cache-write token counter. This is a demonstration-fixture defect.
The fixture was corrected, with its original request evidence and run retained;
the application correctly kept unverified usage as an unresolved obligation.
No paid provider traffic occurred. The corrected run `149cb88d` completed with
four activations and the routes `next`, `revise`, `next`, `accept`. Its 17 mediated
calls include both reviewer-to-worker and reviewer-to-router invocations; all
seven owned processes were reaped. All four synthetic usage receipts settled,
leaving zero pending for this run. The previous fixture obligation remains visible.
[Sanitized runtime evidence](../../../archive/previous-implementation/evidence/s06-ui-completion-local-run-20261003.json)
distinguishes installed execution from illustrative model output and cost.

The remaining installed-process checks passed: 18 tests in 474.23 seconds.
Together with the two bounded-review checks, this covers all 20 installed cases.
Module regression expansion identified three additional product defects: duplicate
React sibling keys in ordinary agent inspectors, an error changing a textarea's
accessible name, and successful polling retaining a stale failure message. Each
received a focused correction and regression; unrelated state and safeguards
were retained. Navigation review also corrected loss of selected-run identity
between experiment sections.

The manual create/save/version journey exposed a first-save history refresh defect:
an unchanged draft identity retained its pre-save not-found response. A regression
reproduced it before correction and passed after the existing refresh generation
was forwarded. The module API and immutable history semantics are unchanged.

The first unchanged whole-project runner began at 06:24:23 UTC. Static checks and
CodeQL passed, followed by 2,280 Python tests. The frontend run passed 855 tests
and failed five in three previously omitted scoped-test files: public-view entry,
graph/activity selection and resource inventory. Their expectations still used
the old presentation. This is a test-assignment inventory omission, not evidence
that every module regression had been covered by the earlier receipts. Assertions
are retained while their setup and selectors are corrected.

Final visual inspection also found that opening adjacent run evidence could clip
the graph: initial framing did not observe a later host-width change. The targeted
correction must refit only an automatically framed viewport when the host changes,
preserving manual pan, zoom and dragging and avoiding refits on ordinary polling.
The pre-correction capture is retained with local diagnostic evidence.

The viewport correction initially introduced a native resize-observer delivery
loop. A browser regression captured window errors directly and rejected that
implementation. The replacement checks visible host dimensions on graph commits
and deferred window resize, retaining temporary observation only for hidden
initialization. Four focused browser cases pass without window errors, preserving
automatic fitting, manual camera changes and polling. Actual browser inspection
also confirms the complete graph beside the Redirector's recorded response.

Combined frontend verification now passes 868 tests in 153 files with unchanged
independent coverage thresholds: 97.85% lines, 91.08% branches, 97.62% functions
and 96.68% statements. The fresh unchanged whole-project runner began at
06:48:08 UTC and passed with exit 0, confirmed at 06:57:11 UTC. It records
2,280 Python tests, 868 frontend tests and 39 browser journeys, with unchanged
quality/security/coverage gates and the existing mutation baseline.
[Final evidence](../../../archive/previous-implementation/evidence/s06-ui-completion-verification-20261003.json)
and [report 0.0.6.5](../../../archive/previous-implementation/progress/sprint-06-status-report.md) retain the
deliverable. Owner usability acceptance and publication remain pending.

## Evaluation and limitations

Exclusive packages allowed concurrent implementation and module verification
without overlapping source ownership. The composition proof uses actual installed
processes; the separate UI fixture remains appropriate for repeatable browser
assertions. Neither passing automated checks nor screenshot resemblance establishes
owner acceptance.

Preparation remained incomplete in three observable ways: one shared presentation
slot needed an implementation-time decision; three existing test files were missed
by scoped assignments; and first-save history plus evidence-panel resizing escaped
the initial whole-page review. The late viewport correction also required a second
implementation after a native browser error. These are recorded rework, not ordinary
feature completion relabeled as first-pass success.

The first full runner repeated Python verification that had already passed when
the final frontend corrections were complete. Its Python phase alone took 326.94
seconds. This quantifies one repetition; it is not a complete activity audit or a
claim that all repeated verification was avoidable. Total participant effort,
classified active time and comparison with previous cycles remain unaudited.

Proposed improvements for a subsequent owner decision:

- Resolve every existing test file to an assignment before releasing testing;
  filename prefixes alone are not an adequate inventory.
- Include first save followed immediately by Versions, and opening/closing adjacent
  evidence, in the short representative product review before the mandatory runner.
- Supply the established runtime and cache environment in every testing handoff.

These proposals do not create a new method version or weaken any verification gate.

## Next-cycle decision

No new method proposal is approved. Current product completion is authorized by
the owner; prior narrow review notes now form part of its acceptance scope.
