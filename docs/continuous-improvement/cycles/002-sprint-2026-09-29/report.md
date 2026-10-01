# C02 — Evaluation of the phased sprint

| Document control | Value                                                                                                                |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| Cycle            | C02 — Sprint through delivery                                                                                        |
| Method           | [M02 — Complete phased sprint](../../methods/002-phased-sprint.md), agreed before the final resumption on 2026-09-29 |
| Record owner     | Cesar Zea                                                                                                            |
| Recorded date    | Not separately stated in the source report; session dated 2026-09-29                                                 |
| Measured period  | 2026-09-29 03:53:47.687–05:47:13.562                                                                                 |
| Time zone        | Lisbon (UTC+1 during the measured period)                                                                            |
| Record type      | Retrospective method evaluation                                                                                      |

## Result

The session delivered the first locally verified cycle and a pull request with all
checks passing. The phase structure was applied, and development of three work
packages overlapped. This provides favorable evidence about organization and time
to delivery, but does not establish a percentage improvement in productivity. The
preceding session built much of the foundation reused here, and the scopes differ.

## Measured window

- Final instruction, English translation of the recorded user instruction: “OK, I will activate the goal so you can continue.” This is a translation, not a verbatim English record.
- Turn start: 2026-09-29 **03:53:47.687**, Lisbon time (UTC+1).
- Turn end: **05:47:13.562**.
- Recorded active duration: **6,805.888 s = 1 h 53 min 25.888 s**. The difference from the wall-clock interval is 13 milliseconds.
- There were no pauses awaiting user responses. Necessary tool and CI waits are included. The hours until the next morning's message and preparation of this report are excluded.
- The earlier message estimated approximately 1 h 52 min, using a checkpoint after the turn began. This report counts from the complete instruction.

## Wall-clock phases, with no double counting of overlap

| Phase                                                             |            Duration |
| ----------------------------------------------------------------- | ------------------: |
| Analysis, documents, contracts and assignments                    |         20 min 17 s |
| Parallel development and individual review                        |         26 min 47 s |
| Joint review and corrections before testing                       |          5 min 30 s |
| Testing, corrections and demonstration through local verification |         37 min 50 s |
| Publication, CodeQL findings, corrections and final CI            |         23 min 03 s |
| **Total, using unrounded timestamps**                             | **1 h 53 min 26 s** |

The phase boundaries (UTC) are the first assignment at 03:14:04, the final initial
delivery at 03:40:51, the first testing assignment at 03:46:21, the documented local
checkpoint at 04:24:11, and the turn end at 04:47:13. Individual review began while
backend implementation was still underway. Functional tests were not run during
preparation and initial implementation; static checks were run. Independently
rounded phase durations may sum to one second more than the rounded total.

## Accumulated agent activity

This is neither CPU time nor an estimate of how long a single implementer would
have taken. It is the sum of active turn durations for the Coordinator and the
three implementers, including their tool waits. Periods when each implementer was
idle between assignments are excluded. Background tests and automatic permission
review processes are not added separately.

| Participant |                Recorded activity |
| ----------- | -------------------------------: |
| Coordinator |                       113.43 min |
| Backend     |                        62.67 min |
| Components  |                        36.77 min |
| Frontend    |                        42.86 min |
| **Total**   | **255.73 min = 4 h 15 min 44 s** |

## Retrospective distribution by activity

The total and milestones are measurements; this classification is an estimate. It
retains the preceding report's methodological basis: visible actions, edit
destinations and event times. Recorded deliberation intervals without a specific
observable purpose are classified as Analysis; their content is neither read nor
reproduced. Analysis therefore also includes understanding and local decisions
during implementation or testing, rather than exclusively new architectural design.

| Activity                                | Approximate accumulated time | Proportion |
| --------------------------------------- | ---------------------------: | ---------: |
| Analysis                                |                      111 min |      43.5% |
| Implementation                          |                       43 min |      16.7% |
| Documentation                           |                       16 min |       6.4% |
| Testing and verification                |                       45 min |      17.5% |
| Technical diagnosis                     |                       11 min |       4.1% |
| Environment and operational integration |                        6 min |       2.2% |
| Communication and follow-up             |                       11 min |       4.5% |
| Context compaction                      |                        8 min |       3.1% |
| Unattributed active time                |                        5 min |       2.0% |
| **Total**                               |     **256 min = 4 h 16 min** |   **100%** |

The minutes use compensated rounding to preserve the total. The CSV files retain
the sum in seconds, without implying semantic accuracy to the second. Commands
with mixed purposes are assigned to their predominant activity. The boundary
between analysis, implementation and testing is particularly approximate.
Reanalysis due to inconsistencies cannot be reliably isolated in this session; it
is included in analysis/review and part of diagnosis. It is not assigned a value
of zero.

The Coordinator accounts for approximately 60 minutes of analysis, reading and
review within 113 minutes. The implementers account for another 51 minutes. This
remains the main block to monitor: separating the phases did not eliminate all
reading or review.

## Comparison with C01

The [C01 report](../001-baseline-2026-09-28/report.md) reconstructed **10 h 04 min
39 s** of activity, while the goal counter reported 8 h 59 min. The new breakdown
must be compared with the reconstructed 10 h 05 min, rather than the counter alone.

| Indicator                                                                |                                                          C01 |                                       C02 |
| ------------------------------------------------------------------------ | -----------------------------------------------------------: | ----------------------------------------: |
| Elapsed active time                                                      |                                                  10 h 05 min |                                1 h 53 min |
| Accumulated implementer and coordinator activity                         | 10 h 05 min, principal work without these three implementers |                                4 h 16 min |
| Analysis/reanalysis plus testing, under the retrospective classification |                                                        62.6% |                                     61.0% |
| Recorded compaction                                                      |                                                       36 min | 8 min accumulated; 6 from the Coordinator |

The duration differences are observed, but **are not causal percentages of time
saved**. An equivalent task was not repeated under both methods. The new sprint
started with existing architecture, components, processes, persistence, budgets
and tests, as well as documentation prepared before resumption. The proportion of
analysis and testing remains effectively similar within the uncertainty of this
classification.

## Observed strengths and unresolved issues

- Common contracts and assignments were prepared before distributing Backend, Components and Frontend work. Ownership was separate, with no editing conflicts between them.
- The first three deliveries occupied approximately 62 accumulated minutes within 27 wall-clock minutes. This is evidence of effective overlap, not proof that sequential execution would have taken exactly 62 minutes.
- Joint review did not require replacing the architecture. Contract clarifications occurred during implementation, together with localized corrections to function limits, asynchronous selectors and graph/execution identity.
- Testing found input, focus and interface-framing defects, together with fixture and tool-configuration adjustments. Tests continued to require corrections.
- There were four launches of `make verify`: one stopped early at a static check, one stopped because of insufficient branch coverage, and two completed successfully, the second after CodeQL corrections. These were not four complete, identical repetitions.
- After publication, CodeQL detected resource cleanup conditional on assertions and ambiguous protocol declarations. Delivery remained open until these were corrected.
- A documentation commit after the correction commit triggered CI again. Grouping these changes before the push would have avoided that additional execution; the entire final 23-minute phase cannot be attributed to this repetition.
- Some Coordinator activity involved repeatedly checking CI logs and states. There is no evidence that all of this reading was indispensable or that the earlier pattern had disappeared.

## Assessment and proposed next adjustment

Retain package assignments and contracts prepared in advance: they enabled a
verifiable delivery without a general redesign or user intervention during the
sprint. The evidence does not yet support a claim that the method drastically
reduces total effort.

The main proposed adjustment is to limit Coordinator review to contracts,
interactions, risks and specific changes; use bounded checklists; and group
corrections and documentation before final verification. Incorporate the failures
actually observed into the readiness criteria: identity, inputs, geometry,
cleanup outside assertions, and branch coverage. This proposal does not remove
necessary tests or add documentation phases.

This section records the proposal made at the close of C02. Subsequent approved
changes are recorded separately in the [C03 plan](../003-contract-closure/plan.md).

## Evidence and limitations

- [Activities by participant](activities.csv).
- [Intervals without double counting within each agent](intervals.csv).
- [Phases](phases.csv).
- [Original durations and results](results.json).
- [Archived measurement criteria](../../measurement.md). Temporary scripts and complete conversation logs are outside this history.
- Source: turn and tool start/end events from the conversation and its three implementers, and milestones from the sprint record. File modification dates were not used as a substitute for time worked.
- Activity-classification uncertainty exceeds the 1.5-percentage-point difference reported between analysis plus testing before and after; these should be interpreted as similar proportions.
- Preparing this report did not modify the project, rerun tests, reopen the goal or make new paid calls.

The [subsequent testing analysis](testing-analysis.md), added on 2026-09-29,
complements this report without replacing its figures.
