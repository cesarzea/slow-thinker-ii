# Open questions and closure register

**Status: First-cycle baseline approved on 2026-09-28; local first-cycle delivery verified.** Owner: Cesar Zea. The owner approved the consolidated closure after selecting daily automatic tariff imports. Remaining first-cycle technical details are implementation and verification obligations within that scope, not additional approval gates.

## First-cycle decisions

| ID | Question / current recommendation | State | Closure evidence |
| --- | --- | --- | --- |
| Q01 | Independent local component processes from the first cycle, with familiar outgoing client calls mediated by the orchestrator. | Closed: approved 2026-09-27 | Explicit owner selection; [accepted ADR 0004](../adr/0004-component-packaging.md). Detailed contracts remain Q04–Q06 and Q17. |
| Q02 | Begin with bundled example graphs selected and visualized in the application. Add an editing tool and manual JSON upload later. | Closed: approved 2026-09-27 | Explicit owner instruction; [four initial graph definitions](../contracts/examples/README.md) and the updated visual workflow. |
| Q03 | Automatically import and update the Vercel catalogue once per day; validate the billing profile and retain immutable local tariff revisions for each run/attempt. See [accounting policy](../contracts/accounting-policy.md#tariffs-and-trustworthy-bounds). | Closed: source and daily automatic updates approved 2026-09-28 | Explicit owner instruction (translated): “Import and update those tariffs automatically once per day”. During implementation verify daily/startup refresh, invalid-source handling and unchanged running/historical tariff revisions. |
| Q04 | Review the [MCP profile](../contracts/mcp-profile.md#sdk-candidate-and-conformance-work), [tested SDK matrix](../contracts/sdk-compatibility.md) and [OpenAI profile](../contracts/openai-initial-profile.md), including the published-capacity reservation strategy. Resolve platform error envelopes. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Approved ADR 0007, pinned dependencies and complete interoperability cases; no silent MCP downgrade |
| Q05 | Review the [component lifecycle](../contracts/component-lifecycle.md): reused hosts with fresh stateless LLMCall objects/clients, startup/readiness, busy-ancestor rejection and independently retained resource data. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Lifecycle acceptance cases, QA04, QA11, QA22–QA24; real host lifecycle and recovery are covered by the implementation verification record |
| Q06 | Review [call authority](../contracts/call-authority.md): per-invocation grants, isolated clients, generated tool aliases, filtered discovery and revocation. Finalize credential delivery and browser access separately. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | QA03/QA14/QA24 and CP04; no payload-asserted identity |
| Q07 | Review the [accounting policy](../contracts/accounting-policy.md): currency/calendar, exact amounts, admission-month attribution and the [conservative reservation tradeoff](../contracts/openai-initial-profile.md#proposed-initial-bound-published-model-capacity). | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Approved policy and explicit provider assumptions; examples cover equality, simultaneous calls, month boundaries, missing costs, corrections and reserve versus charge |
| Q08 | Review the [transition/race policy](../contracts/execution.md#transition-and-race-policy), budget-stop outcome, late responses, separate cleanup and settlement, and no automatic ambiguous replay. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Approved table and QA07–QA08/QA23; runtime race coverage is recorded in the implementation verification record |
| Q09 | Review [ADR 0011](../adr/0011-local-persistence.md): local SQLite, backend-only access, short transactions, explicit dispatch intent, crash recovery and preserved accounting. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Owner engine selection recorded; review T1–T5 failure cases and QA25, then implementation verification |
| Q10 | Review the [observation contract](../contracts/observation.md): event catalog, internal reports, capture statuses, redaction, storage failure and proposed retention until explicit deletion. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Approved payload/retention contracts and inspection acceptance cases; QA05/QA26 execution follows implementation |
| Q11 | Review the [visual proposal](../architecture/visual-model.md) and [operator API](../contracts/operator-api.md): linked views, command receipts/withdrawal, consistent projections, paging and reconnection. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Approved interaction/API model, QA12–QA13/QA27 journeys and Q18 targets; the UI and server are implemented; acceptance evidence belongs to the verification record |
| Q12 | Run, saved work-session and monthly budgets cover only managed Slow Thinker II calls. The original executor remains independent, with no shared accounting integration. | Closed: approved 2026-09-28 | Explicit owner selection: “Solo slow thinker ii”; R23 and QA17 define the scope and its verification |
| Q13 | Review the [LLMCall contract](../contracts/llm-call.md), effective instance schemas and graph/controller contracts. Approve and apply the [model-result revision](../contracts/openai-initial-profile.md#response-preservation-and-functional-interpretation) preserving the native response through MCP. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | ADR 0005 review, revised model schema/fixtures and semantic checks; provider/error mappings remain Q04/Q08 |
| Q14 | Review the [directory/module proposal](../architecture/module-boundaries.md), configure all mandatory gates and select one verification entry point. Standards themselves are already mandatory. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | QA16/QA28 failing-violation demonstrations, location manifest and local/CI parity before application code |
| Q17 | Review [installation](../contracts/component-installation.md#proposed-environment-and-installation-policy): uv, exact hashed wheel locks, independent immutable environments and direct host launch; close registration/resolution and bootstrap schemas. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | ADR 0004, registration fixtures, CP01 and QA23; approved preparation/publication rules and real host acceptance cases |
| Q18 | Explicit performance and capacity targets: graph size, payload/schema bounds, status delay and storage volume. Do not invent numbers. | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | Measurable limits in quality scenarios |
| Q20 | Review the [typed Python API](../contracts/python-component-api.md), GroundedReview specimen, base metadata and [explicit environment-update policy](../contracts/component-installation.md#updates-repetition-and-removal). | Closed: first-cycle baseline approved 2026-09-28; implementation evidence in the verification record | [ADR 0008](../adr/0008-component-inheritance-and-versions.md), registration/schema checks and QA19; the component SDK and loader are implemented; acceptance evidence belongs to the verification record |

## Decisions for later functional cycles

| ID | Question | Boundary to preserve now |
| --- | --- | --- |
| Q15 | Comparison datasets, metrics and weights, repeated trials, evaluator trust, attribution uncertainty, automatic variant proposals and stopping criteria. | Run/configuration/evidence lineage; analysis calls use the same accounting controls |
| Q16 | Dynamic control, messages/events/queues, joins, shared-memory concurrency, pause/resume, reusable subgraphs, containers and multiple users. | Versioned control/component contracts; no assumptions that every future workflow is a sequence or DAG |
| Q19 | License, distribution, contribution workflow and first public release. | Apache 2.0 selected; publication authorized as cesarzea/slow-thinker-ii with Cesar Zea authorship. No released functionality is claimed; release assurance applies from the first release |
| Q21 | Standalone Python export: direct calls with no platform logging, intermediation or supervision are selected. Specify supported components/control profiles, generated project structure, direct client binding, state/resource dependencies and verification of functional behavior and removed overhead. | [ADR 0009](../adr/0009-standalone-python-export.md); separate functional logic from instrumentation and platform services now; no first-cycle exporter |
| Q22 | Select the first concrete tool and memory/context plugin for a near-term functional cycle, and decide their invocation policy, sharing, persistence and inspection examples. Recommendation: one deterministic tool and a simple explicit memory resource before a richer provider integration. | R03, R08–R10; component-specific operations, mediated calls and generic inspection now; a model-driven tool loop must declare additional calls and stopping rules |

## First-cycle extension: review with conditional routing

Scope approved by the owner on 2026-09-29: include the redirector component and a
bounded proposer–reviewer loop in the first functional cycle. The local implementation is verified; the existing finite-sequence profile remains supported.

Proposer and reviewer use ordinary `LLMCall` functionality, configured independently.
The redirector is usable independently or embedded inside another component. Its
user-authored deterministic Python script selects among explicitly declared
outputs. The containing graph or agent defines their destinations. In this example,
the reviewer embeds the redirector; the principal graph shows the agents and their
outgoing routes. Rejected proposals return with reviewer observations; accepted
proposals exit. Managed calls remain mediated and recorded by the platform.

The [conditional routing implementation contract](../contracts/conditional-routing.md)
now specifies script input/return shape and packaged loading, mediated composition,
activation-specific bindings, script errors, configurable limits and exhaustion,
and collapsed/expanded presentation for the delivery sprint. These are technical
selections within the approved extension; implementation and local delivery verification are complete. Execution remains subject to configured deadlines and budgets.
Determinism is a component contract, not a guarantee provided by arbitrary Python.
The earlier suggestion of at most three proposals, per-requirement findings and
particular model choices remains a recommendation, not an approved fixed setting.

## Closure procedure

Resolve first-cycle blockers through explicit decisions, update affected ADRs/contracts/examples, and rerun structural and semantic review checks. Record the selected option and its acceptance evidence here. Future scope can remain deferred when its boundary is explicit.

The State column distinguishes selections from unresolved design details. References to future executable tests are verification obligations, not a requirement to implement the product before its specification can close. Close a design question when its decision, contract, acceptance criteria and verification method are approved; keep implementation evidence in the verification record. Temporary feasibility probes can inform a decision but cannot substitute for product tests.

The consolidated approval accepts USD/calendar months in UTC, conservative reservations and retention until explicit deletion for the first cycle. Daily automatic Vercel imports supersede the earlier manual-tariff proposal. Future-cycle questions remain open.

Application implementation is authorized by the explicit owner approval. Earlier Draft/Proposed labels describe the review origin; they do not replace executable verification or indicate approval of future-cycle features.
