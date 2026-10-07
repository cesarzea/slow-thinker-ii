# Sprint roadmap

| Document control | Value                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------- |
| Document ID      | PLAN-001                                                                                |
| Revision         | 4                                                                                       |
| Owner            | Cesar Zea                                                                               |
| Updated          | 2026-10-02, Europe/Lisbon                                                               |
| Status           | S06 product completion locally verified; owner review pending |
| Working method   | [M06](../../../continuous-improvement/methods/006-delivery-preparation.md)                    |
| Previous plan    | [Revision 3 snapshot](sprint-roadmap-20261002-r3.md)                                    |

## Objective and delivery order

Deliver a configurable collaboration laboratory with a coherent user interface,
then compare experiments, analyze collaboration deeply and automate the proposal
and evaluation of improvements. This is the global plan. Detailed sprint
specifications and module tickets are prepared when each sprint is ready to start,
following the [requirements](requirements.md).

The owner requested this replan after identifying that the current interface
primarily supports technical inspection. S06 now delivers the product workspace
for configuring agents and graphs and managing experiments and executions. The
previous S06–S15 scopes move to S07–S16; delivered S01–S03 identifiers stay unchanged.
No previously planned capability is removed.

Execute in numbered order, closing each sprint with a working demonstration and
required verification before starting the next. Independent package assignments
within a sprint run in parallel under M06. Dependencies identify functional
prerequisites; they do not imply that all intervening work is technically required.
[S03](personal-experiments-sprint.md) was merged in
[PR #11](https://github.com/cesarzea/slow-thinker-ii/pull/11) on 2026-10-02.
The owner subsequently activated [S04–S06](s04-s06-delivery.md) as one complete
delivery block. Its mandatory local checks and actual model/resource demonstration
passed; the three sprint reports retain separate acceptance scopes. Owner review
and hosted verification remain pending. S07 and later scopes are not activated. Owner interface review required a
[completion pass for S06](s06-product-completion.md); the original scope and all
later sprint assignments remain unchanged.

## Sprint plan

| Sprint | Scope                                                                                                                                                                                               | Prerequisites                                                | State                              |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------- |
| S01    | Local execution, mediated component calls, bounded proposer/reviewer collaboration, history, budgets and costs.                                                                                     | Initial foundations                                          | Delivered                          |
| S02    | Agent-focused canvas, visible input/output, optional configuration/system markers, evidence inspection and English presentation.                                                                    | S01                                                          | Delivered                          |
| S03    | Import/edit JSON graphs; configure agents, save immutable versions and create manual variants.                                                                                                      | S01–S02                                                      | Merged; functionally closed |
| S04    | Provider-neutral model selection, a second provider, supported reasoning options and unified cost/error handling; expose selection and configuration in the existing interface.                     | S03; existing gateway                                        | Locally verified; review pending     |
| S05    | External user components, one tool and simple private/shared memory; expose configuration and resource activity using existing installation and MCP boundaries.                                     | S03; existing component SDK                                  | Locally verified; review pending     |
| S06    | Product workspace: coherent navigation and forms for agents, supported graphs, resources, experiments, sessions and budgets; execution controls, results, history and optional evidence inspection. | S03–S05; existing canvas and operator API                    | Product completion locally verified; review pending |
| S07    | Task datasets, evaluation criteria, repeated trials and comparison by quality, time, cost and failures, with task setup and comparison views.                                                       | S03, S06; existing evidence/accounting                       | Planned; specification pending     |
| S08    | Parallel branches/joins, concurrent stateless calls and declared serialized stateful execution; configure and observe these execution modes.                                                        | S03, S05; S06 workspace                                      | Planned; specification pending     |
| S09    | Deep analysis of communications, result evolution and possible influence, with evidence-linked analysis views.                                                                                      | S07; S08 for parallel examples                               | Planned; specification pending     |
| S10    | Bounded runtime graph changes and reusable subgraphs, with configuration and visualization of graph revisions.                                                                                      | S03, S05, S08; S06 workspace                                 | Planned; specification pending     |
| S11    | Extensible messages/events, bounded mailboxes and pause/resume at supported boundaries, with communication configuration and execution controls.                                                    | S05, S08, S10                                                | Planned; specification pending     |
| S12    | Automatic proposal, controlled execution and evaluation of variants, with objectives, lineage, stopping limits and review of proposed improvements.                                                 | S03, S07, S09; S10/S11 for their profiles                    | Planned; specification pending     |
| S13    | Prompt-based experiment creation and modification, with visible proposed changes and explicit user acceptance.                                                                                      | S03, S06; existing canvas                                    | Planned; specification pending     |
| S14    | Full graphical authoring over the same versioned JSON definitions, extending the S06 configuration workspace.                                                                                       | S03, S06; supported profiles                                 | Planned; specification pending     |
| S15    | Standalone Python export for an explicit supported profile, using direct calls and resolved dependencies, with export selection and feedback.                                                       | S04–S05; S07 comparison fixtures                             | Planned; specification pending     |
| S16    | Single-owner server deployment and containerized graph execution, with persistent history, managed limits and the existing product workspace.                                                       | Stable supported profiles; S11 if durable resume is included | Planned; specification pending     |

S01/S02 identify the existing [execution](first-cycle-sprint.md) and
[canvas](agent-canvas-sprint.md) deliveries. Their [verification record](../verification.md)
remains authoritative. All required remote checks passed on `2a4726e`, including
the polling and geometry corrections. [PR #8](https://github.com/cesarzea/slow-thinker-ii/pull/8)
was merged on 2026-10-01 as `e47e6ae`.
The [S02 status report](../progress/sprint-02-status-report.md), version `0.0.2.5`,
consolidates its delivered progress and outstanding items.
Product sprint numbers are distinct from process-improvement cycle numbers.
Existing hosting, inheritance, package preparation, tariff updates and accounting
are reused rather than scheduled for reconstruction.

## User interface delivery

Every future sprint includes its required backend behavior, user interactions,
documentation and verification. Acceptance must cover a complete user journey in
the application; an API-only delivery cannot close a user-facing scope. S04/S05
extend the existing interface while their capabilities are introduced. S06
establishes the product workspace, which all later sprints extend consistently.

S06 covers:

- **Agents:** component selection and configuration of instructions, models,
  reasoning options, inputs, outputs and resource bindings supported by each type.
- **Graphs:** forms for agents, connections, declared routes and execution limits
  in the supported control profiles, with validation and immutable revision saving.
- **Resources and experiments:** configuration of available tools and memory,
  experiment revisions and variants, task input, saved sessions and budgets.
- **Executions:** clear admission, running, stopping and recovery states; results,
  history and cost summaries; optional inspection of calls and available evidence.
- **Interaction design:** coherent navigation and reusable form patterns, clear
  loading/empty/error states, keyboard access and English product-authored content.

Configuration forms and expert JSON editing use the same versioned definitions
and validation contracts. S06 preserves supported extension configuration rather
than imposing a closed set of built-in agent types. Its design must define how
component-declared configuration is presented and validated. Credentials do not
become fields in graph JSON. Saving a revision must not alter admitted runs or
their history.

The [approved visual model](../architecture/visual-model.md) remains authoritative:
agents and collaboration routes are the main graph; resources and technical
details are accessible separately. S06 configures graphs through forms alongside
the existing canvas and JSON authoring. S14 adds direct graphical authoring.
Evaluation setup and comparisons arrive in S07 and extend this same workspace.

## Milestones and estimation basis

| Milestone | Sprint block | Available outcome                                                                                              |
| --------- | ------------ | -------------------------------------------------------------------------------------------------------------- |
| MS1       | S03–S05      | Personal graphs, multiple providers, custom components, tools and simple memory through the initial interface. |
| MS2       | S06          | A coherent product workspace for configuring and running the supported collaboration systems.                  |
| MS3       | S07          | Compare manual variants against task-specific quality, time and cost priorities.                               |
| MS4       | S08–S09      | Parallel collaboration and deep analysis of possible influence and result evolution.                           |
| MS5       | S10–S11      | Supported dynamic, event-driven and resumable workflows.                                                       |
| MS6       | S12          | Automatic bounded proposal and evaluation of improvements.                                                     |
| MS7       | S13–S16      | Prompt/graphical authoring, supported Python export and single-owner server execution.                         |

The main evaluation objective becomes usable at MS3, deep analysis at MS4 and the
automatic improvement loop at MS6. The S06 workspace precedes these outcomes;
advanced authoring and deployment follow at MS7.

The [previous plan](sprint-roadmap-20261002-r1.md#indicative-delivery-schedule)
preserves the original 80–160 active-hour forecast from the start of S03. That
forecast omitted the explicit product-workspace scope and included S03, which is
now functionally closed. It is not a current estimate of remaining work. Updated
durations and calendar targets remain uncommitted until the affected scope and
available capacity are reviewed during sprint preparation.

Planning estimates must include analysis, specification, implementation, review,
corrections, testing, documentation and necessary tool waits. Concurrent
implementer activity is not added to elapsed duration. Inactive periods and waits
for owner decisions shift calendar dates and remain outside active elapsed time.
Recalibrate at each milestone and retain the previous forecast and deviations;
do not infer a productivity gain from the working method or from parallelism alone.

## Preparation, scheduling and closure

Before each sprint, resolve its affected [open decisions](open-questions.md),
approve the final scope and prepare contracts, acceptance criteria, ownership and
module tickets. Include the end-to-end user journey and failure/recovery behavior
in that preparation. Planning this workspace does not require implementing every
future graph profile or resource type in S06.

Every delivery preserves mandatory engineering gates, English documentation,
managed mediation and configured deadlines/budgets. Any paid demonstration stays
within the remaining existing USD 3 authorization. Python export deliberately
removes platform logging, intermediation and supervision for its supported profile.
Analysis distinguishes observed, reported and inferred evidence; unavailable
reasoning is not reconstructed and influence is not claimed as proven causality.

Future details remain open under Q15 (evaluation, analysis and optimization), Q16
(control, communication and deployment), Q21 (export), Q22 (tools/memory) and Q23
(product workspace). The second provider/profile is selected before S04. Advanced
memory integrations, additional protocols and multi-user operation remain later
extensions.

## Revision history

| Revision | Date       | Change                                                                                                                                                           |
| -------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 4        | 2026-10-02 | Record the owner-authorized S06 product completion within its existing scope; later sprint assignments unchanged. |
| 3        | 2026-10-02 | S04–S06 initial local delivery checkpoint, preserved in the previous-plan snapshot. |
| 2        | 2026-10-02 | Owner-requested product workspace added as S06; former S06–S15 moved to S07–S16; user-interface delivery, dependencies, milestones and estimation basis updated. |
| 1        | 2026-10-02 | [Preserved plan](sprint-roadmap-20261002-r1.md) before the product-workspace replan, including the original forecast and S03 closure checkpoint.                 |
