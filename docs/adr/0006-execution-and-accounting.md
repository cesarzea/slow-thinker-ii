# ADR 0006: Separate execution state, spending reservations and evidence

- Status: Proposed
- Recorded: 2026-09-27
- Decision-maker: Cesar Zea
- Requirements: R11–R16, R20, R23
- Open questions: Q07–Q10

## Context and problem statement

Deadlines, cancellation and backend crashes can end useful execution before the final cost is known. Multiple nested calls can compete for one budget. A run's terminal state cannot be used as proof that all charges are settled.

## Decision drivers

No oversubscription of available budget, no double counting, durable attribution, bounded scheduling, and truthful uncertainty.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Durable admission, atomic reservations and later settlement | Controls committed spending and preserves late evidence | Requires transaction and reconciliation design |
| Count costs only after responses | Simple ledger | Cannot prevent concurrent overspending |
| Release every reservation on timeout | Quickly restores apparent balance | Can understate outstanding provider charges |

## Decision outcome

Recommend one admission authority across run, work-session and monthly scopes, with atomic cost reservations before billable dispatch. Account each billable attempt once, aggregate by references, and preserve unresolved obligations after execution stops. Use decimal monetary values with explicit precision and rounding.

The requirements for limits and whole-run stops are already agreed. Exact persistence boundaries, reservation ownership, lifecycle states, reconciliation and month attribution remain proposed or open.

The owner closed Q12 on 2026-09-28: all three budget scopes cover only managed Slow Thinker II calls. The original executor remains independent. This scope decision does not accept the remaining proposals in this ADR.

The [transition table](../contracts/execution.md#transition-and-race-policy) now proposes a failed run with reason `budget_denied`, a deadline check before admission/completion, and the first durably accepted stop cause as primary. Process cleanup and financial settlement remain separate from terminal execution. Review these details under Q08; they are not accepted through publication.

## Consequences

The UI must distinguish execution status from accounting finality. A zero-cost declaration still needs an explicit trusted policy. Strict-cap mode rejects unbounded operations. Cancellation cannot promise provider billing stops immediately.

Budget displays must identify their Slow Thinker II scope. Sharing a provider account or API key with other software does not bring that software's spending into these totals; no integration with the original executor is required.

## Confirmation

QA06–QA09, QA11, QA17 and QA25 cover races, unknown costs, late results, restart and accounting scope. Review the [accounting policy and worked cases](../contracts/accounting-policy.md) and [ADR 0011 transaction/crash proposal](0011-local-persistence.md) before implementation. Documentary examples do not prove concurrent or durable behavior.
