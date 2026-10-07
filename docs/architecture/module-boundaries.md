# Module boundaries

The source tree is organized by capability. Every module has a public entry point,
a brief `readme.md` and a `specification.md` in its directory, and a `todo.md` only
while assigned work remains. Imports cross module boundaries only through public
entry points. The checks below run in the single verification command.

## Backend packages

All under `backend/src/slow_thinker_ii/`.

| Package                    | Responsibility                                                                                   | May import                                   |
| -------------------------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------- |
| `contracts`                | JSON value types, canonical encoding and decoding                                                | Standard library                              |
| `accounting`               | Money in nano-dollars, tariffs, reservation bounds, settlement charges, budget admission decisions | `contracts`                                  |
| `access`                   | Invocation grants: issue, resolve, revoke; digests only                                          | `contracts`                                  |
| `catalog`                  | Component declarations, platform component declarations, effective ports, LLM catalog entries and parameter schemas | `contracts`, `jsonschema`        |
| `graphs`                   | Graph documents, validation and diagnostics, run plans                                           | `catalog`, `accounting`, `contracts`, `jsonschema` |
| `engine`                   | Run scheduling, activations, embedded pipeline, limits and termination, behind ports             | `graphs`, `catalog`, `access`, `contracts`   |
| `application`              | Use cases and their ports: graph library, runs, LLM gateway, reports, usage                      | Domain packages and `engine`                 |
| `adapters.sqlite`          | Schema, migrations and stores for graphs, runs, events and the budget ledger                     | `application`, domain packages, `sqlite3`    |
| `adapters.http`            | Operator API v2, `/v1/chat/completions`, `/mcp` reports, authentication                          | `application`, FastAPI, MCP                  |
| `adapters.hosts`           | Local process launcher, MCP stdio client, readiness, bootstrap documents                         | `application`, `engine` ports, MCP           |
| `adapters.providers`       | OpenAI, DeepSeek and simulated provider transports, usage normalization, redaction               | `application`, `accounting`, `httpx`         |
| `adapters.installations`   | Installed component registry, verification and declaration loading                              | `application`, `catalog`                     |
| `bootstrap`                | Server configuration, environment secrets and composition root                                   | Everything above; imported by nothing        |

Rules:

- The layers are, from top to bottom: `bootstrap`; `adapters`; `application`;
  `engine`; `graphs`; `catalog`, `accounting` and `access` as independent siblings;
  `contracts`. Lower layers never import higher ones; there are no import cycles.
- Domain packages and `engine` import no web framework, persistence, process,
  network or provider library: not `fastapi`, `sqlite3`, `mcp`, `openai`, `httpx`
  or `pydantic`.
- Adapters do not import each other's internals. Modules whose names start with an
  underscore are private to their package.
- No mutable module-level state and no environment access outside `bootstrap`.
- Import Linter enforces these contracts from `pyproject.toml`.

## Component packages

| Package                | Responsibility                                                        | May import                     |
| ---------------------- | --------------------------------------------------------------------- | ------------------------------ |
| `components/host`      | Host SDK implementing the [component protocol](../contracts/component-protocol.md) | MCP SDK, `jsonschema`, `httpx2`, `openai` |
| `components/llm-call`  | LLM Call component                                                    | `components/host`, `openai`    |
| `components/router`    | Router component                                                      | `components/host`              |
| `components/memory`    | Memory component, embedded as a node's memory                         | `components/host`              |

Components never import the backend, and the backend never imports component
packages, including the host SDK. Both implement the [component protocol](../contracts/component-protocol.md);
backend tests compare the two implementations of its wire schemas.

## Interface

All under `frontend/src/`.

| Directory                 | Responsibility                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------- |
| `api`                     | Transport, authentication, validated wire types and the operator API client         |
| `ui`                      | Presentation primitives and the generic configuration controls                      |
| `features/graphs`         | Graph list and creation                                                             |
| `features/editor`         | Canvas, palette, node cards, side panels, node dialogs, limits, run mode and observation points |
| `features/runs`           | Run mode's panel: message, Execute, status, figures and Stop                        |
| `features/activity`       | Activity timeline, per-node totals and the observed points' live feed               |
| `features/catalog`        | Read-only view of the installed components, configured LLMs and budgets             |
| `features/history`        | Run lists for all graphs or one graph                                               |
| `features/versions`       | History panel: working copy, branches drawn as lanes, versions and changes          |
| `app`                     | Routing, access, connection and the product shell                                   |

Features never import each other; shared code lives in `ui` or `api`. Code outside
`features` imports a feature only through its `index.ts`. dependency-cruiser enforces
these rules; knip rejects unused files and exports.

## Placement manifest

Every source file lies under a root declared in `tooling/locations.json`. Adding a
module adds its root there; utility packages created to escape size limits are not
allowed.

## Module documents and implementation workflow

1. Read the module's `readme.md`, `specification.md` and `todo.md`, and the contracts
   they cite, before changing it.
2. Implement against the public interfaces of other modules only.
3. Write unit and contract tests with the code and pass the module's scoped gates
   before delivery.
4. Remove completed items from `todo.md`; delete it when nothing remains. Keep the
   specification current; delivery status belongs in the sprint status report.
