# C12 — Core step 1

| Document control                        | Value                                                                  |
| --------------------------------------- | ---------------------------------------------------------------------- |
| Document ID                             | C12                                                                    |
| Status                                  | Active                                                                 |
| Record owner                            | Cesar Zea                                                              |
| Recorded date and timezone              | 2026-10-04, UTC                                                        |
| Method identifier and version           | [M07](../../methods/007-validated-journeys.md)                         |
| Product sprint / delivery specification | [Step 1 delivery](../../../specification/s06/README.md)             |

## Context and hypothesis

C12 delivers step 1 of the new execution core: journeys J1–J3 and the activity view.
It is the first application of M07. The starting point is the published S03 code on
branch `core-foundation`, with the S04–S06 implementation archived locally.

Hypotheses under evaluation, by decision identifier:

- P14: validating journeys before deriving contracts reduces owner rejections after
  technical verification.
- P15: tests written with the code surface coverage and integration defects before
  the final runner.
- P16: implementing shared foundations with one implementer reduces missing shared
  decisions during parallel work.
- P17: documentation under the README standards stays consistent and smaller per
  delivered scope.
- P18: per-phase time and token records make the cycle comparable.

P11–P13 remain pending proposals and are not evaluated as approved practice.

## Measurement basis

Times are observed checkpoints in UTC taken from file and repository timestamps;
they are not an activity audit. Token usage is recorded where the tooling reports it.

| Phase                                   | Start                | End                  | Evidence                                   |
| --------------------------------------- | -------------------- | -------------------- | ------------------------------------------ |
| 0 — Journey preparation and validation  | 2026-10-04T04:22:48Z | 2026-10-04T05:0x (owner validation; exact time not captured) | [Journey record](../../../specification/s06-journeys/README.md) |
| 1 — Analysis, specification and tasks   | after validation, first record at 2026-10-04T05:08:55Z | 2026-10-04T05:37:21Z (F1 launched) | Requirements, ADRs 0015–0023, architecture, contracts, module specifications, assignments |
| 2 — Development with tests              | 2026-10-04T05:37:21Z | 2026-10-04T08:26:55Z (last package, A1, delivered) | Deliveries recorded below                  |
| 3 — Review and corrections              | Interleaved: each delivery reviewed on arrival | Continues during phase 4 | Corrections recorded with each delivery    |
| 4 — Integration and acceptance          | 2026-10-04T08:26:55Z | Complete runner passed 2026-10-04T09:11:23Z; accepted by the owner on 2026-10-07 after the review | [Verification record](../../../specification/s06/verification.md) |

## Delivery and process results

Observations recorded during the cycle:

- Phase 1 found a verification gate defect: the CodeQL snapshot excluded every
  directory whose name starts with `bootstrap`, so the backend composition root was
  never analysed. The exclusion now applies only to framework-style names
  (`bootstrap-…`, `bootstrap.…`, `bootstrap*.js|css|map`), with a regression test.
- The previous implementation was removed from the working tree after archiving; ported
  code is taken from `origin/main` and commit `a844514` as each specification names.
- F1 (domain foundations) delivered in 59 min 04 s of agent time with 191 tool uses and
  581,406 reported subagent tokens: 309 tests, 100% line and branch coverage in the five
  packages, mutation testing of `accounting` with 519 of 523 mutants killed and one
  timeout (previous record: 141 of 200). Its report raised five questions; the review
  resolved them as two corrections (no embedded components in Trigger and Output
  nodes; ECMA-262 `$` semantics for schema patterns), one removal (unused operation
  types) and two approvals. No contract gap blocked the work.
- F1 also found a second verification defect: `verify.py` deleted only the mutation
  statistics file, so `backend/mutants` kept copies of deleted tests and old mutants.
  The runner now removes the whole directory before mutation testing, with a test.
- Staging under P16 (2026-10-04T06:38:53Z): after F1's foundations were implemented and checked, F2
  (engine and application) started together with the packages that depend only on wire
  contracts: the browser interface (U) and the component side (P2a: host SDK, LLM Call,
  Router, packaging). Adapters that implement F2's ports (persistence, HTTP, providers,
  host launching) wait for F2's delivery. The original plan grouped the component side
  with the host launcher as P2; it was split to start the independent part earlier.
- F1's review corrections took 10 min 01 s with 30 tool uses (659,507 reported subagent
  tokens, which include the reloaded context of the original assignment): 330 tests,
  100% line and branch coverage; no exported interface changed.
- P2a (host SDK, LLM Call, Router, packaging) delivered in 51 min 37 s with 261 tool uses
  and 611,148 reported subagent tokens: 238 tests, 100% line and branch coverage in four
  packages, real subprocess runs of both components over MCP stdio. It reported two
  contract gaps — exact tool schemas and SDK error codes were informal in the protocol
  contract, and the module-boundary text claimed shared wire types in the SDK, which the
  import rules forbid — both closed in the contract by the coordinator, plus a version
  mapping for installations (component version versus distribution version).
- F2 (engine and application) delivered in 55 min 49 s with 200 tool uses and 586,187
  reported subagent tokens: 107 tests, 100% line and branch coverage in both packages,
  the three journeys and the limit case through the gateway with scripted fakes. It
  documented its open details in the specifications and raised six questions; the
  review moved parameter validation into `catalog` (one validator, ECMA patterns),
  assigned adapter test fixtures to each adapter's own test directory, amended the
  protocol wording on late grant use, and accepted the counting and status choices.
- Environment: the machine's default Node.js is v23.10, outside the range required by
  dependency-cruiser and Vitest, and the pinned Node.js 24 is not installed. Local gates
  run with the installed Node.js 26.10; CI keeps Node.js 24. This deviation is recorded
  with every local verification result.
- Review corrections after F2 (grouped, M07 phase 3 within phase 2 deliveries): F1
  added LLM parameter checks to `catalog` (3 min 34 s) and then replaced its duplicated
  validation code with one public schema-problems API (11 min 05 s); F2 switched the
  gateway to it (1 min 17 s). Domain, engine and application then held 478 tests at 100%
  line and branch coverage.
- P1 (provider adapters) delivered in 29 min 20 s with 103 tool uses and 345,849
  reported subagent tokens: 145 tests, 100% line and branch coverage, and the three
  journeys through the real gateway with the simulated provider. Its review found a
  composition gap: the gateway takes one provider, but a configuration may mix the
  `simulated` provider with real ones, so the composition root now dispatches by
  provider. The review also checked DeepSeek's current documentation, which supports
  only `json_object` output; the contract now adapts `json_schema` requests for DeepSeek
  instead of letting them fail at the provider. P1 implemented the adaptation in 2 min
  15 s with 6 tool uses (19,538 more reported subagent tokens): 153 tests, 100% line and
  branch coverage.
- A2 (HTTP adapters) delivered in 36 min 24 s with 164 tool uses and 461,267 reported
  subagent tokens: 121 tests, 100% line and branch coverage, and a smoke run over a real
  socket with the OpenAI client and the host SDK's report call. Its review found three
  integration defects that no single package could see:
  - The assigned test directory `backend/tests/http/` shadowed the standard library's
    `http` package and broke every pytest run while it existed; it was renamed.
  - The Vite proxy forwarded the browser's host, which the backend refuses.
  - The example configuration did not accept the backend's own origin for the
    interface it serves.

  A configured static directory that has not been built now fails startup with an
  instruction. A2 renamed its test package in 1 min 1 s with 8 tool uses (8,216 more
  reported subagent tokens).
- U (browser interface) delivered in 1 h 33 min 9 s with 347 tool uses and 965,087
  reported subagent tokens: 222 tests at 98.92% statements, 93.72% branches, 99.25%
  functions and 99.47% lines. Without a backend, U ran the coordinator's journey specs
  against an in-memory mock. That found a defect in the coordinator's journey helpers:
  an inexact accessible-name match, where "Story" also matched "Funny story". The
  review then compared the interface with the validated journey record and found a
  specification error of the coordinator: the record shows the status `Stopped:
  activation limit reached` with the explanation below it, while the runs
  specification asked for `Stopped: <detail>`. The specification was corrected and U
  changed the interface in 3 min 59 s with 17 tool uses: 225 tests, with coverage
  unchanged within 0.11 points.
- P2b (host launcher) delivered in 38 min 19 s with 115 tool uses and 282,377 more
  reported subagent tokens: 104 tests, 487 of 488 lines and 78 of 80 branches, real host
  processes for both components and an engine run of the story-triage journey. Its
  review added the platform's host-side failure codes to the protocol contract, which
  had listed only the SDK's codes. It also found a timing race: a run-bound call
  budget rounded down could let a host's own timeout precede the run deadline and fail
  the run instead of stopping it. F2 was asked to round run-bound budgets up, and did
  so in 1 min 56 s with 5 tool uses: 112 engine and application tests at 100% line
  and branch coverage, including a host timeout answered exactly at the deadline.
- A1 (persistence, installations, composition root) delivered in 53 min 5 s with 233
  tool uses and 565,213 reported subagent tokens: 154 tests, at least 98.0% of lines
  and 93.5% of branches per package, and a run of J1 through the composed application
  on a real server with real component hosts. Its review found that verifying an
  installed environment hashes every file on the event loop at each host launch; P2
  was asked to move that call off the loop and make it once per component and run. The
  production path through `make components` had not run end to end; it is part of
  phase 4.
- First integrated state (2026-10-04, after A1): the lock regenerated without the
  previous implementation's LangChain, LangGraph and `psutil` dependencies, and
  `httpx2` declared for the tests that import it. 22 import contracts kept; ruff,
  formatting (414 files), pyright, mypy, vulture and the source rules clean; 1,400
  Python tests passing with 99.39% combined coverage; frontend typecheck, lint,
  boundaries, dead-code and 225 unit tests passing. The build warns that the main
  bundle exceeds 500 kB.
- Browser journeys against the real backend: the five journey tests passed on the
  first integrated run (16.3 s). A new activity journey for step 1.2 compared the
  interface with the validated activity view and found one more label deviation
  ("Model calls" instead of the validated "LLM calls"). U corrected it in 54 s with 4
  tool uses. Eight browser tests then passed in 27.0 s.
- Installed path and visual review (acceptance server started from configuration with
  the components installed by `make components` in 8 s, the simulated provider and the
  built interface): the three example graphs completed in about 1.4 s each, with
  gapless event sequences and recorded usage. Reviewing the built interface at 1440 by
  900 against the validated designs found two layout defects that no unit or journey
  test caught:
  - A grid-row error left the editor canvas at half height until a node was selected,
    and the run view had a fixed 420 px canvas.
  - Canvas cards were wider than the spacing of the coordinator's J3 example layout,
    so one card hid another card's port, connection and activation count.

  The coordinator widened the example layout and split the interface bundle into
  library chunks, which removed the build's size warning. U fixed both layouts and the
  automatic placement in 17 min 32 s with 59 tool uses, adding layout tests that load
  the real stylesheets: 229 tests. Measured afterwards in the browser, the canvases
  are 759 px (editor) and 760 px (run view) tall, and the cards have gaps of 26 to
  43 px.
- First complete runner (2026-10-04T08:59Z): every gate before CodeQL passed; CodeQL
  failed on five `py/side-effect-in-assert` errors in F2's tests (a fake ledger method
  named `open` called inside assertions) and one `py/unreachable-statement` warning in
  A1's tests. The implementers' scoped gates had not included CodeQL, so test code
  first met it in the complete runner. F2 renamed the method and moved three other
  side effects out of assertions (1 min 51 s, 12 tool uses); A1 restructured that
  test and four others with the same pattern (3 min, 8 tool uses). The coordinator
  added browser tests for connecting ports by dragging and for restoring unsaved
  changes after a reload (AC01, AC09), which only unit tests covered before.

- Owner review, round 1 (2026-10-04, after a guided tour of the running product). The
  owner asked where to see and configure the components and where to see runs and
  experiments, and requested five changes:
  - richer, more compact configuration controls (the Router's output fields spanned the
    whole dialog);
  - a configuration dialog that keeps its size and position when the section changes;
  - side-panel sections collapsed by default, with an option to expand them all;
  - spending in the banner limited to three decimals;
  - pages for components and runs.

  The owner chose quick changes during review, with complete testing and validation
  when the review closes. Experiments remain roadmap step 5. U took the dialog,
  controls and side panel; a new implementer, V, took the Components and Runs pages
  and the banner.

  Further requests in the same round: removing connections from the canvas and an
  automatic arrangement button. V delivered in 22 min 55 s with 114 tool uses; U in
  30 min 29 s with 117 tool uses (fixed-size dialog with section navigation, compact
  controls, collapsed side panel, connection removal, Arrange). The interface then
  held 308 unit tests; journey updates were left to closing.

  The owner then asked to drop the operator token or make it memorable, and not to
  ask for it again after a reload. Decision: an opt-in mode without operator
  authentication, accepted only when every allowed host is a loopback address and
  serving only loopback peers, plus the token kept per browser tab in token mode.
  A1 (2 min 39 s, 15 tool uses), A2 (5 min 17 s, 31 tool uses) and V (7 min 30 s,
  21 tool uses) implemented it in parallel; the contract and security document were
  amended. A2's suite stayed at 100% line and branch coverage; the interface held
  318 unit tests.

- Owner review, later rounds (2026-10-04 and 05). The owner asked that review changes
  be made directly by the coordinator, without implementers, and that linting and
  testing wait for the close. Changes were made in short edit, typecheck and build
  loops against a running demonstration server; per-change times were not captured.
  The rounds covered the professional redesign of the editor, autosave with activated
  versions and branches (ADR 0024), arrangement modes and connection styles, port sides,
  undo and redo, node deletion, collapsible and resizable side panels, a demonstration
  with the real providers (GPT-5 nano added as the cheapest model), run mode executing
  what is on screen with observation points and a live feed (ADR 0025), and Memory as
  an embedded component (ADR 0026).
  - A first Memory implementation inside the engine was rejected by the owner, who
    required absolute encapsulation between components and platform. It was replaced by
    a `memory` position of the component protocol served by its own package, which
    required rebuilding every component package.
  - Two direct requests were reversed after the owner's objection (a graph direction
    attribute and automatic port sides).
- Close of the review (2026-10-05). Node facets as observation points were completed
  first. Then the review's debt was paid: 40 ESLint findings (mostly functions over 30
  lines and files over 150 lines grown during review), outdated tests (35 failing
  interface tests, Python tests hanging because a test fake built run records without
  the new `change` field), the browser journeys written for the removed Save button,
  run dialog and run page, and the documentation. New tests cover change runs, the
  memory position with real host processes, observation points, run mode, side panels
  and a memory browser journey. The complete runner then passed; figures are in the
  [verification record](../../../specification/s06/verification.md#complete-runner).

## Evaluation and limitations

Agent work in phase 2: eight first deliveries took 6 h 56 min 47 s of agent time with
1,614 tool uses, in 2 h 49 min 34 s of elapsed time; review corrections and integration
follow-ups added 1 h 6 min 28 s. Reported subagent tokens are listed per delivery above;
they include the context reloaded on each resumption and are not additive.

- P14 (validated journeys): the owner accepted step 1 on 2026-10-07, after a review that
  changed several criteria; its effect is evaluated in the next cycle. During
  phase 4 the validated record caught three deviations before the owner saw the product:
  the run status wording, the "LLM calls" label and the canvas layout. Two of them were
  the coordinator's specification errors, not implementation errors.
- P15 (tests with the code): supported for behaviour. Every package arrived with at least
  93.5% branch coverage, and the first integrated browser run passed all five journeys.
  It did not catch integration and presentation defects:
  - a test package that shadowed the standard library;
  - the Vite proxy's host;
  - origins missing from the example configuration;
  - the editor's grid row and overlapping cards;
  - CodeQL findings in test code, because the scoped gates omitted CodeQL.
- P16 (shared foundations first): supported. The parallel packages raised no gap in the
  domain contracts; their questions concerned composition (provider dispatch, host-side
  failure codes, static files, event-loop blocking during verification).
- P17 (documentation under the README standards): partially evaluated. Module
  specifications stayed current, and implementers changed them with their code. The
  contracts needed six amendments that implementation revealed: protocol tool schemas
  and SDK codes, host-side failure codes, nullable call records, DeepSeek structured
  output, late grant use and the J3 example layout.
- P18 (measurement): supported. Each delivery and correction has elapsed time and tool
  uses. Token figures are comparable only within one agent's first delivery.

Limitations: the measures come from one cycle with one coordinator; agent time is
sequential work by each agent and overlaps in elapsed time; local verification used
Node.js 26 instead of the pinned Node.js 24.

## Next-cycle decision

The owner accepted step 1 on 2026-10-07. The owner scheduled step 2 as the next sprint:
Labs, mem0 as a memory component and shared resources. Observed in the review: deferring
lint and tests during quick changes kept the owner's loop short but accumulated
structural debt that took the close several hours; components must be encapsulated from
the first implementation. Proposed process changes for the next cycle:
- include CodeQL in the scoped gates;
- add a visual review at a desktop size to each interface delivery;
- check assigned test directory names against the standard library;
- during quick review changes, run the source rules (file and function size) with each
  build, since they are cheap and their debt grows fastest.

### Addendum, 2026-10-07

Step 1 is sprint S06 under the project's sprint numbering. After the
[scope review of 2026-10-06](../../../specification/scope-review-2026-10-06.md) the owner
replanned the work as sprints S07–S25 ([roadmap revision 3](../../../specification/roadmap.md));
the next sprint is S07, not the step 2 described above. The review also showed that
rewriting requirements without listing what they drop lets scope disappear unnoticed;
every scope rewrite now lists removed, reduced and changed items for the owner's
approval.
