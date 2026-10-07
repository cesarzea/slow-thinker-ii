# Architecture of the core

| Document control | Value                                                              |
| ---------------- | ------------------------------------------------------------------ |
| Document ID      | ARCH-CORE                                                          |
| Revision         | 1                                                                  |
| Owner            | Cesar Zea                                                          |
| Date             | 2026-10-04                                                         |
| Structure        | [arc42](https://arc42.org) with [C4](https://c4model.com) views    |
| Previous edition | [Architecture of the previous implementation](../archive/previous-implementation/architecture/README.md) |

## 1. Introduction and goals

Slow Thinker II lets users build graphs of collaborating components, run them under
supervision and analyse what happened, as defined in the
[requirements](../specification/requirements.md). The core's quality goals, in
order: complete and truthful recording of every interaction; extensibility by
independently packaged components; bounded execution (time, activations, money);
a configuration experience free of technical plumbing; maintainability under the
mandatory engineering standards.

## 2. Constraints

- The [engineering standards](../../README.md#engineering-standards) apply without
  exception, including small units, coverage and the single verification command.
- Python 3.13 with FastAPI for the platform; React, TypeScript, React Flow and Vite
  for the browser interface ([ADR 0003](../adr/0003-local-application-stack.md)).
- Components run as separate processes speaking MCP ([ADR 0004](../adr/0004-component-packaging.md),
  [ADR 0007](../adr/0007-mcp-profile.md)); the protocol stays container-ready
  ([ADR 0023](../adr/0023-container-ready-component-boundary.md)).
- Local SQLite persistence behind backend ports ([ADR 0011](../adr/0011-local-persistence.md)).
- S06 is single-user and local, with trusted components.

## 3. Context and scope

See the [context and container views](views.md). The operator uses the browser
interface. The platform calls model providers over HTTPS with server-side
credentials. Component hosts are local processes launched per run.

## 4. Solution strategy

- A pure, asynchronous **engine** schedules message deliveries and activations of
  a compiled graph and knows nothing of HTTP, SQLite or processes
  ([ADR 0017](../adr/0017-message-driven-execution.md)).
- A pure **graph** module parses and validates [graph documents](../contracts/graph-document.md)
  against component declarations and the LLM catalog, and compiles run plans
  ([ADR 0016](../adr/0016-graph-document-model.md)).
- **Authorization** is derived from the plan: grants identify an activation and
  allow exactly the deliveries and service entries the graph declares
  ([ADR 0018](../adr/0018-derived-authorization.md)).
- The **LLM gateway** mediates every model call: authorize, validate, reserve,
  dispatch, settle, record ([ADR 0019](../adr/0019-platform-llm-service.md),
  [ADR 0022](../adr/0022-budgets-and-request-reservations.md)).
- An append-only **event log** per run is the single source for results, totals
  and activity ([ADR 0021](../adr/0021-supervision-and-recording.md)).
- The interface renders component declarations with a fixed control vocabulary
  ([ADR 0020](../adr/0020-declared-component-configuration.md)).

## 5. Building block view

The [module boundaries](module-boundaries.md) define packages, dependency rules and
public entry points. In summary:

| Layer         | Packages                                                       | Responsibility                                                         |
| ------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Composition   | `bootstrap`                                                    | Configuration and wiring                                               |
| Adapters      | `adapters.http`, `adapters.sqlite`, `adapters.hosts`, `adapters.providers`, `adapters.installations` | HTTP, persistence, component processes, provider transports, installed packages |
| Application   | `application`                                                  | Use cases: graph library, runs, LLM gateway, reports, usage; port definitions |
| Engine        | `engine`                                                       | Run scheduling, activation pipeline, limits and termination            |
| Domain        | `graphs`, `catalog`, `access`, `accounting`, `contracts`       | Graph documents and plans, declarations and LLM catalog, grants, money and budgets, JSON values |
| Components    | `components/host`, `components/llm-call`, `components/router`, `components/memory` | Host SDK and the component packages                      |
| Interface     | `frontend/src/{app,features,api,ui}`                           | Graph list, editor, run and activity views                             |

## 6. Runtime view

The [runtime scenarios](runtime.md) follow journey J3: saving a graph, starting a run,
an activation with an embedded Router, a model call, a loop, completion and the
activation-limit stop.

## 7. Deployment view

One backend process serves the compiled interface and the APIs on loopback. It
launches component hosts from installed, hash-verified environments under
`.local/components` and stores state in `.local/state.sqlite3`. Model providers are
reached over HTTPS from the backend process only.

## 8. Crosscutting concepts

| Concept                              | Specification                                              |
| ------------------------------------ | ---------------------------------------------------------- |
| Graph documents and diagnostics      | [Graph document](../contracts/graph-document.md)           |
| Component declarations and screens   | [Component declaration](../contracts/component-declaration.md) |
| Messages, activations and limits     | [Execution](../contracts/execution.md)                     |
| Host launch, operations and reports  | [Component protocol](../contracts/component-protocol.md)   |
| Model calls and providers            | [LLM service](../contracts/llm-service.md)                 |
| Money, budgets and tariffs           | [Accounting](../contracts/accounting.md)                   |
| Event log                            | [Recording](../contracts/recording.md)                     |
| Browser API                          | [Operator API](../contracts/operator-api.md)               |
| Threats and controls                 | [Security](security.md)                                    |

## 9. Architectural decisions

[ADR 0015](../adr/0015-new-execution-core.md) to [ADR 0023](../adr/0023-container-ready-component-boundary.md)
define the core. Earlier records remain in the [decision log](../adr/README.md).

## 10. Quality requirements

[Quality scenarios](quality.md) give stimuli, expected responses and their checks.

## 11. Risks and technical debt

| Risk                                                                                   | Mitigation                                                                          |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Local processes are not a sandbox; a Router script runs user code                      | S06 is single-user and trusted; container isolation is planned for S08 and S18            |
| The byte-level tokenization assumption under-reserves a provider that breaks it         | Recorded per provider; overruns are recorded and stop the run when a budget is exceeded |
| Reused subsystems carry assumptions of the previous model                              | Each reused module is reviewed against the new contracts and keeps its tests         |
| Concurrent activations expose races in the engine and the ledger                       | Pure engine tests with controlled scheduling; ledger admission in one transaction    |
| Holidays are not modelled in DeepSeek tariffs                                           | Charges stay at or above the provider's price; documented                           |

## 12. Glossary

See the [glossary](glossary.md).
