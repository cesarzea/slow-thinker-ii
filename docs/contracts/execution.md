# Execution, accounting and evidence

**Status: Approved first-cycle contract.** Limits, central mediation, lifecycle and persistence semantics are part of the approved baseline. References: R05, R11–R16, R23; [ADR 0006](../adr/0006-execution-and-accounting.md).

## Admission and identity

A run selects an immutable graph revision, separate input, saved work session and effective limit policy. Save resolved type versions, model settings, tariff references and enabled capabilities. The platform assigns run, activation, logical-call and attempt identities; component assertions cannot overwrite authoritative identity.

A single work session may contain many runs and survive restarts. It does not grant state sharing or identify an MCP transport session.

## Candidate execution states

| State | Meaning |
| --- | --- |
| `created` | Admitted and recorded; execution has not started. |
| `running` | Work is eligible or active. |
| `stopping` | New dispatch is prohibited; cancellation/finalization is in progress. |
| `completed` | Required work completed successfully. |
| `failed` | An unhandled execution failure ended the run. |
| `cancelled` | Operator or control policy requested termination. |
| `timed_out` | Effective deadline expired. |
| `interrupted` | Backend continuity was lost; no automatic paid replay. |

### Transition and race policy

The following proposal makes Q08 reviewable. The platform serializes terminal decisions with dispatch admission; callbacks do not set run state directly. Preserve a structured primary reason and subsequent observations independently of the terminal label.

| Current state and condition | Proposed transition and effect |
| --- | --- |
| `created`; all required hosts ready | `running`; graph work becomes eligible. |
| `created`/`running`; operator stop | `stopping`, target `cancelled`, reason `operator_stop`. |
| `created`/`running`; run deadline expires | `stopping`, target `timed_out`, reason `run_deadline`. |
| `created`/`running`; any budget admission is refused | `stopping`, target `failed`, reason `budget_denied`; no rejected call is dispatched. |
| `created`/`running`; startup or unhandled operation failure | `stopping`, target `failed`, preserving the specific cause. An unhandled call deadline instead targets `timed_out` with reason `call_deadline`. |
| `running`; controller completes and all required outputs are valid | Atomically commit `completed` only if no stop decision exists, the run deadline is still open and no managed execution is outstanding. |
| `stopping`; local call dispositions recorded | Commit the chosen terminal outcome. Cleanup can still be pending/failed and accounting can remain unsettled; neither is represented as successful work. |
| Nonterminal state on backend recovery | `interrupted`; invalidate old work authority and reconcile outstanding calls/processes without replay. |
| Any terminal state; later response, stop or cost evidence | Preserve the outcome; append the observation or settle the original charge. No graph advancement. |

The first durably accepted stop cause determines the target outcome. At every admission/completion decision, check the effective run deadline first; work cannot succeed after expiry merely because its timeout callback is late. If success was already committed before a later stop request, the run stays completed. Store later causes as secondary observations without overwriting the first. Recovery of an uncommitted stop becomes `interrupted`, retaining its recorded intended outcome and reason.

Output publication and permission to schedule its dependent step share the same stop/deadline gate. A late validated response may be retained as evidence but cannot become a new successful binding after that gate closes. An ambiguous dispatch remains potentially performed; reconnecting never proves it safe to retry.

Shutdown progress (`pending`, `complete`, `failed`) and charge settlement are separate from the run outcome. The UI must show unresolved cleanup and spending explicitly. See [component lifecycle](component-lifecycle.md) for process ownership and bounded teardown. Cancellation/cleanup durations and their numeric defaults remain configurable profile choices under Q18.

## Accounting invariants

**Accepted scope (Q12, 2026-09-28):** run, saved work-session and monthly totals cover only managed Slow Thinker II calls. Spending by the original Slow Thinker or other tools is outside these budgets, even when they use the same provider account or API key. These limits are not provider-account spending caps. No accounting import, bridge or shared ledger with the original executor is in scope.

1. Before dispatch, atomically reserve a defensible maximum charge in run, session and monthly scopes.
2. Reservations compete against both settled charges and outstanding obligations. Multiple callers cannot spend the same balance.
3. Parent totals aggregate charge references; they do not create duplicate charges for child attempts.
4. An unknown or unbounded cost is not zero. Strict-cap execution rejects such an operation before it starts.
5. Save exact quantities, currency, rates and calculation policy. The [accounting policy](accounting-policy.md) proposes decimal-string boundaries, integer ledger units, upward rounding and admission-month attribution under Q07.
6. Failed, retried, cancelled and interrupted calls can still incur costs. Do not release obligations merely because a deadline or connection ended.
7. Reconciliation is idempotent and can append late evidence after execution becomes terminal, without restarting the graph.
8. Technical protocol round trips or continuations do not automatically constitute separately billable work. Correlate actual provider attempts and their authoritative usage.

A complete tariff file cannot alone guarantee a maximum charge; provider limits and the dispatched request must support the bound. Unresolved reservations remain unavailable until settled or resolved through an approved policy. Unexpected excess charges must be recorded and surfaced, never discarded to make the cap appear satisfied.

## Deadlines and failure behavior

Per-call and per-run deadlines include queueing, retries and nested work within their applicable scope. Descendants cannot extend the parent's remaining deadline. Use a monotonic duration source during execution and recorded wall-clock timestamps for inspection; restart recovery needs a separate explicit policy.

A budget refusal stops the entire run. Unhandled failures also stop the initial executor. Components may handle subcall errors within their allowed behavior. Retry policy must be explicit and must not automatically duplicate ambiguous side effects.

Proposed failure categories are invalid configuration/input, denied authority, unsupported capability, lifecycle violation, component failure, provider refusal/failure, invalid model output, deadline expiry and uncertain dispatch. Keep the original provider status/reference when available, with secrets removed. LLMCall's completed-response validation errors retain their [specific result envelope](llm-call.md#success-and-failure); transport errors are not converted into empty successful responses. The [provider matrix](openai-initial-profile.md#http-errors-and-uncertain-outcomes) proposes native HTTP error preservation; platform-generated errors and SDK verification remain Q04/Q06.

## Evidence envelope proposal

The [event schema](schemas/event.schema.json) defines a versioned envelope, not the entire event catalog. It requires an event ID, run and graph revision, sequence, timestamp, actor, event type, evidence classification and payload. Call and activation references are optional where inapplicable.

| Evidence value | Interpretation |
| --- | --- |
| `observed` | A platform-observed boundary or control event. |
| `reported` | A component's own statement about internal reasoning, state or progress. |
| `inferred` | An analytical interpretation tied to evidence and an analyzer version. |

The actor records the source; the platform records receipt. Proposed ordering is a durable per-run sequence assigned by the platform, not a claim that timestamps from different processes share a perfect clock. The [observation contract](observation.md) proposes the event catalog, causal identities, capture statuses and completeness rules; machine-readable per-event payload schemas remain Q10.

## Persistence and replay

Persist authorization and reservation evidence before external side effects. SQLite is selected. [ADR 0011](../adr/0011-local-persistence.md) proposes its detailed reservation, dispatch-intent and result/settlement boundaries, bounded payloads in the same store and explicit crash cases. These detailed semantics await approval; retention/deletion rules remain Q10. No event-sourcing framework is proposed.

Dispatch authorization is durable before sending. A stop committed before that authorization prevents it; afterward, cancellation is best effort because the request may already be in transit. Local transactions cannot atomically stop a remote provider. The accounting proposal keeps possibly dispatched attempts reserved until reconciled.

Analysis may read history without rerunning providers. Re-executing a graph creates a new run and new spending authorization; it is not a free replay. Missing usage and redacted payloads remain explicitly distinguishable from zero usage or empty output.
