# C03 — Contracts, testing and verification

| Document control                    | Value                                                                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------- |
| Cycle ID                            | C03                                                                                           |
| Owner                               | Cesar Zea                                                                                     |
| Original plan recorded              | 2026-09-29                                                                                    |
| Activation and local delivery notes | 2026-09-30                                                                                    |
| Current status                      | Local delivery verified; publication evaluation pending                                       |
| Planned method                      | [M05](../../methods/005-local-ci-verification.md), retaining M04 and M03                      |
| Approved decisions                  | [P05, P06 and P07](../../improvement-register.md), including the clarification of P03 and P04 |

## Original plan — 2026-09-29

At the time of this plan, the improvements were agreed and the cycle had not
started. Functional scope, start, duration and results remained to be defined or
measured. Later activation and delivery notes are recorded below.

### Hypotheses

Resolving shared decisions and referencing established contracts precisely before
delegation should reduce avoidable questions and rework. Measure the additional
preparation time as well to assess the effect on total delivery time.

The testing extension approved on 2026-09-29 proposes that preparing the environment
and scenarios, validating test infrastructure and grouping corrections and
publication should reduce test defects and avoidable repetition. Measure its cost.

The second extension approved on 2026-09-29 proposes that running reproducible CI
checks locally, including CodeQL, before publication should reduce remote correction
cycles. Measure the added local cost and total delivery time.

### Planned application

- Separate established decisions, unresolved coordinator decisions and internal
  module choices.
- Check contracts from both sides and walk through the complete case and failures.
- Assign work with sufficiently defined dependencies, autonomy and acceptance.
- Classify questions by cause, separately from progress updates and deliveries.

### Approved testing improvements

- Use shared commands and environments with pinned versions and propagated failures.
- Link scenarios and expected outcomes to contracts in implementation assignments.
- Validate representative fixtures, configurations, servers and browser setup at
  the start of testing before expanding the suite.
- Verify tests, static checks and coverage for each delivered block. The coordinator
  owns whole-system interaction and coverage verification.
- Group corrections and perform complete verification with code, tests and
  documentation ready. Record the cause of each subsequent repetition.

### Approved local CI verification

- Use one command locally and in GitHub with the same versions, configuration and
  failure criteria for reproducible checks.
- Include CodeQL before publication alongside existing checks.
- Verify the final code, tests and documentation; refresh evidence after changes.
- Retain independent GitHub verification and identify service-only checks. Treat
  automated Dependabot proposals separately.

### Evaluation to perform

Record time by phase and activity, question causes, cross-module defects,
corrections and verified outcomes. Compare with C02 while accounting for scope and
starting conditions. Retain results even when they contradict the hypotheses.

Separate product defects, test or fixture errors, environment problems and
incorrect expectations caused by ambiguous contracts. Record rework and repetition
with their causes. Assess total time, including added preparation. Figures and
outcomes were still awaiting measurement when this plan was recorded.

Also measure locally detected defects, remote-only defects, corrective publications,
CI cancellations and repetitions, verification duration and time to detect failures.
Do not attribute savings before evidence is available.

## Activation note — 2026-09-30

The owner authorized the reviewed agent-canvas changes and English throughout
the product. C03 now applies to that bounded presentation delivery. The original
plan above is preserved. Its publication/CodeQL hypothesis remains untested if
this delivery is not published.

The coordinator resolved shared UI identity, configuration provenance and API
compatibility before delegating two independent module groups. The complete
contract and acceptance scope are in the
[agent-canvas sprint specification](../../../archive/previous-implementation/specification/agent-canvas-sprint.md).
No provider calls or publication were needed. Review preceded the separate test
implementation phase.

The first retained clock sample was 2026-09-30 15:37:54 UTC, already during analysis.
It is a lower bound, not a claimed exact start. The 15:45:45 UTC sample occurred
after contracts and assignments. Earlier time must be reconstructed from source
timestamps before a reconciled total can be reported.

## Local delivery closure — 2026-09-30

The [delivery report](report.md) records outcomes, corrections and measurement
limits. Publication and CodeQL evaluation remain outside the completed local scope.
