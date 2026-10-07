# S06 verification record

| Document control | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| Document ID      | STEP-1-VERIFICATION                                                         |
| Delivery         | [S06](README.md), acceptance criteria AC01–AC13                          |
| Cycle            | [C12](../../continuous-improvement/cycles/012-core-step-1/report.md)        |
| Date             | 2026-10-05                                                                  |
| Source state     | Working tree of branch `core-foundation`, not committed                     |
| Status           | Locally verified after the owner's review; accepted by the owner on 2026-10-07 |

This record lists the evidence for each acceptance criterion and the results of the
complete verification runner. Browser journeys run the real backend with the
simulated provider; unit, contract and integration tests run with the code.

## Acceptance evidence

| ID   | Evidence                                                                                                                                                                                                 |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC01 | Browser: `j1-one-agent.spec.ts` (build, configure, save, run, result under the Output's name); `editing.spec.ts` (connection by dragging). Interface: `editor-canvas`, `editor-workspace`, `editor-save`. |
| AC02 | Browser: `j1-one-agent.spec.ts`, and `j3-review-loop.spec.ts` (DeepSeek Temperature follows Reasoning). Interface: `ui-parameters`, `editor-node-dialog`. Domain: `test_llm_parameters.py`, `test_llm_entries.py`. |
| AC03 | LLM Call: `test_generate.py`, `test_contracts.py`, `test_model_failures.py`, `test_llm_call_process.py`. Browser: `activity.spec.ts` shows the prompt as the system message and the story as the user message.     |
| AC04 | Browser: `j2-embedded-router.spec.ts`. Interface: `editor-embedding` (Add component, ports replaced, removal with the affected connections). Domain: `test_graph_ports.py`, `test_declaration_rules.py`.      |
| AC05 | Router: `test_router.py`, `test_router_script.py`, `test_router_process.py`. Engine: `test_failures.py`. Hosts: `test_components.py` (a Router that does not compile fails the run with its detail). Interface: `run-mode-execution`. |
| AC06 | Browser: `j3-review-loop.spec.ts` (accepted loop; limit case `Stopped: activation limit reached` with its detail). Engine: `test_stops.py`, `test_journeys.py`.                                              |
| AC07 | Browser: `j3-review-loop.spec.ts` and `activity.spec.ts` (Limits dialog, budget used). Interface: `app-shell` (Today and This month). Application: `test_budgets.py`.                                       |
| AC08 | Browser: J1–J3 (run mode on the editor's screen, the Trigger's message asked for on Execute, the result under the Output's name). Interface: `run-mode-execution` (Execute, Stop, Run again, statuses with reason and detail), `run-mode-observation`, `observation-points`. Application: `test_runs.py`, `test_change_runs.py`. Engine: `test_scheduling.py`, `test_stops.py`. |
| AC09 | Browser: `editing.spec.ts` (every edit saved as it is made and kept after a reload). Interface: `editor-lifecycle`, `editor-save`, `run-mode-execution` (Execute saves pending edits first). HTTP: `test_http_graphs.py`. SQLite: `test_graph_store.py`. |
| AC10 | Browser: `activity.spec.ts` (order, expandable model call with request, reply, parameters and rates, Router decision, reported evidence, filters, totals and activations by node). Interface: `activity-*`.   |
| AC11 | Browser: `j1-one-agent.spec.ts` (no permission or slot text). Interface: `ui-schema-editor` (no raw JSON box). Application: `test_gateway_requests.py` (`403 model_not_allowed`). Access: `test_grants.py`. |
| AC12 | Application: `test_budgets.py`, `test_gateway_provider.py`. Accounting: `backend/tests/unit/` and mutation testing. SQLite: `test_ledger.py` (atomic reservations under concurrency).                    |
| AC13 | Interface text in English throughout. The complete runner below, with unchanged thresholds, includes the browser journeys J1, J2, J3, the limit case, the activity view and a node with a Memory.                              |

## Integration and recovery

Integration tests run the composed application:
- `backend/tests/bootstrap/test_served_run.py`: a served J1 run with real component
  hosts calling the platform back;
- `backend/tests/bootstrap/test_application.py`:
  - startup finishes interrupted runs as `failed` with `interrupted` and settles
    their reservations as estimated (restart recovery);
  - one backend owns the database;
  - shutdown cancels active runs and closes their hosts;
- `backend/tests/hosts/test_components.py`: the engine runs the story-triage journey
  on the real LLM Call and Router processes.

## Installed components

On 2026-10-05 `make components` built and installed LLM Call, Router and Memory in
13 s, and again after the license change (resolutions `97d5fa3c…`, `98148091…` and
`4d485287…`). A server started from a configuration with those resolutions, the
simulated provider and the built interface ran the three example graphs to completion
in 1.4 to 2.3 s each, and a fourth graph in
which an Editor with a Memory and a Router sends its first reply back to itself
completed in 2.1 s with four memory calls, the second recall carrying the first
exchange. Every run, started through the operator API, had a gapless event sequence,
reported evidence and recorded usage. The owner reviewed the interface on a
demonstration server during the review session; this final build has not been
reviewed in the browser since.

## Complete runner

`make verify` ran on the final source state from 2026-10-06T00:27:31Z to 00:31:33Z,
with unchanged thresholds and Node.js 26.10, and exited with status 0. Every step
passed:

| Step                                                     | Result                                                                    |
| -------------------------------------------------------- | ------------------------------------------------------------------------- |
| Source rules                                             | 150 lines per file, 30 per function, complexity 8: no violation           |
| ruff check and format, pyright strict, mypy strict       | No finding                                                                |
| Import Linter                                            | 23 contracts kept                                                         |
| vulture                                                  | No finding                                                                |
| TypeScript typecheck, ESLint, Prettier                   | No finding                                                                |
| dependency-cruiser, knip                                 | No violation (252 modules, 1,064 dependencies); no unused code            |
| CodeQL (pinned bundle)                                   | Python: no error or warning, 49 notes; JavaScript and TypeScript: none    |
| pytest with coverage                                     | 1,617 passed; 99.77% of lines (7,025 of 7,041), 98.94% of branches (1,401 of 1,416) |
| Vitest with coverage                                     | 414 passed; 97.68% statements, 90.59% branches, 98.38% functions, 98.87% lines |
| Interface build                                          | No warning; largest chunk 379 kB, plus the layout worker (1.6 MB) loaded on demand |
| Playwright journeys                                      | 11 passed in 39.3 s                                                       |
| Mutation testing of `accounting`                         | 523 mutants: 519 killed, 1 timeout, 3 survived                            |

Of the 49 CodeQL notes, 47 (`py/ineffectual-statement`) are the `...` bodies of
`Protocol` methods, one is an awaited task inside `pytest.raises` in a provider test,
and one (`py/unused-import`) is the explicit re-export of `GraphStore` from the
application's ports. The three surviving mutants are equivalent:
- two change the result returned by `_exact_quanta` for amounts below one
  nano-dollar, whose caller rejects any nonzero remainder whatever the quotient;
- one makes `charge` always call `_higher(first, last)`, which returns the same rate
  when both are equal.

## Known limitations

- Local verification runs Node.js 26.10 because the pinned Node.js 24 is not installed
  on the verification machine and Node.js 23 is outside the supported range; CI uses
  Node.js 24.
- Real OpenAI and DeepSeek calls are not part of automated verification. The DeepSeek
  adapter sends structured output as `json_object` with the schema in a system
  instruction, as the provider supports only that mode.
- A canvas card taller than 200 px, such as a Router with three or more outputs, can
  be placed less than 24 px above the next automatically placed card.
- A node with a Memory is stateful and takes one activation at a time; until input
  queues exist (S14), a second message that arrives while it is busy fails that
  activation with `node_busy`, and the run with it.
- Interface branch coverage is 90.59%, close to the 90% threshold.
