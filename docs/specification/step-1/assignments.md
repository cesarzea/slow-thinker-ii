# Step 1 assignments

Assignments follow [M07](../../continuous-improvement/methods/007-validated-journeys.md):
shared foundations first with one implementer (F1, then F2), then independent packages
in parallel with exclusive ownership. Every assignment reads the cited contracts and
module specifications, writes unit and contract tests with its code, passes its scoped
gates, and delivers a map from acceptance items to changed files and evidence.

## Shared rules for every implementer

- Read [AGENTS.md](../../../AGENTS.md), the [module boundaries](../../architecture/module-boundaries.md),
  the contracts cited by the module specifications and the specifications themselves.
- Files you own are listed below; do not edit any other file. If you need a change
  elsewhere, report it instead.
- Previous code is available in git: `git show origin/main:<path>` (published S03 code)
  and `git show archive/s06-c11-wip~1:<path>` (commit `a844514`, verified S04–S06 code).
  Port only what your specification names; never copy wholesale.
- Engineering limits apply to every source and test file: at most 150 lines per file,
  30 lines per Python function, McCabe complexity 8; TypeScript strictest with no `any`.
- Each module directory has `readme.md` (write a brief one), `specification.md` (given;
  keep it current) and `todo.md` only while work remains.
- Use English in code, messages and documents.
- Scoped gates, run from the repository root with the existing environment
  (`uv run --no-sync` and `npx --no-install`; do not change lockfiles):
  - `uv run --no-sync ruff check <paths>` and `uv run --no-sync ruff format --check <paths>`
  - `npx --no-install pyright <paths>`
  - `uv run --no-sync mypy <package paths>` for domain, engine and application packages
  - `uv run --no-sync vulture <paths> --min-confidence 60`
  - `uv run --no-sync python -c "from pathlib import Path; from tooling.quality.inventory import read_locations; from tooling.quality.source_rules import check_source; print(chr(10).join(check_source(Path('.'), read_locations(Path('.')))) or 'source rules ok')"`
  - `uv run --no-sync pytest <test paths> --cov=<package> --cov-branch --cov-report=term-missing`
    with at least 90% of lines and of branches for the owned packages
  - Frontend: `npm run typecheck`, `npm run lint`, `npm run format:check`,
    `npm run boundaries`, `npm run deadcode`, `npm test`
- Delivery report: acceptance map, local design choices, gate results with numbers,
  anything unresolved.

## F1 — Domain foundations

| Item       | Value                                                                                                      |
| ---------- | ---------------------------------------------------------------------------------------------------------- |
| Owns       | `backend/src/slow_thinker_ii/{contracts,accounting,access,catalog,graphs}/`; `backend/tests/unit/` and `backend/tests/domain/` |
| Specs      | [accounting](../../../backend/src/slow_thinker_ii/accounting/specification.md), [access](../../../backend/src/slow_thinker_ii/access/specification.md), [catalog](../../../backend/src/slow_thinker_ii/catalog/specification.md), [graphs](../../../backend/src/slow_thinker_ii/graphs/specification.md); `contracts` gains JSON Pointer helpers and drops the unused operation types |
| Contracts  | Graph document, component declaration, LLM service (catalog), accounting                                   |
| Depends on | Nothing                                                                                                     |

Accounting tests live in `backend/tests/unit/` because mutation testing selects them
there. Contract examples and schemas under `docs/contracts/` are test fixtures; tests
read them, never copy them.

## F2 — Engine and application

| Item       | Value                                                                                                     |
| ---------- | --------------------------------------------------------------------------------------------------------- |
| Owns       | `backend/src/slow_thinker_ii/{engine,application}/`; `backend/tests/engine/`, `backend/tests/application/` and shared fakes in `backend/tests/support/` |
| Specs      | [engine](../../../backend/src/slow_thinker_ii/engine/specification.md), [application](../../../backend/src/slow_thinker_ii/application/specification.md) |
| Contracts  | Execution, recording, LLM service (calls), accounting                                                     |
| Depends on | F1 delivered and reviewed                                                                                 |

## Parallel packages after F2

| ID  | Owns                                                                                              | Specs                                                                 |
| --- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| A1  | `adapters/sqlite/`, `adapters/installations/`, `bootstrap/`, `examples/`, their tests under `backend/tests/{sqlite,installations,bootstrap}/` | sqlite, installations, bootstrap                     |
| A2  | `adapters/http/` and `backend/tests/http_adapter/` (not `http`, which would shadow the standard library) | http                                                   |
| P1  | `adapters/providers/` and `backend/tests/providers/`                                              | providers                                                             |
| P2  | `adapters/hosts/`, `components/host/`, `components/llm-call/`, `components/router/`, `tooling/components/`, `backend/tests/hosts/`, `tooling/tests/test_component_*` | hosts, host SDK, LLM Call, Router |
| U   | `frontend/src/`, `frontend/tests/` except journeys                                                | api, ui, app, graphs, editor, runs, activity                          |

## Coordinator

Owns `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json`, `Makefile`,
`tooling/locations.json`, `tooling/quality/`, `tooling/tests/` (except component
preparation tests), `frontend/playwright.config.ts`, `frontend/tests/journeys/`,
`backend/tests/journeys/` and all documents outside module directories. Tasks: shared
configuration, the CodeQL exclusion that skips `bootstrap` directories, import-contract
violation tests, lockfile regeneration, review, integration and browser journeys,
complete verification and the owner demonstration.
