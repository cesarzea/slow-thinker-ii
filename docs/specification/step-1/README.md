# Step 1 delivery: build, run and inspect graphs

| Document control | Value                                                                        |
| ---------------- | ---------------------------------------------------------------------------- |
| Document ID      | STEP-1                                                                       |
| Revision         | 2                                                                            |
| Owner            | Cesar Zea                                                                    |
| Date             | 2026-10-04                                                                   |
| Status           | Accepted by the owner on 2026-10-07 — see the [sprint report](sprint-report.md) |
| Method           | [M07](../../continuous-improvement/methods/007-validated-journeys.md); cycle [C12](../../continuous-improvement/cycles/012-core-step-1/report.md) |
| Journeys         | [Validated version 1](../core-step-1-journeys/README.md), V01–V12            |

## Objective

Deliver the validated journeys end to end: build and configure graphs of Trigger,
LLM Call, Router and Output nodes in the editor, save versions, run them under
supervision with limits and budgets (step 1.1), and inspect each run's activity
(step 1.2). The [architecture](../../architecture/README.md), decisions 0015–0023
and the [contracts](../../contracts/README.md) define the design.

## Acceptance criteria

Each criterion cites the journeys and validation points it implements.

| ID    | Criterion                                                                                                                                                                                                                         | Source                 |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| AC01  | A user creates a graph, adds Trigger, LLM Call and Output from the palette, connects ports by dragging, configures the nodes through their dialogs, saves version 1, runs it and sees the result under the Output's name.          | J1, V01, V04           |
| AC02  | The LLM Call dialog has the sections Prompt, Model, Input format and Output format. Model lists the catalog's LLMs and renders the selected entry's parameter schema inline; DeepSeek's Temperature is disabled unless Reasoning is `none`. | J1, V05                |
| AC03  | The LLM Call sends its prompt as the system message and the received message as the user message; JSON output is validated against its schema and an invalid reply fails the activation and is kept. | V06, ADR 0010          |
| AC04  | Add component offers only components embeddable at the node's output. Adding a Router adds its sections, marked embedded, to the node's dialog and replaces the node's output ports with the Router's outputs. Removing it lists the affected connections and removes them on confirmation. | J2, V07                |
| AC05  | The Router calls `route(received, node_input)` and emits the returned content on the returned output. An undeclared output, a malformed result or an exception fails the activation and the run, with the detail shown. | J2, V08                |
| AC06  | A connection may lead back to an earlier node. The review loop of J3 completes when the Reviewer accepts; when it never accepts, the run stops at the activation limit with that status and reason shown. | J3, V03, V09           |
| AC07  | The Limits dialog edits activations, running nodes, time limit and run budget; daily and monthly budgets come from the platform configuration and their usage is visible. | J3, V09                |
| AC08  | The run dialog shows the Trigger's message, editable for that run only. Runs complete when no message is pending and no node is running; they stop, fail or are cancelled with a reason and detail; Stop cancels a running run. | V02, V03               |
| AC09  | Save creates a new immutable version. A run uses the last saved version; with unsaved changes, Run offers Save and run. Unsaved changes survive a page reload in the same browser. | V10                    |
| AC10  | The activity view lists, in order, messages, activations, model calls with expandable request, reply, tokens, cost and duration, Router decisions, component reports marked as reported, and the run's end, with per-node activations and cost and run totals. | Step 1.2, V11          |
| AC11  | No permission, slot, wrapper, platform identifier or raw JSON editor appears in ordinary configuration. A component cannot call an LLM other than the one its configuration selects. | V04, V07, ADR 0018     |
| AC12  | Every model call reserves its bound against the run, day and month budgets before dispatch, records its cost and applied rates, and a denial stops the run naming the budget. | V09, ADR 0022          |
| AC13  | All interface text is English. The complete verification runner passes on the final source with unchanged thresholds, and browser journeys cover J1, J2, J3, the limit case and the activity view with the simulated provider. | V12, CR18              |

## Criteria changed by the owner's review

The owner's review on 2026-10-04 and 05 changed how some criteria are met; the
[sprint report](sprint-report.md) and ADRs 0024–0026 record the decisions.

| ID   | As reviewed                                                                                                         |
| ---- | ------------------------------------------------------------------------------------------------------------------- |
| AC01 | Every edit is saved as it is made; the run is started from run mode and its result read in the run panel.            |
| AC04 | Add component offers the components embeddable at the node's free positions: output, and now memory.               |
| AC07 | Run limits are edited in the Graph panel shown without a selection, instead of a Limits dialog.                     |
| AC08 | Run enters run mode; Execute runs what is on screen, asking for the message only when the Trigger says so.          |
| AC09 | There is no Save: every edit is a stored change, versions are activated on purpose, and runs execute the latest change. |
| AC10 | The activity page is reached by the run's address; run mode's observation points show events live.                 |

## Delivery modules

See [module boundaries](../../architecture/module-boundaries.md). Assignments are in
[assignments](assignments.md).

## Verification

- Unit and contract tests are written with the code (M07 P15). Each module passes its
  scoped gates before delivery.
- Integration tests cover persistence, the HTTP API, the LLM gateway with the
  simulated provider, real component hosts, and restart recovery.
- Browser journeys use the real backend with the simulated provider; component hosts
  run from the development environment's packages, so journeys need no wheel
  installation or network access. Automated tests cover installation with fixture
  wheels. Acceptance also runs a graph on hosts installed by `make components`, which
  downloads hash-locked dependency wheels, and records the result.
- The complete runner (`make verify`) runs on the final source state.
- A demonstration with the real OpenAI and DeepSeek providers runs J1–J3 within the
  existing paid authorization once the owner provides credentials.

## Out of scope

Shared context and memory, tools and MCP servers for nodes, joins, threads and
queues, several triggers, batch runs, API execution, users and billing, containers,
export, component inheritance and automatic tariff import.
