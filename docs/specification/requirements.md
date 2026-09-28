# Requirements and scope

**Status: First-cycle scope approved 2026-09-28; implementation in progress.**

## Purpose

Create a flexible, extensible platform for investigating and improving collaboration between agents. Users should be able to identify the configurations that work best for a task according to their chosen priorities: result quality, execution time, cost, or other criteria.

The intended progression is: define and evaluate collaborative systems; create and compare variants; automate the proposal and evaluation of further variants. Deep analysis supplies evidence for this improvement loop. There is no universal definition of the best graph or a promise to find a global optimum.

A later Export as Python capability should turn a selected graph into a complete, independently executable Python application. Its primary optimization removes platform logging, intermediation and supervision while preserving functional graph logic and explicit dependencies. It is a future deployment path for experiment results, not a first-cycle feature.

## Stakeholders

| Stakeholder | Need |
| --- | --- |
| Experiment designer | Express a collaboration process and choose its evaluation criteria. |
| Component author | Add agents, resources, control mechanisms, and collaboration techniques through documented contracts. |
| Experiment analyst | Inspect what happened, compare versions, and distinguish evidence from interpretation. |
| Maintainer | Develop an inspectable, modular system with the engineering controls required from the outset. |

## Recorded requirements

Identifiers below describe requirements, not implementation completion. “Boundary now” means the design must accommodate later capabilities without pretending to implement them in the first cycle.

| ID | Requirement | Delivery boundary |
| --- | --- | --- |
| R01 | Define experiments, run them, and inspect behavior and results. | First cycle |
| R02 | Use independent, user-defined component types and configured instances, packaged separately and executed in local processes outside the backend. | Independent processes from the first cycle; detailed packaging contract pending |
| R03 | Support agents, resources, memory/context providers, flow controllers, and collaboration techniques as extension roles. | Boundary now; expand implementations in cycles |
| R04 | Define a graph per experiment; ultimately support arbitrary topology, conditions, parallelism, deliberate loops, and runtime changes. | Finite sequences first; no universal DAG restriction |
| R05 | Route managed component interactions through the platform, including access to model providers. | First cycle |
| R06 | Expose component MCP capabilities through a platform proxy, filtered by graph permissions. | First cycle; precise profile pending |
| R07 | Use the current stable MCP revision, with explicit compatibility and capability support. | Protocol contract before implementation |
| R08 | Let components call LLMs, agents, tools and resources through the orchestrator using familiar client interfaces; preserve supported OpenAI and LangChain call signatures and their use inside LangGraph nodes. Apply the same controls to external clients. | Chat Completions and basic model/tool invocation from component processes first; exact SDK, parameter and error coverage must be explicit |
| R09 | Make memory and context optional, private or explicitly shared; agents choose the information sent in their calls. Keep resource sharing, state retention and host-process lifetime distinct. | Binding model now; tools and memory are near-term extensions; concrete memory implementations later |
| R10 | Distinguish independent calls, serialized stateful execution, and other declared concurrency modes. | Stateless agents first; reject unsupported modes |
| R11 | Record managed calls and available internal instrumentation, including exposed reasoning and state. | First cycle; internal reporting is component-dependent |
| R12 | Keep observed, component-reported, and inferred evidence distinguishable. Recording does not grant agents access to the trace. | First cycle |
| R13 | Enforce configurable deadlines per call and per run, including waiting and retries. | First cycle |
| R14 | Account for managed billable attempts and enforce budgets per run, saved work session, and month. | First cycle |
| R15 | Stop the whole run when further work cannot be authorized by a budget; preserve evidence and outstanding costs. | First cycle |
| R16 | Persist work sessions, run configurations, history, and results across interface restarts. | First cycle |
| R17 | Store graph definitions as editable JSON. Start with bundled example graphs; later provide an editing tool and manual JSON upload, with prompt-based and full graphical authoring in the intended evolution. | Select bundled examples first; user editing and upload later |
| R18 | Represent graphs visually from the first functional version, live and after execution. | First cycle |
| R19 | Distinguish logical participants, activations, permitted connections, control flow, and actual communications. Preserve positions while readable; reflow when needed. | Basic linked views first |
| R20 | Start locally, with one user and one active workflow; keep history inspectable. | First cycle |
| R21 | Use Python/FastAPI and React/TypeScript/React Flow/Vite, with a graph format independent of the UI library. | First cycle |
| R22 | Close the first-cycle specification before implementation; engineering requirements apply from the first implementation. | Immediate |
| R23 | Preserve the original project independently. Run, session and monthly budgets cover only managed Slow Thinker II calls, with no runtime or accounting dependency on the original executor. | Accepted scope: Q12, explicit owner selection 2026-09-28 |
| R24 | Create graph variants, compare their executions, then automate proposal and evaluation of variants. | Later cycles; identities and provenance needed now |
| R25 | Analyze information exchange, idea evolution, possible influence, outcome quality, time, and cost. | Trace foundation first; automated analysis later |
| R26 | Allow multiple plausible sources of an adopted idea; do not equate convergence with correctness or similarity with proven causality. | Analysis contract later; evidence semantics now |
| R27 | Support optional component implementation inheritance through code, with an exact base version or a compatible range bounded by a major version; retain the exact dependency resolution used by each run. | Basic single inheritance in the first cycle; extension and packaging contract pending Q20 |
| R28 | Export a complete supported graph as readable standalone Python code with direct calls and resolved component dependencies, removing platform logging, intermediation and supervision while retaining functional graph logic. | Later cycle; export direction selected; portability and generation details pending Q21 |
| R29 | LLMCall supports text or schema-validated JSON output. On invalid output return a structured failure, retain the received response and make no implicit repair call. Further calls require explicit configuration and normal accounting. | First cycle; policy accepted in ADR 0010; detailed API proposed |

Platform mediation, recording and supervisory requirements apply to platform-managed runs. R28 defines a separate future standalone profile that deliberately omits those services, including platform accounting, budget enforcement and watchdogs. Its build metadata identifies the source graph and dependencies without requiring runtime logging.

## First functional cycle

A configurable finite sequence uses two stateless LLM agent instances: one proposes, another reviews, and the first revises. This produces three distinct activations. The revised proposal receives the problem, original proposal, and review explicitly.

The executor must support other finite sequences and repeated use of components. It must not hardcode this example. The first UI offers [four bundled examples](../contracts/examples/README.md): single agent, handoff, review cycle and repeated review. Model access, costs, errors, and stops remain platform-managed.

The reference `LLMCall` component supports configurable instructions, model inputs/options and text/JSON output with explicit validation errors. Basic code inheritance lets a separately packaged component specialize its public extension points. Candidate [LLMCall and Python contracts](../contracts/llm-call.md), typed fixtures and a derived code specimen are ready for review; Q13 and Q20 must close the detailed implementation contracts.

The owner selected a very inexpensive OpenAI model for the initial integration on 2026-09-28. The [provider profile](../contracts/openai-initial-profile.md) proposes GPT-6 Luna; models remain configurable and other providers can be added through resource adapters.

This cycle includes selection and validation of bundled JSON graphs, live graph status, generic text/JSON inspection, saved history, and deadlines and budgets. Call outputs arrive complete; token streaming is not required. Closing the browser does not stop the backend. A backend restart marks unfinished runs interrupted; it does not imply automatic resumption.

## Deferred functional capabilities

Graph editing tools and manual JSON upload, parallel and conditional execution, runtime graph mutation, reusable subgraphs, memory-provider implementations, interactive pause/resume, historical navigation during a live run, automatic influence analysis, variant comparison, automatic graph improvement, standalone Python export, server/container deployment, and multiple users remain later work. These are functional deferrals; the engineering requirements are not deferred.

The owner clarified on 2026-09-28 that tools, memory and other resources must follow soon after the starting profile. Their extension boundaries belong in the initial design: components declare their own operations and bindings, managed calls remain mediated, and closing a run-owned process does not imply deleting persistent resource data. The first concrete additions and their acceptance examples remain to be selected; this clarification does not authorize application implementation or move every future capability into the first cycle.
## Evidence limits

Exposed reasoning can explain a component's reported rationale, including reliance on repeated endorsements. It is not a complete record of internal computation or conclusive causal proof. Independent arrival at the same idea remains possible. Missing internal evidence must be represented as unavailable, not reconstructed as fact.

The initial trust model requires cooperating local components. Complete mediation of their declared interactions does not establish OS-level containment of malicious code.

## Traceability

See [ADRs](../adr/README.md), [quality scenarios](../architecture/quality.md), [proposed contracts](../contracts/README.md), and [open questions](open-questions.md). The first-cycle closure is approved; acceptance still requires implementation and verification of the agreed behavior.
