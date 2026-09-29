# First-cycle delivery sprint

Status: first-cycle local delivery verified on 2026-09-29.

## Delivery objective

Deliver the approved local, single-user experiment workflow end to end: select a
bundled graph, provide its input, execute independently hosted components through
the platform, observe calls and costs live, stop safely and inspect saved results.
Include the approved bounded proposer/reviewer collaboration: feedback returns to
the proposer until the reviewer accepts or a configured limit stops execution.
The existing four finite examples remain supported.

This completes the agreed first cycle. Graph editing/upload, automatic influence
analysis, memory-provider implementations, arbitrary parallel/dynamic scheduling,
standalone export and server deployment remain outside this delivery.

## Preparation baseline

The current implementation already has isolated component installation, finite
Sequence execution, managed model calls, saved sessions, accounting, operator
commands and detailed evidence inspection. Existing tests are historical evidence,
not proof that the new sprint passes. Preserve the uncommitted inspector navigation
fixes and unrelated user changes; do not absorb IDE changes into implementation.

Local documents now cover 28 existing modules. Their `todo.md` files identify
unfinished work. New component documents and the contracts below define the added
interfaces before implementation. Do not repeat the repository-wide inventory.

## Shared implementation contracts

- [Conditional routing](../contracts/conditional-routing.md): redirector,
  composition, controller decisions, repeated activations and graph bindings.
- [Managed gateway](../contracts/managed-gateway.md): outgoing MCP calls and
  optional reports with authenticated invocation identity.
- [Inspection projections](../contracts/inspection-projections.md): graph detail,
  live execution and graph/inspector selection.
- Existing [accounting](../contracts/accounting-policy.md),
  [execution](../contracts/execution.md), [observation](../contracts/observation.md)
  and [operator API](../contracts/operator-api.md) policies remain authoritative.

## Complete implementation assignments

Each assignment owns complete packages and their corresponding local documents.
Dependencies use the contracts above, so implementation can run in parallel.

| Assignment | Exclusive ownership | Required delivery |
| --- | --- | --- |
| Backend | `backend/`, graph schema under `docs/contracts/schemas/graph.schema.json` | General MCP gateway; recorded denials and optional reports; graph detail/live projections; conditional compilation/program; exact public monetary input; over-bound charge quarantine; proven process ownership/recovery; composition and startup wiring. |
| Components | `components/`, `examples/grounded-review/`, `tooling/components/`, new bounded-review fixtures under `docs/contracts/examples/` | Redirector, RoutedCall and BoundedFlow packages; host MCP/report helpers; preparation recipes and the bundled collaborative example. Preserve LLMCall and Sequence behavior. |
| Browser | `frontend/` | Definition-driven inputs; Structure/Execution views; control, permission and observed-call layers; live activation state; bounded-loop rendering; linked inspector and reported/unavailable evidence. |
| Coordinator | Root configuration/lockfiles, shared architecture/contracts and sprint record | Freeze cross-package contracts, register new package locations/dependencies, review deliveries and whole-system behavior, group correction tickets and direct final verification. |

During development, do not write or run functional tests. Implementers deliver
code, updated local documents, a concise change inventory and unresolved issues.
They may use compilation/type checks to detect invalid code. Request shared
contract changes through the coordinator; never invent an incompatible boundary.
Do not commit or push independently. Do not call paid model providers.

### Backend acceptance tickets

1. Authenticated denied calls produce evidence and zero target dispatches.
2. MCP discovery is permission-filtered; calls, native model requests and reports
   retain the trusted caller and activation; revocation and deadlines apply.
3. Public budget strings convert exactly to internal quanta. A charge above its
   reservation is retained, stops active execution and quarantines the affected
   pricing bound even when aggregate budgets remain available.
4. Restart does not replay work. Cleanup can terminate only a proven owned process;
   unverifiable ownership remains explicitly unconfirmed and blocks new admission.
5. Conditional programs preserve activation-specific feedback and route evidence.
   All stops, unknown routes and exhausted limits prevent further scheduling.
6. Browser projections expose exact definitions, inputs, identities, relationships,
   recorded activations/reports and costs through bounded authenticated reads.

### Component acceptance tickets

1. Redirector accepts user-authored packaged Python and returns one declared port.
2. RoutedCall invokes a normal worker and redirector through the platform, with no
   direct peer call or hidden model retry; internal components can be collapsed.
3. BoundedFlow checks the recorded transition history and selects next, complete
   or exhausted without being hardcoded to proposer/reviewer names.
4. The new example preserves a weak proposer and a reviewer as independently
   configurable LLMCall instances, returning concrete findings on rejection.
5. New packages install through exact hashed bundles and expose explicit public APIs.

### Browser acceptance tickets

1. A graph is visible before starting; input comes from that exact definition.
2. Repeated activations remain distinct from configured agents; an actual call is
   not confused with permission or control flow.
3. Selected graph objects open the matching evidence visibly and accessibly.
4. Reflow, polling, connection loss and history selection preserve identity and
   never repeat a command or silently change the backend execution state.
5. The reviewer return/accept routes and optional internals are understandable;
   missing reasoning and unresolved costs are explicit.

## Review, corrections and testing

Receive all deliveries, review their contracts and the full execution path, then
write grouped correction tickets in the responsible modules. Review corrections
until the complete result appears ready for testing. No separate merge phase is
needed because assignments do not overlap; interaction correctness still requires
whole-system review and integration tests.

Only then finalize and delegate testing tickets. Backend owns its unit, storage,
HTTP, process, permission, accounting and SDK-conformance tests. Components own
component, packaging and deterministic routing tests. Browser owns feature tests
and Playwright journeys. The coordinator owns verification configuration and the
cross-package acceptance assessment. Test the specifications, not merely the
implemented branches.

Run focused corrections against affected tests and the full mandatory `make verify`
before delivery. Preserve coverage, mutation, boundary, typing and security gates.
Required provider tests use simulations. A live demonstration must first confirm
remaining headroom under the user's existing total USD 3 authorization; never reset
that allowance or imply that a per-run cap resets the authorized total.

Finish with a runnable local application, inspectable accepted and rejected/limited
review paths, saved evidence, updated usage instructions and an honest verification
record. Commits and any authorized pushes use Cesar Zea / cesarzea only.

## Progress measurement

Record phase boundaries and distinguish wall time from aggregate parallel effort.
At resume, the goal counters were 32,344 seconds and 4,495,563 tokens; these are
cumulative goal counters, not this sprint's elapsed time. Compare verified delivery,
rework and integration defects; do not infer efficiency from generated code volume.

Preparation completed: 28 existing modules and three new component packages have
local documents; 19 modules/packages have pending-work tickets. Three shared
contracts define cross-package interactions, and immutable public type skeletons
exist for the new packages. Module-document links were checked. No functional tests
were run during preparation. Development checkpoint: 2026-09-29 03:15:08 UTC;
all three assignments were active at this point.

Review/correction checkpoint: 2026-09-29 03:45:38 UTC. All three deliveries have
been reviewed individually and together. Corrected physical unit sizes, a strict
Python annotation, asynchronous selector discovery and browser identity checks.
Source-placement/size gates, strict backend typing and 26 import contracts pass.
No functional tests ran before this checkpoint.

### Testing assignments

- Backend owns backend tests and fixtures, including the shared browser-test
  server and installed checks. Exercise all five compiled graphs, real nested MCP
  requests and retained source identities; conditional acceptance, rejection,
  exhaustion, Stop and deadlines; denial/report evidence; v5 migration, quarantine,
  cleanup ownership and exact budgets. Complete native OpenAI/LangChain/LangGraph
  conformance with simulated providers. Make browser fixtures return the exact
  saved graph and support a deterministic bounded-review run.
- Components owns component tests, the derived example and complete `tooling/tests`
  package. Exercise selector/pointer/schema/port failures, exact controller history,
  scoped MCP/report/LangChain helpers and all seven preparation recipes. Preserve
  existing gate violation tests and independent packaging behavior.
- Browser owns frontend tests and journeys. Cover exact identity and fixed snapshot
  paging, inputs, collapsed internals, repeated activations, keyboard/focus inspection,
  unavailable/reported evidence and reconnection. Coordinate shared fixture needs
  through the backend owner; do not edit backend fixtures.
- Coordinator prepares the current exact component bundle, runs installed acceptance
  checks and the final full verification, inspects the UI, and retains the existing
  paid-call allowance and accounting history for a subsequent live demonstration.

Implement the planned tests before running the respective suites. Group discovered
failures into module correction tickets, then implement fixes and rerun affected
checks. Do not lower assertions, coverage, size, typing or other quality gates to
make a delivery pass. No implementer makes paid provider calls.

## Delivery verification

Final verification checkpoint: 2026-09-29 04:24:11 UTC. `make verify` passes with
1,266 Python tests, 119 frontend tests and seven browser journeys. Nineteen real
installation checks plus the nonterminating-selector check pass. Two live OpenAI
runs confirm immediate acceptance and rejection/correction/acceptance with exact
feedback provenance, confirmed process cleanup and retained accounting.

Preparation began at 02:54:16 UTC; the elapsed time to this verified checkpoint was
1 hour 29 minutes 55 seconds. These are wall-clock boundaries, not summed parallel
agent effort or proof of a causal speedup over earlier work. Testing corrections
included fixture expectations/runtime selection, UI identity and viewport behavior,
a protocol annotation and missing contract/validation branch tests. Implementation
and verification evidence is consolidated in the [verification record](../verification.md).
