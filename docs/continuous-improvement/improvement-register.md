# Improvement Proposal and Decision Register

| Document control        | Value                        |
| ----------------------- | ---------------------------- |
| Document ID             | CI-REG-001                   |
| Status                  | Maintained decision register |
| Owner                   | Cesar Zea                    |
| Established             | 2026-09-29                   |
| English project edition | 2026-09-30                   |

## Decisions recorded after C02 — 2026-09-29

M02 was applied in C02. P05, P06 and P07 were approved for C03 as M05, which
incorporates M04 and M03. P03 and P04 were incorporated into P06. P01 and P02
remain pending. Recording a proposal does not constitute approval.

| ID  | Recorded observation                                                                        | Proposed action                                                                                                                     | Evaluation                                                                                       | Decision at 2026-09-29                                                           |
| --- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| P01 | The coordinator spent approximately 60 of 113 minutes on analysis, reading and review       | Focus review on contracts, interactions and risks; avoid reconstructing every implementation                                        | Compare reading/review, escaped defects and corrections with scope differences recorded          | Proposed; decision pending                                                       |
| P02 | Inputs, identity, framing and focus required corrections                                    | Make these criteria explicit in acceptance preparation for affected UI modules                                                      | Record defects detected before delivery and defects escaping review                              | Proposed; decision pending                                                       |
| P03 | Branch coverage and CodeQL triggered corrections after initial checks                       | Include observed failures in relevant checks before declaring delivery ready                                                        | Record cause, detection phase and necessary repetitions without lowering thresholds              | Approved through P06's per-block controls and coverage; application then pending |
| P04 | A later documentation commit triggered CI again                                             | Group final documentation with corrections before publication                                                                       | Count CI runs and record why each repeated                                                       | Approved and incorporated into P06; application then pending                     |
| P05 | Work was delegated with unresolved shared decisions and insufficiently precise references   | Close and check cross-module contracts before delegation; distinguish existing sources, coordinator decisions and internal autonomy | Classify queries by cause and measure preparation, clarifications and rework                     | Approved for C03; application then pending                                       |
| P06 | Testing required environment, fixture and expectation corrections and repeated verification | Share environment/commands, link scenarios to contracts, validate infrastructure early, check per-block delivery and group closure  | Separate failure causes and evaluate rework, justified repetition and total elapsed time         | Approved for C03; application then pending                                       |
| P07 | Local checks passed, but CodeQL found defects after upload; it had not run locally          | Use one local/CI command for reproducible checks, including CodeQL, on final changes before upload                                  | Measure locally/remotely detected defects, corrective uploads, repetitions, waits and total time | Approved for C03; application then pending                                       |

## Approval history

**2026-09-29:** The owner authorized a separately organized history of the working
method and its results as part of continuous improvement. Versioned methods and
archived cycles implement that decision.

**2026-09-29:** P05 was approved for C03 and recorded in
[M03](methods/003-contract-closure.md) and the [C03 plan](cycles/003-contract-closure/plan.md).
The decision did not activate the cycle or automatically approve P01–P04.

**2026-09-29, subsequent decision:** P06's five testing adjustments were approved.
[M04](methods/004-testing-and-verification.md) retained M03, concretized P03's
per-block delivery checks and incorporated P04. P01/P02 remained pending; C03 had
not yet started and its results were not measured at that decision.

**2026-09-29, subsequent decision:** P07 approved local verification equivalent to
CI before upload, including CodeQL. [M05](methods/005-local-ci-verification.md)
retained previous method versions and GitHub's independent verification.
[The initial C02 CodeQL run failed](https://github.com/cesarzea/slow-thinker-ii/runs/109255994412)
after local checks passed; [the final check passed](https://github.com/cesarzea/slow-thinker-ii/runs/109258589234)
after corrections. Approval at that point did not establish implementation,
measurement or activation of C03.

## Application update — 2026-09-30

C03 applied contract closure, phased delivery/review and separate test preparation
to the agent-canvas delivery. Its [report](cycles/003-contract-closure/report.md)
records fixture/verification corrections, results and limitations. Local CodeQL
was not run and publication was not evaluated. M05 therefore has partial
application evidence; its remote-defect/publication hypothesis remains untested.
The report's renderer-mock and verification-environment improvements are proposals,
not newly approved method versions.

**2026-09-30, documentation decision:** The owner authorized formal English process
records within the project documentation. This section supersedes the former
external location as the canonical record. Historical methods, results and
approval boundaries are preserved. The decision changes documentation governance;
it does not approve pending proposals or introduce a new development method.

## Proposals following C03 — 2026-10-01

Status: proposed for owner review; no working-rule or method-version change.
Target cycle: the next agreed delivery, not yet assigned. These proposals refine
existing concerns; they do not replace P05–P07 or automatically approve P01/P02.

| ID  | Evidence and hypothesis                                                                                                                                                                                                    | Proposed refinement                                                                                                                                                                                                                                                                                                                                                                           | Evaluation                                                                                                                                                                                                                                    |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| P08 | The graph implementer read backend plan/snapshot internals. This is a signal to investigate, not proof of unnecessary work. A handoff may leave a developer reconstructing shared decisions even without asking questions. | Make each assignment usable with its module specification and exact dependency contracts: consumed data paths and provenance, a representative public payload, resolved shared decisions and explicitly local choices. Use existing specifications/tickets rather than additional documents. Report unexpected investigation beyond those contracts with its missing information and outcome. | Distinguish necessary dependency comprehension, local implementation design and repeated cross-module design analysis. Record reopened decisions, causes and associated effort; include added coordinator preparation in total delivery cost. |
| P09 | The coordinator accounted for 18.44 of 27.11 analysis minutes. The audit does not identify how much review was duplicated. This refines pending P01.                                                                       | Include a brief acceptance-to-change map and material local design choices in each delivery. Review the changed code, contracts, interactions and risks using that map; retain mandatory code and whole-system review.                                                                                                                                                                        | Compare coordinator reading/review effort, decisions reconstructed during review and defects escaping review, accounting for scope. Fewer file reads alone do not establish improvement.                                                      |
| P10 | Shared renderer mocks, resource expectations and omitted browser-cache settings required corrections. These are documented C03 failures and refine P06's test readiness.                                                   | Before parallel testing, establish the shared fixtures/renderer mocks and run one representative composition/browser check. Resume failed verification blocks through the same configured entry point and environment.                                                                                                                                                                        | Record product, fixture, expectation and environment failures separately; count necessary reruns with causes and measure preparation plus total verification/delivery time.                                                                   |

The primary hypothesis is reduced repeated analysis across handoffs, including
investigation that occurs without a clarification request. Necessary understanding
of public dependency contracts remains part of implementation. No saving is
established by these proposals; acceptance coverage and quality gates remain intact.

## Approval of M06 — 2026-10-01

Owner: Cesar Zea. Status: P08, P09 and P10 approved as
[M06](methods/006-delivery-preparation.md), extending M05. The owner accepted the
three proposed changes and requested the new method version. The earlier proposal
status above is preserved as the record before this decision.

M06 applies to subsequent authorized delivery work; the next target cycle is not
yet assigned. It does not activate a new sprint, change C03's method or approve
P01/P02 independently. Its rationale is to reduce repeated shared-decision analysis
and avoidable test infrastructure corrections while preserving implementation
autonomy, code review and verification gates. Measure preparation plus delivery
cost and acceptance outcomes; no productivity gain is established by approval.

## Decision procedure

Append a dated decision with rationale, owner, target cycle and expected evidence.
If the agreed procedure changes, retain the prior method and create a new version.
Record the subsequent outcome even when it contradicts the hypothesis.
