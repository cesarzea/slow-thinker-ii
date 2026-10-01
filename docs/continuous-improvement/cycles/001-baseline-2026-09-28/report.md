# C01 — Baseline work-time report

| Document control | Value                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| Cycle            | C01 — Baseline period                                                                                |
| Method           | [M01 — Incremental development](../../methods/001-incremental.md), reconstructed historical practice |
| Record owner     | Cesar Zea                                                                                            |
| Recorded date    | Not stated in the source report; the history was established on 2026-09-29                           |
| Audited period   | Continuous goal created on 2026-09-28 and its brief reactivation on 2026-09-29                       |
| Time zone        | Lisbon (UTC+1 during the audited period)                                                             |
| Record type      | Retrospective reconstruction                                                                         |

The project was not modified and the goal was not resumed to prepare this report.

**Reconstructed active time: 10:04:39 (approximately 605 minutes, or 10 h 05 min).**
This duration comes from recorded turns. The allocation by activity is a
retrospective estimate; its minutes are not exact measurements of individual tasks.

## Start, pause and excluded time

| Window             | Start               | Pause               | Elapsed time | Recorded active time |
| ------------------ | ------------------- | ------------------- | -----------: | -------------------: |
| Main goal          | 2026-09-28 00:51:32 | 2026-09-28 18:35:25 |     17:43:53 |             10:02:36 |
| Brief reactivation | 2026-09-29 02:39:18 | 2026-09-29 02:41:21 |     00:02:03 |             00:02:03 |

The two windows span **17:45:56**. They exclude **07:41:17** of gaps between turns
and inactivity not counted in the recorded active duration. Time between the first
pause and the reactivation is outside these windows.

The record distinguishes the following interruptions:

- 2026-09-28 02:10:10–02:24:30: 14 min 20 s without a turn, after approval became pending.
- 2026-09-28 02:25:18–02:27:03: 1 min 45 s between the user's comment about Vercel and the instruction to provide a daily update.
- 2026-09-28 03:31:52–03:39:14: 7 min 22 s without a turn after the first delivery.
- 2026-09-28 03:47:21–03:47:31: 10 s between an interrupted turn and the next turn.
- Two turns have active durations shorter than their wall-clock intervals: approximately 4 min 48 s in the packaging block and 7 h 12 min 46 s in the overnight process block. Evidence is insufficient to attribute these interruptions to waiting for a user response. They are excluded using the active duration reported in the record.
- The remaining differences concern interval boundaries and timestamp precision. An asynchronous question is not deducted if work continued in parallel.

## Reconciliation with the goal counter

| Item                                              |         Time |
| ------------------------------------------------- | -----------: |
| Counter up to the first pause                     |     08:56:59 |
| Reactivation counted                              |     00:02:03 |
| Final counter                                     |     08:59:02 |
| Three additional work turns initiated by messages |     01:05:36 |
| Residual difference from precision or boundaries  |     00:00:02 |
| Reconstructed total                               | **10:04:39** |

The goal became blocked awaiting approval at 02:10 and became active again at
03:39. Three work turns occurred between those times: checking Vercel (48 s),
incorporating the daily update (2 min 05 s), and implementing the first delivery
after the user approved it (1 h 02 min 43 s). This activity explains almost all of
the difference from the counter. No time was added to reach a predetermined total.

## Estimated distribution

| Activity                                | Approximate time | Percentage | Included work                                                                                                                                                              |
| --------------------------------------- | ---------------: | ---------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Analysis                                |       3 h 51 min |      38.2% | Reading code and contracts, research and deliberation not identified as corrective work. This does not represent four hours of new architectural design.                   |
| Reanalysis due to inconsistencies       |       0 h 13 min |       2.1% | Identified intervals reviewing MCP discovery and compatibility, contract consistency and monthly allocation. This is a conservative estimate, not the full cost of rework. |
| Implementation                          |       1 h 45 min |      17.4% | Writing and modifying implementation, including code corrections. Writing tests is classified under Testing and verification.                                              |
| Documentation                           |       0 h 29 min |       4.8% | Editing and validating documents. Designing their contracts is classified under Analysis or Reanalysis due to inconsistencies.                                             |
| Testing and verification                |       2 h 15 min |      22.4% | Writing tests, feasibility checks, execution, static checks and visual checks; more than `make verify` alone.                                                              |
| Technical diagnosis                     |       0 h 22 min |       3.6% | Reading and interpreting failures and results. A test failure is not assumed to imply an architectural defect.                                                             |
| Environment and operational integration |       0 h 07 min |       1.2% | Dependencies, environments, operational configuration and Git management during the interval. Most publication work occurred after the pause and is excluded.              |
| Communication and follow-up             |       0 h 11 min |       1.7% | Progress messages, responses and coordination within active intervals.                                                                                                     |
| Context compaction                      |       0 h 36 min |       6.0% | Recorded compaction intervals: system overhead, rather than functional development.                                                                                        |
| Unattributed active time                |       0 h 16 min |       2.7% | Active duration retained without a reliable activity assignment; it is not artificially distributed among the other categories.                                            |
| **Total**                               |  **10 h 05 min** |   **100%** | Matches the rounded active total.                                                                                                                                          |

The 13 minutes of reanalysis and 22 minutes of diagnosis must not be added together
to claim that all of this time was avoidable rework. Corrections also consume
implementation and testing time, and diagnosis does not always result from an
earlier error. Analysis may include reanalysis that cannot be distinguished; this
boundary is less reliable than the total duration.

## Method and limitations

1. The original conversation events were reviewed: goal creation and changes, turn starts and ends, and activities with start and end timestamps. The two earlier brief goals and all work after the pause were excluded, except for the reactivation specified above. Preparing this report is also excluded.
2. Active turn durations were summed, clipping turns that crossed the start or pause. When a turn remained open for hours, its recorded active duration was used instead of the entire wall-clock difference.
3. Actions were classified by tool, command, edit destination and visible messages. Internal reasoning content was neither used nor reproduced. Deliberation intervals without a more specific observable purpose were assigned to Analysis.
4. The timeline was divided into disjoint intervals. When a test continued in the background while code was being written, time was attributed once to the foreground activity.
5. Short gaps were attributed to the next observable activity. Long gaps remained unattributed unless there was evidence of code or document generation. This is inference, not task telemetry. In two turns, allocations had to be adjusted proportionally to the recorded active duration; the adjustments are recorded in [results.json](results.json).
6. The distinction between new analysis, diagnosis and reanalysis is approximate. Identifiable inconsistency intervals were reviewed against their messages: MCP incompatibilities, client/process consistency and preservation of responses, and correction of monthly allocation. Other intervals are not classified as rework without evidence.
7. The total has a strong temporal basis; confidence in the semantic distribution is medium to low. There is no contemporaneous timesheet, so precision to the minute cannot be claimed for each category. CSV seconds make the sum reproducible; they do not increase that confidence.

See the shared [measurement criteria](../../measurement.md) for the historical
measurement framework.

## Conclusions recorded for C01

- Total time spent within these windows was approximately 10 h 05 min. The goal counter alone omitted approximately 66 minutes of work in manual turns.
- The largest estimated block is analysis, reading and decisions, followed by test preparation and execution, and implementation. It has not been established that most of the time was lost rewriting the architecture.
- Recorded compactions occupied approximately 36 minutes. Their duration is observable overhead; it does not demonstrate that they caused requirements to be lost.
- Documentation is estimated at 29 minutes under this classification: approximately 22 during specification and 7 during implementation. Contract design and reading are classified under Analysis. The previous estimate of 20–40 minutes of documentation maintenance was not supported by this breakdown and is superseded by this calculation, subject to its stated limits.
- The 16 unattributed minutes remain explicit. Assigning them to implementation or analysis to create an appearance of precision would be incorrect.

## Reproducible evidence

- [Turns and activity totals](turns.csv).
- [Classified intervals and event references](intervals.csv).
- [Results and adjustments](results.json).
