# Documentation

**Status, 2026-10-07:** sprint S06, the new execution core, is accepted by the owner;
the [roadmap](specification/roadmap.md) plans S07–S25 and the next sprint is S07. Work
follows the [M07 method](continuous-improvement/methods/007-validated-journeys.md).

This page is the index of every maintained document; `make verify` fails when a
maintained Markdown document is missing from it or a link between documents is
broken. All maintained documentation is in English. Requirements, decisions,
contracts and implementation evidence are kept separate; a decision's acceptance does
not imply that it is implemented or verified. The previous implementation's documents
are [archived](archive/previous-implementation/README.md) and indexed there.

## Reading order

1. [Requirements](specification/requirements.md): what the platform is, why, and CR01–CR29.
2. [Roadmap](specification/roadmap.md): sprints S01–S25 and their milestones.
3. [Architecture](architecture/README.md): arc42 description with C4 views.
4. [Decisions](adr/README.md): the MADR log.
5. [Contracts](contracts/README.md): the boundaries between modules and with users.
6. [S06 delivery](specification/s06/README.md): the latest accepted sprint.
7. [Local development](development.md): how to run the platform.

## Repository

| Document | Contents |
| -------- | -------- |
| [README](../README.md) | What the platform is, its principles, current status and engineering standards |
| [AGENTS](../AGENTS.md) | Working rules for contributors and agents |
| [CONTRIBUTING](../CONTRIBUTING.md) | How to propose, implement, verify and submit a change; license of contributions |
| [CHANGELOG](../CHANGELOG.md) | Development progress and the sprint report versions |
| [Pull request template](../.github/PULL_REQUEST_TEMPLATE.md) | What every pull request describes |
| [Local development](development.md) | Build the components, configure and start the server, spending |

## Specification

| Document | Contents |
| -------- | -------- |
| [Requirements](specification/requirements.md) | Purpose, rationale, stakeholders and requirements CR01–CR29 |
| [Roadmap](specification/roadmap.md) | Sprints S01–S25, milestones and revision history |
| [Scope review of 2026-10-06](specification/scope-review-2026-10-06.md) | Scope dropped or reduced by revision 2 and the owner's decision on each item |
| [S06 journeys](specification/s06-journeys/README.md) | Validation record of the S06 journeys and their page |
| [S06 delivery](specification/s06/README.md) | S06 acceptance criteria and modules |
| [S06 assignments](specification/s06/assignments.md) | Module ownership during S06 |
| [S06 sprint report](specification/s06/sprint-report.md) | What S06 delivered, the owner's review and open items |
| [S06 verification record](specification/s06/verification.md) | Evidence per acceptance criterion and the complete runner's results |

## Architecture

| Document | Contents |
| -------- | -------- |
| [Architecture](architecture/README.md) | arc42 overview: goals, constraints, solution strategy and risks |
| [Context and container views](architecture/views.md) | C4 context and container diagrams |
| [Runtime scenarios](architecture/runtime.md) | How a run flows through the modules, following journey J3 |
| [Module boundaries](architecture/module-boundaries.md) | Source tree by capability and the allowed dependencies |
| [Quality scenarios](architecture/quality.md) | Measurable quality goals and how they are checked |
| [Security](architecture/security.md) | Threat model against the OWASP Top 10 for LLM applications, controls and planned changes |
| [Glossary](architecture/glossary.md) | Terms used across the documentation |

## Decisions

The [decision log](adr/README.md) lists every record with its status.

| Record | Decision |
| ------ | -------- |
| [0001](adr/0001-engineering-baseline.md) | Architecture documentation and engineering gates from the first implementation |
| [0002](adr/0002-platform-mediation.md) | Platform-mediated communication |
| [0003](adr/0003-local-application-stack.md) | Python backend and TypeScript browser application |
| [0004](adr/0004-component-packaging.md) | Independent component packages run as separate processes |
| [0005](adr/0005-versioned-contracts.md) | Versioned component, graph and run contracts |
| [0006](adr/0006-execution-and-accounting.md) | Separate execution state, spending reservations and evidence |
| [0007](adr/0007-mcp-profile.md) | MCP profile with explicit call directions |
| [0008](adr/0008-component-inheritance-and-versions.md) | Component inheritance with bounded versions (S22) |
| [0009](adr/0009-standalone-python-export.md) | Standalone Python export (S24) |
| [0010](adr/0010-llm-output-validation.md) | LLM output validation without implicit repair calls |
| [0011](adr/0011-local-persistence.md) | One local transactional store behind persistence interfaces |
| [0012](adr/0012-single-maintainer-review.md) | Review for a single-maintainer repository |
| [0013](adr/0013-workspace-authoring-state.md) | Authoring state of the earlier S06 scope (superseded) |
| [0014](adr/0014-component-owned-dialogs-and-composition.md) | Component-owned dialogs and composition (superseded) |
| [0015](adr/0015-new-execution-core.md) | A new execution core reusing verified subsystems |
| [0016](adr/0016-graph-document-model.md) | Graph documents of nodes, ports, connections and embedded components |
| [0017](adr/0017-message-driven-execution.md) | Message-driven asynchronous execution |
| [0018](adr/0018-derived-authorization.md) | Authorization derived from connections and declared uses |
| [0019](adr/0019-platform-llm-service.md) | Platform LLM service with provider-declared parameters |
| [0020](adr/0020-declared-component-configuration.md) | Component-declared configuration rendered by the platform |
| [0021](adr/0021-supervision-and-recording.md) | Supervision and recording by default |
| [0022](adr/0022-budgets-and-request-reservations.md) | Run, daily and monthly budgets with request-size reservations |
| [0023](adr/0023-container-ready-component-boundary.md) | Container-ready component boundary |
| [0024](adr/0024-working-copy-and-activated-versions.md) | Every change saved, with activated versions |
| [0025](adr/0025-runs-of-changes-and-run-mode.md) | Runs of changes, run mode and observation points |
| [0026](adr/0026-memory-position.md) | Memory as an embedded component position |
| [0027](adr/0027-functional-source-license.md) | Functional Source License |
| [0028](adr/0028-companies-users-and-workspaces.md) | Companies, users and workspaces |
| [0029](adr/0029-node-placement.md) | Placement of nodes in containers |

## Contracts

| Document | Contents |
| -------- | -------- |
| [Contracts](contracts/README.md) | Overview of the contracts and their examples |
| [Graph document](contracts/graph-document.md) | The JSON format of a graph, format 1 |
| [Component declaration](contracts/component-declaration.md) | How a component declares its ports, configuration and screens |
| [Component protocol](contracts/component-protocol.md) | The MCP operations between the platform and a component host |
| [Execution](contracts/execution.md) | Messages, activations, limits and how a run ends |
| [LLM service](contracts/llm-service.md) | Providers, models and their declared parameters |
| [Accounting](contracts/accounting.md) | Tariffs, reservations, charges and budgets |
| [Recording](contracts/recording.md) | The events a run records and their evidence |
| [Operator API](contracts/operator-api.md) | The HTTP API the browser interface uses, version 2 |

## Backend modules

Each module has a readme (purpose and public interface) and a specification
(behaviour and acceptance).

| Module | Contents | Documents |
| ------ | -------- | --------- |
| `access` | Invocation grants for derived authorization | [readme](../backend/src/slow_thinker_ii/access/readme.md) · [specification](../backend/src/slow_thinker_ii/access/specification.md) |
| `accounting` | Exact money arithmetic, tariffs and charges | [readme](../backend/src/slow_thinker_ii/accounting/readme.md) · [specification](../backend/src/slow_thinker_ii/accounting/specification.md) |
| `application` | Use cases and the ports the adapters implement | [readme](../backend/src/slow_thinker_ii/application/readme.md) · [specification](../backend/src/slow_thinker_ii/application/specification.md) |
| `bootstrap` | Server configuration, secrets and composition | [readme](../backend/src/slow_thinker_ii/bootstrap/readme.md) · [specification](../backend/src/slow_thinker_ii/bootstrap/specification.md) |
| `catalog` | Component declarations and LLM catalog entries | [readme](../backend/src/slow_thinker_ii/catalog/readme.md) · [specification](../backend/src/slow_thinker_ii/catalog/specification.md) |
| `contracts` | JSON values and pointers shared across boundaries | [readme](../backend/src/slow_thinker_ii/contracts/readme.md) · [specification](../backend/src/slow_thinker_ii/contracts/specification.md) |
| `engine` | The run scheduler | [readme](../backend/src/slow_thinker_ii/engine/readme.md) · [specification](../backend/src/slow_thinker_ii/engine/specification.md) |
| `graphs` | Graph documents, validation and run plans | [readme](../backend/src/slow_thinker_ii/graphs/readme.md) · [specification](../backend/src/slow_thinker_ii/graphs/specification.md) |
| `adapters.hosts` | Component hosts as local processes | [readme](../backend/src/slow_thinker_ii/adapters/hosts/readme.md) · [specification](../backend/src/slow_thinker_ii/adapters/hosts/specification.md) |
| `adapters.http` | The platform's HTTP surface | [readme](../backend/src/slow_thinker_ii/adapters/http/readme.md) · [specification](../backend/src/slow_thinker_ii/adapters/http/specification.md) |
| `adapters.installations` | Offline installation of component packages | [readme](../backend/src/slow_thinker_ii/adapters/installations/readme.md) · [specification](../backend/src/slow_thinker_ii/adapters/installations/specification.md) |
| `adapters.providers` | OpenAI, DeepSeek and simulated providers | [readme](../backend/src/slow_thinker_ii/adapters/providers/readme.md) · [specification](../backend/src/slow_thinker_ii/adapters/providers/specification.md) |
| `adapters.sqlite` | Graphs, runs, events and the budget ledger in SQLite | [readme](../backend/src/slow_thinker_ii/adapters/sqlite/readme.md) · [specification](../backend/src/slow_thinker_ii/adapters/sqlite/specification.md) |

## Frontend modules

| Module | Contents | Documents |
| ------ | -------- | --------- |
| `api` | Validated access to the operator API | [readme](../frontend/src/api/readme.md) · [specification](../frontend/src/api/specification.md) |
| `app` | The product shell, pages and routes | [readme](../frontend/src/app/readme.md) · [specification](../frontend/src/app/specification.md) |
| `features/activity` | The activity view and the live feed of observed points | [readme](../frontend/src/features/activity/readme.md) · [specification](../frontend/src/features/activity/specification.md) |
| `features/catalog` | The components page | [readme](../frontend/src/features/catalog/readme.md) · [specification](../frontend/src/features/catalog/specification.md) |
| `features/editor` | The graph editor and run mode | [readme](../frontend/src/features/editor/readme.md) · [specification](../frontend/src/features/editor/specification.md) |
| `features/graphs` | The graph list and new graphs | [readme](../frontend/src/features/graphs/readme.md) · [specification](../frontend/src/features/graphs/specification.md) |
| `features/history` | The runs list | [readme](../frontend/src/features/history/readme.md) · [specification](../frontend/src/features/history/specification.md) |
| `features/runs` | Run mode's panel | [readme](../frontend/src/features/runs/readme.md) · [specification](../frontend/src/features/runs/specification.md) |
| `features/versions` | The editor's History panel | [readme](../frontend/src/features/versions/readme.md) · [specification](../frontend/src/features/versions/specification.md) |
| `ui` | Shared presentation primitives | [readme](../frontend/src/ui/readme.md) · [specification](../frontend/src/ui/specification.md) |

## Components

| Package | Contents | Documents |
| ------- | -------- | --------- |
| Host SDK | The Python side of the component protocol | [readme](../components/host/README.md) · [specification](../components/host/specification.md) |
| LLM Call | Sends its prompt and the received message to the selected LLM | [readme](../components/llm-call/README.md) · [specification](../components/llm-call/specification.md) |
| Router | Runs the user's script to choose an output | [readme](../components/router/readme.md) · [specification](../components/router/specification.md) |
| Memory | Keeps a node's exchanges during a run | [readme](../components/memory/readme.md) · [specification](../components/memory/specification.md) |

## Tooling

| Tool | Contents | Documents |
| ---- | -------- | --------- |
| Component preparation | Builds and installs the component packages | [readme](../tooling/components/readme.md) · [specification](../tooling/components/specification.md) |
| Repository verification | The quality gates behind `make verify` | [readme](../tooling/quality/readme.md) · [specification](../tooling/quality/specification.md) |
| CodeQL verification | The pinned CodeQL suites | [readme](../tooling/quality/codeql/readme.md) · [specification](../tooling/quality/codeql/specification.md) |

## Engineering process improvement

| Document | Contents |
| -------- | -------- |
| [Overview](continuous-improvement/README.md) | How the engineering process is evaluated, and every cycle |
| [Rules for these records](continuous-improvement/AGENTS.md) | How process records are maintained |
| [Improvement register](continuous-improvement/improvement-register.md) | Proposals and the owner's decisions |
| [Measurement](continuous-improvement/measurement.md) | How time and effort are measured, and its limits |
| [Cycle template](continuous-improvement/cycle-template.md) | The structure of a cycle report |
| [M01](continuous-improvement/methods/001-incremental.md) | Earlier incremental practice |
| [M02](continuous-improvement/methods/002-phased-sprint.md) | Complete sprint in distinct phases ([archived rules](continuous-improvement/methods/002-rules-snapshot.md)) |
| [M03](continuous-improvement/methods/003-contract-closure.md) | Contract closure before delegation |
| [M04](continuous-improvement/methods/004-testing-and-verification.md) | Contracts, test preparation and verification |
| [M05](continuous-improvement/methods/005-local-ci-verification.md) | Local verification equivalent to CI |
| [M06](continuous-improvement/methods/006-delivery-preparation.md) | Assignment preparation, review evidence and test readiness |
| [M07](continuous-improvement/methods/007-validated-journeys.md) | Validated journeys, tests with code and sprints as stopping points (current) |
| [C01](continuous-improvement/cycles/001-baseline-2026-09-28/report.md) | Baseline work-time report |
| [C02](continuous-improvement/cycles/002-sprint-2026-09-29/report.md) | Evaluation of the phased sprint ([testing analysis](continuous-improvement/cycles/002-sprint-2026-09-29/testing-analysis.md)) |
| [C03](continuous-improvement/cycles/003-contract-closure/report.md) | Agent canvas and English presentation ([plan](continuous-improvement/cycles/003-contract-closure/plan.md), [time audit](continuous-improvement/cycles/003-contract-closure/time-audit.md)) |
| [C04](continuous-improvement/cycles/004-dependency-maintenance/report.md) | Dependency compatibility maintenance |
| [C05](continuous-improvement/cycles/005-personal-experiments/report.md) | Personal experiment delivery |
| [C06](continuous-improvement/cycles/006-provider-resource-workspace/report.md) | Provider, resource and workspace delivery |
| [C07](continuous-improvement/cycles/007-product-workspace-completion/report.md) | Earlier S06 product workspace completion |
| [C08](continuous-improvement/cycles/008-workspace-redesign/report.md) | Earlier S06 workspace redesign |
| [C09](continuous-improvement/cycles/009-s06-fidelity/report.md) | Earlier S06 fidelity correction |
| [C10](continuous-improvement/cycles/010-s06-interface-completion/report.md) | Earlier S06 product interface |
| [C11](continuous-improvement/cycles/011-s06-composition-and-dialogs/report.md) | Earlier S06 composition and component-owned dialogs |
| [C12](continuous-improvement/cycles/012-core-step-1/report.md) | The new execution core, sprint S06 |
