# Architecture overview

**Status: Approved first-cycle architecture.** This view follows [arc42](https://arc42.org/overview/). Architectural requirements are binding; mechanisms marked proposed remain subject to approval.

## 1. Introduction and goals

The system supports experiments that improve agent collaboration according to task-specific quality, time, cost, and other objectives. Initial work establishes a configurable execution and observation foundation. Later cycles compare graph variants and automate experimentation.

The [requirements](../specification/requirements.md) identify stakeholders, functional scope, and the distinction between first-cycle work and future capabilities. Principal quality goals are extensibility, traceability, bounded execution, clear visual inspection, and maintainability.

## 2. Constraints

- The local application implements the approved first cycle; later capabilities remain deferred.
- Start locally, with one user, trusted components, and one active workflow.
- Use Python/FastAPI for the backend and React/TypeScript/React Flow/Vite for the frontend.
- Graph definitions are editable, versioned JSON, independent of React Flow serialization.
- Managed communication, including model access, passes through platform control.
- Preserve the [mandatory engineering baseline](../../../../README.md#engineering-standards), including the seven reference TypeScript rules without narrowing their scope.
- Budget and deadline values are configurable; no project defaults have been selected.

## 3. Context and scope

See the [C4 context and container views](views.md). The browser is an operator interface; components have independently controlled access to platform capabilities. External providers receive explicitly supplied inputs. Local deployment is not a claim that all experiment data stay on the machine.

## 4. Solution strategy

Use a small orchestration core with extension contracts. Separate definitions, configured instances, activations, graph revisions, and recorded evidence. Centralize authorization, scheduling, deadlines, spending reservations, and event persistence. Keep provider integrations and visual layout outside the domain model.

The first cycle supports finite sequences and bounded conditional routing. Policy-specific data belongs to versioned controller configuration, preserving room for future scheduling mechanisms.

Future [standalone Python export](../../../adr/0009-standalone-python-export.md) motivates keeping functional component logic independent of instrumentation, application services and client routing. The selected export profile generates direct calls and removes platform logging, intermediation and supervision. Export implementation is deferred; platform-managed execution retains its first-cycle process, mediation and supervision requirements.

## 5. Building block view

These are logical responsibilities. The source layout and enforced dependency direction are defined in the module-boundary contract; they do not imply independently deployed microservices.

| Responsibility           | Owns                                                                                                                      | Public interactions                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Definitions and registry | Component descriptors, immutable graph versions, static validation and manual lineage                                     | Resolve types, read bundled/personal definitions and save validated revisions |
| Execution                | Run and activation lifecycle, scheduling, deadlines                                                                       | Start, request stop, receive authorized outcomes                              |
| Access and routing       | Caller identity, scoped discovery, invocation policy                                                                      | Resolve permitted capabilities and dispatch requests                          |
| Accounting               | Reservations, usage, charges, scope balances                                                                              | Authorize bounded spending and settle actual usage                            |
| Observation              | Events, payload references, read models                                                                                   | Append evidence and supply authorized inspection                              |
| Integration adapters     | MCP, model providers, compatibility APIs, persistence                                                                     | Translate external formats at validated boundaries                            |
| Browser features         | Structured/JSON configuration, revision selection, graph views, inspectors, resources and session/run/settings navigation | Use bounded application APIs and status updates                               |

Only public module APIs may be used across responsibilities. Domain code must not import web frameworks, provider SDKs, UI types, or storage implementations. A composition root wires implementations. The [module-boundary contract](module-boundaries.md) defines the implemented directories, dependency direction, public entry points and placement checks.

S03's [personal experiment library](../contracts/personal-experiments.md) composes
bundled definitions with SQLite-owned personal revisions behind a common reader.
Static authoring validation checks declared contracts without launching installed
components. Execution preparation independently resolves installations, effective
schemas and limits, then freezes the selected exact revision. Browser authoring
uses raw canonical text and backend-generated drafts to preserve numeric values
across Python and JavaScript. Runtime evidence continues to refer to the admitted
snapshot rather than the current editor or library selection.

S04–S06 adds the [workspace](../contracts/product-workspace.md) application boundary
for trusted discovery, source-preserving patches and transactional limit commands.
[Model policies](../contracts/model-resources.md) select provider-specific request
and billing behavior behind a common model-resource host; immutable per-model
tariffs remain separate from historical charges. [Resource binding](../contracts/tools-memory.md)
resolves run-local or persistent namespaces before independent calculator, memory
and composed-agent processes launch. Child bindings and grants remain explicit;
configuration discovery does not expose credentials or confer authority.

## 6. Runtime view

The [runtime scenarios](runtime.md) cover validation, the three-activation example, nested calls, budget denial, cancellation, and restart. The [execution and evidence contract](../contracts/execution.md) proposes state and event semantics.

## 7. Deployment view

Initially the operator runs the backend on the local machine and opens a browser interface served by it. The owner selected local SQLite behind backend persistence interfaces; [ADR 0011](../../../adr/0011-local-persistence.md) records that choice and proposes its detailed settings and recovery semantics. Independent local component processes are required from the first cycle by [ADR 0004](../../../adr/0004-component-packaging.md).

The [MCP profile proposal](../contracts/mcp-profile.md) distinguishes the platform-to-component transport from calls made by components back to the platform. Components use familiar model/tool client interfaces through platform adapters with the same authorization, accounting and observation controls. One component process is not inherently one agent, session, or activation.

Server hosting, container isolation, remote component deployment, and multiple users require later deployment decisions. No claim of untrusted-code isolation applies to the initial local process model.

## 8. Crosscutting concepts

| Concept                                                    | Specification                                              |
| ---------------------------------------------------------- | ---------------------------------------------------------- |
| Component identities, state, memory bindings               | [Component contract](../contracts/components.md)           |
| Host readiness, invocation reuse, process teardown         | [Component lifecycle](../contracts/component-lifecycle.md) |
| Caller identity, permissions and causal context            | [Call authority](../contracts/call-authority.md)           |
| Graph definitions, revisions, control policy               | [Graph contract](../contracts/graphs.md)                   |
| Protocol, discovery, and interoperability                  | [MCP profile](../contracts/mcp-profile.md)                 |
| Accounting, cancellation, observability                    | [Execution contract](../contracts/execution.md)            |
| Tariffs, monetary precision, periods and settlement        | [Accounting policy](../contracts/accounting-policy.md)     |
| Persistence transactions and crash recovery                | [Storage proposal](../../../adr/0011-local-persistence.md)       |
| Event catalog, capture completeness and reported internals | [Observation contract](../contracts/observation.md)        |
| Live graph and historical inspection                       | [Visual model](visual-model.md)                            |
| Secrets, instruction boundaries, trust                     | [Initial threat model](security.md)                        |

## 9. Architectural decisions

The [MADR index](../../../adr/README.md) records accepted principles and independent-process packaging separately from proposed detailed contracts, execution mechanisms, and transport choices. Accepted means an agreed decision, not an implemented feature.

## 10. Quality requirements

[Quality scenarios](quality.md) give stimuli, required responses, and proposed acceptance checks. Numeric limits remain operator-configured where agreed; performance and scale targets still need selection.

## 11. Risks and technical debt

[Risks](risks.md) record uncertainty about SDK support, incomplete instrumentation, cancellation, shared state, trace volume, visual complexity, and evaluation validity. There is no implementation debt yet. Open decisions are not silently represented as resolved design choices.

## 12. Glossary

The [glossary](glossary.md) distinguishes terms that must not become interchangeable: graph versus result graph, component type versus instance, node versus activation, and work session versus agent conversation.

## S06-UX target architecture — 2026-10-02

The [implemented workspace design](../specification/s06-workspace-redesign.md) retains
the existing C4 containers and runtime boundaries. Within the browser, app owns
selection/navigation, definition-editor owns the single draft, experiment-library
owns collection/version views, and graph/execution/inspector remain separate
features. The backend adds read models through application.library and existing
operator queries, with optional presentation normalization in application.workspace.
See [ADR 0013](../../../adr/0013-workspace-authoring-state.md) and the
[module map](module-boundaries.md#s06-ux-target-module-map). The owner-authorized implementation and mandatory verification are complete;
[S06 delivery evidence](../progress/sprint-06-status-report.md) retains the scope
and limits. Owner usability acceptance remains separate.
