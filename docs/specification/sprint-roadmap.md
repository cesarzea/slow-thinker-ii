# Sprint roadmap

| Document control | Value                                                                |
| ---------------- | -------------------------------------------------------------------- |
| Document ID      | PLAN-001                                                             |
| Owner            | Cesar Zea                                                            |
| Updated          | 2026-10-01, Europe/Lisbon                                            |
| Status           | Proposed delivery plan; implementation not activated                 |
| Working method   | [M06](../continuous-improvement/methods/006-delivery-preparation.md) |

## Objective and delivery order

Deliver a configurable collaboration laboratory, then compare experiments, analyze
collaboration deeply and automate the proposal and evaluation of improvements.
This is the global plan. Detailed sprint specifications and module tickets are
prepared when each sprint is ready to start, following the [requirements](requirements.md).

Execute in numbered order, closing each sprint with a working demonstration and
required verification before starting the next. Independent package assignments
within a sprint run in parallel under M06. Dependencies identify functional
prerequisites; they do not imply that all intervening work is technically required.
S03 is the proposed next sprint. Later scopes remain provisional.

## Sprint plan

| Sprint | Scope                                                                                                                            | Prerequisites                                                | State                |
| ------ | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | -------------------- |
| S01    | Local execution, mediated component calls, bounded proposer/reviewer collaboration, history, budgets and costs.                  | Initial foundations                                          | Delivered            |
| S02    | Agent-focused canvas, visible input/output, optional configuration/system markers, evidence inspection and English presentation. | S01                                                          | Delivered locally    |
| S03    | Import/edit JSON graphs; configure agents, save immutable versions and create manual variants.                                   | S01–S02                                                      | Next proposed sprint |
| S04    | Provider-neutral model selection, a second provider, supported reasoning options and unified cost/error handling.                | S03; existing gateway                                        | Proposed             |
| S05    | External user components, one tool and simple private/shared memory using existing installation and MCP boundaries.              | S03; existing component SDK                                  | Proposed             |
| S06    | Task datasets, evaluation criteria, repeated trials and comparison by quality, time, cost and failures.                          | S03; existing evidence/accounting                            | Proposed             |
| S07    | Parallel branches/joins, concurrent stateless calls and declared serialized stateful execution.                                  | S03, S05                                                     | Proposed             |
| S08    | Deep analysis of communications, result evolution and possible influence, linked to available evidence.                          | S06; S07 for parallel examples                               | Proposed             |
| S09    | Bounded runtime graph changes, reusable subgraphs and visualization of graph revisions.                                          | S03, S05, S07                                                | Proposed             |
| S10    | Extensible messages/events, bounded mailboxes and pause/resume at supported boundaries.                                          | S05, S07, S09                                                | Proposed             |
| S11    | Automatic proposal, controlled execution and evaluation of variants, with objectives, lineage and stopping limits.               | S03, S06, S08; S09/S10 for their profiles                    | Proposed             |
| S12    | Prompt-based experiment creation and modification, with visible proposed changes.                                                | S03; existing canvas                                         | Proposed             |
| S13    | Full graphical authoring over the same versioned JSON definitions.                                                               | S03; supported profiles                                      | Proposed             |
| S14    | Standalone Python export for an explicit supported profile, using direct calls and resolved dependencies.                        | S04–S05; S06 comparison fixtures                             | Proposed             |
| S15    | Single-owner server deployment and containerized graph execution, with persistent history and managed limits.                    | Stable supported profiles; S10 if durable resume is included | Proposed             |

S01/S02 identify the existing [execution](first-cycle-sprint.md) and
[canvas](agent-canvas-sprint.md) deliveries. Their [verification record](../verification.md)
remains authoritative; shared local verification passes. Remote CodeQL passed,
and the corrected polling case passed. A separate geometry readiness correction
is verified locally and awaits remote CI.
The [S02 status report](../progress/sprint-02-status-report.md), version `0.0.2.5`,
consolidates its delivered progress and outstanding items.
Product sprint numbers are distinct from the process-improvement cycle numbers.
Existing hosting, inheritance, package preparation, tariff updates and accounting
are reused rather than scheduled for reconstruction.

## Indicative delivery schedule

Planning unit: active elapsed hours from the start of S03, including preparation,
implementation, review, corrections, testing, documentation and necessary tool
waits. Assume one coordinator and up to three independent implementers under M06.
Concurrent implementer activity is not added to elapsed duration. Inactive periods
and waits for owner decisions shift calendar dates and are outside these estimates.

These ranges are initial planning judgments, not measured forecasts or delivery
commitments. They reflect the proposed scope and its technical complexity; they
are not extrapolated from C02/C03 or based on an assumed M06 productivity gain.
Confidence is low before detailed sprint preparation. Recalibrate after S03 and
at each milestone, preserving the original forecast and recording deviations.

| Milestone | Sprint block | Available outcome                                                                      | Block duration | Cumulative active time |
| --------- | ------------ | -------------------------------------------------------------------------------------- | -------------- | ---------------------- |
| MS1       | S03–S05      | Personal graphs, multiple providers, custom components, tools and simple memory.       | 12–24 h        | 12–24 h                |
| MS2       | S06          | Compare manual variants against task-specific quality, time and cost priorities.       | 6–12 h         | 18–36 h                |
| MS3       | S07–S08      | Parallel collaboration and deep analysis of possible influence and result evolution.   | 12–24 h        | 30–60 h                |
| MS4       | S09–S10      | Supported dynamic, event-driven and resumable workflows.                               | 16–32 h        | 46–92 h                |
| MS5       | S11          | Automatic bounded proposal and evaluation of improvements.                             | 6–12 h         | 52–104 h               |
| MS6       | S12–S15      | Prompt/graphical authoring, supported Python export and single-owner server execution. | 28–56 h        | 80–160 h               |

The main evaluation objective becomes usable at MS2, deep analysis at MS3 and the
automatic improvement loop at MS5. MS6 adds authoring and deployment paths rather
than blocking those earlier outcomes. The indicative remaining total is 80–160
active elapsed hours. Calendar dates depend on the agreed activation date and
daily/weekly availability; these have not yet been selected.

## Preparation, scheduling and closure

Before each sprint, resolve its affected [open decisions](open-questions.md),
approve the final scope and prepare contracts, acceptance criteria, ownership and
module tickets. Refine the timing forecast at that point, including analysis,
implementation, review, corrections, testing and documentation. Once availability
and an activation date are specified, convert the forecast into calendar targets;
do not treat active hours as calendar time.

Every delivery preserves the mandatory engineering gates, English documentation,
managed mediation and configured deadlines/budgets. Any paid demonstration stays
within the remaining existing USD 3 authorization. Python export deliberately
removes platform logging, intermediation and supervision for its supported profile.
Analysis distinguishes observed, reported and inferred evidence; unavailable
reasoning is not reconstructed and influence is not claimed as proven causality.

Future details remain open under Q15 (evaluation, analysis and optimization), Q16
(control, communication and deployment), Q21 (export) and Q22 (tools/memory).
The second provider/profile is selected before S04. Advanced memory integrations,
additional protocols and multi-user operation remain later extensions.
