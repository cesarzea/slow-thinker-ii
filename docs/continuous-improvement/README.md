# Engineering Process Improvement

| Document control                      | Value                     |
| ------------------------------------- | ------------------------- |
| Document ID                           | CI-001                    |
| Status                                | Maintained project record |
| Owner                                 | Cesar Zea                 |
| Established                           | 2026-09-29                |
| Integrated into project documentation | 2026-09-30                |

## Purpose and scope

This record evaluates the engineering process used to develop Slow Thinker II.
It preserves versioned working methods, delivery-cycle observations, measurements,
review findings and improvement decisions. Its purpose is to support evidence-based
changes to that process without rewriting previous results.

Process-improvement cycles and product sprints have distinct identities. A cycle
records how work was organized and evaluated; a sprint defines the product delivery.
The approved [delivery specifications](../specification/first-cycle-sprint.md) and
[agent-canvas sprint](../specification/agent-canvas-sprint.md) define product scope.
The repository's [working rules](../../AGENTS.md) remain the operational authority.

## Method register

| Method                                                                                                  | Recorded status                                            | Application                                                           |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------- |
| [M01 — Incremental development](methods/001-incremental.md)                                             | Reconstructed observed practice; no retrospective approval | C01 baseline                                                          |
| [M02 — Complete sprint in phases](methods/002-phased-sprint.md)                                         | Approved on 2026-09-29                                     | C02; three implementers                                               |
| [M03 — Contract closure before delegation](methods/003-contract-closure.md)                             | Approved on 2026-09-29; incorporated into M04              | Contract preparation for C03                                          |
| [M04 — Contracts, test preparation and verification](methods/004-testing-and-verification.md)           | Approved on 2026-09-29; incorporated into M05              | Test preparation for C03                                              |
| [M05 — Local verification equivalent to CI](methods/005-local-ci-verification.md)                       | Approved on 2026-09-29; partially applied                  | C03 local delivery; local CodeQL and publication effect not evaluated |
| [M06 — Assignment preparation, review evidence and test readiness](methods/006-delivery-preparation.md) | Approved on 2026-10-01; current method                     | CodeQL gate follow-up applied; no efficiency audit                    |

Methods are retained as historical versions. A later method does not overwrite an
earlier method or retroactively change which method was used for a cycle.

M06 incorporates approved P08–P10 and retains M05's obligations. Its approval
does not activate a new sprint or cycle. See the
[dated decision](improvement-register.md#approval-of-m06--2026-10-01).

## Cycle register

| Cycle                                                                                | Method                 | Observed active elapsed time                 | Accumulated participant activity                | Outcome                                                                          |
| ------------------------------------------------------------------------------------ | ---------------------- | -------------------------------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------- |
| [C01 — Baseline](cycles/001-baseline-2026-09-28/report.md)                           | M01                    | 10 h 04 min 39 s                             | 10 h 04 min 39 s for the audited principal work | Execution, observation and control foundations; objective remained open          |
| [C02 — Sprint through delivery](cycles/002-sprint-2026-09-29/report.md)              | M02                    | 1 h 53 min 26 s                              | 4 h 15 min 44 s across four participants        | First local cycle verified; PR #8 checks completed                               |
| [C03 — Agent canvas and English presentation](cycles/003-contract-closure/report.md) | M05, partially applied | 36 min to initial handoff                    | 1 h 03 min 50 s across three participants       | Initial delivery audited; subsequent input/output correction verified            |
| [C04 — Dependency maintenance](cycles/004-dependency-maintenance/report.md)          | M06                    | Not audited; checkpoint span recorded        | Not audited                                     | Selected updates locally verified; remote publication pending                    |
| [C05 — Personal experiments](cycles/005-personal-experiments/report.md)              | M06                    | Not audited; 2 h 20 min 49 s checkpoint span | Not audited                                     | Personal authoring locally verified; delivery and preparation defects classified |

C01 covers the audited windows on 2026-09-28 and the brief reactivation on
2026-09-29. C02 covers 03:53:47–05:47:13 Europe/Lisbon on 2026-09-29. The initial C03
checkpoint interval was 15:37:54–16:09:15 UTC on 2026-09-30. The
[2026-10-01 audit](cycles/003-contract-closure/time-audit.md) reconstructs
15:36:03.706–16:12:03.527 UTC through the initial handoff, including preparation
and closing documentation; subsequent review corrections remain excluded. Report
preparation time is outside these measurements. Lisbon was UTC+1 for these dates.

The initial C03 delivery passed 139 frontend tests and nine browser journeys. The
later input/output correction passed 154 frontend tests and ten journeys, with the
four affected journeys rerun after a node-handling correction. These are successive
verification checkpoints, not measures of engineering productivity.

## Improvement cycle and records

1. Define the delivery context, hypothesis, method version and acceptance evidence
   before applying a proposed change.
2. Execute the approved work and retain observations, deviations and corrections.
3. Evaluate delivery outcomes, elapsed time, accumulated activity and rework using
   the [measurement policy](measurement.md).
4. Record the decision and its owner/date in the [improvement register](improvement-register.md).
   A proposal changes the working method only after explicit approval.
5. Preserve the prior version and record the next cycle's outcome even when it
   contradicts the original hypothesis.

Use the [cycle record template](cycle-template.md) for subsequent evaluations.
The [C03 plan](cycles/003-contract-closure/plan.md) retains the original approved
hypotheses and dated activation/closure notes. Follow-up proposals remain proposals
until approved. No further product sprint is defined by this process record.

## Evidence, limitations and governance

The cycles have different scopes, starting points and delivery constraints. Their
times do not establish a causal productivity improvement. Retrospective task
classification is approximate even when its accounting totals reconcile.
Analysis and testing represent approximately 63% of C01 and 61% of C02; that
small difference remains within classification uncertainty.

[Provenance](provenance.json) records the source and translated artifact hashes.
English presentation preserves numerical values and event chronology. Historical
approval/status statements are retained with their original dates; dated notes
identify later developments. Complete conversations, credentials and original
commands are excluded from the retained evidence.

All maintained process documents and authored evidence labels are in English.
This section is the canonical project record following the owner's decision on
2026-09-30. Former external document locations are navigation redirects. This is
an internal engineering record; it makes no claim of certification or compliance
with an external process standard.

## Publication verification follow-up — 2026-10-01

The [dated C03 follow-up](cycles/003-contract-closure/report.md#publication-verification-follow-up--2026-10-01)
records the common CodeQL gate and full local verification, using M06 package
assignment and review/test phases. This closes the local publication prerequisite
at a later checkpoint; it does not retroactively change C03's partial M05 assessment
or its measured times. Updated remote CI remains pending. Follow-up duration and
resource usage were not audited, so efficiency remains unevaluated.

## Browser CI regression follow-up — 2026-10-01

The [dated C03 follow-up](cycles/003-contract-closure/report.md#browser-ci-regression-follow-up--2026-10-01)
records a polling test that passed locally without proving the intended drag and
then failed in remote CI. Corrected movement and reset assertions passed focused
repetitions and the full local runner under M06. Remote validation of the correction
is pending at recording. Earlier verification counts and audited cycle times remain
unchanged; this follow-up supplies no measured productivity comparison.

## Geometry readiness follow-up — 2026-10-01

The [second browser follow-up](cycles/003-contract-closure/report.md#geometry-readiness-follow-up--2026-10-01)
records remote polling success and a separate narrow-viewport readiness failure.
Complete visible-card samples now support the original geometry assertions; the
representative, 20 repetitions and full local runner pass. Remote verification is
pending at preparation. Historical durations and conclusions remain unchanged;
two escaped test defects limit any claim about the method's verification efficacy.

## Maintenance closure and S03 evaluation — 2026-10-02

C04's [dated closure](cycles/004-dependency-maintenance/report.md#publication-and-identity-closure--2026-10-01)
records PR #9 merged with required checks passing and the owner's public-name
decision. Earlier pending statuses and checkpoint measurements remain preserved.
[C05](cycles/005-personal-experiments/report.md) evaluates M06's S03 application,
including shared-contract omissions, review corrections and classified verification
failures. Its checkpoints do not constitute an activity-duration audit. P11/P12
remain proposals; no efficiency improvement or new method version is claimed.
