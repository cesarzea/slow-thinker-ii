# Accounting policy proposal

**Status: Approved first-cycle contract.** R13–R16, R23; Q03, Q07–Q09. Only Slow Thinker II is in scope. Daily tariff imports, the SQLite ledger and managed execution have implementation tests. See the [verification record](../verification.md#first-cycle-delivery).

## Currency, periods and policy changes

Recommend USD for the first profile, matching the selected provider's published rates, with no currency conversion. Use calendar months in a configured IANA timezone, initially UTC. Record the timezone and exact UTC interval `[start, end)` for each period; display that scope alongside the monthly budget.

An attempt belongs to the month of its durable reservation admission, not the month of its response or invoice. Save the run, saved work-session and period identities on the attempt. They never change during reconciliation. One run spanning a boundary can therefore contain attempts assigned to different months. A new month has its own allowance; it does not erase previous obligations or reset run/session totals.

Currency and timezone are selected when the accounting store is initialized. The initial profile rejects subsequent changes to these two settings once accounting entries exist; a later migration must define period overlap and conversion explicitly. Changing the computer's timezone cannot create another monthly allowance. Detect a clock moving behind the last admission timestamp and suspend new admission until corrected; monotonic call/run deadlines remain separate.

Budget amounts are configurable decimal strings. Zero permits no positive-cost admission. Missing required limits are invalid; they do not mean unlimited. Save the effective policy revision. Reject a limit reduction below existing commitments; increasing a session/month limit is an explicit operator change, never an agent action. A running run retains its run cap and can only become more constrained by higher-scope policies. Starting another session does not reset the shared monthly scope.

## Exact amounts and admission

Propose an accounting quantum of USD `0.000000001`. Represent ledger amounts as integer quanta and public monetary values as decimal strings. Limits must be exactly representable; reject excess precision and integer overflow. Rates and usage calculations use exact decimal/rational arithmetic, with no binary floating-point conversion.

Sum an attempt's charge categories before rounding. Round its reservation upward to the next quantum. On settlement, retain the exact calculated amount and round the accounted amount upward once. Preserve any rounding adjustment separately; the UI must not label that adjustment as provider-billed usage. UI formatting cannot change ledger comparisons or display a positive charge as an exact zero.

For each of the three scopes, admission requires:

`settled accounted charges + outstanding obligations + new reservation <= configured cap`

Equality is allowed. An already funded attempt may complete; any later denied admission stops the whole run. Atomically accept the reservation in every applicable scope or in none. Never acquire money separately in each scope. Parent agents and controllers aggregate references to child charges; they do not charge those calls again.

An unsettled attempt contributes one obligation: its reserved bound, or a larger already evidenced cost if the bound has been exceeded. Partial usage is evidence within this obligation, not a second charge. A settled attempt contributes only its accounted charge. Unknown usage, transport failure, cancellation and elapsed time never imply a zero charge or release a reservation.

## Tariffs and trustworthy bounds

Automatically import and update tariffs once per day from the [Vercel model catalogue](https://ai-gateway.vercel.sh/v1/models), as selected by the owner. The local backend performs the refresh every 24 hours while running and checks for a missing catalogue or overdue refresh on startup. Reading the public catalogue does not require routing model calls through Vercel. [Source API documentation](https://vercel.com/docs/ai-gateway/models-and-providers#dynamic-model-discovery).

Validate the imported model/provider, tier, region, units and charge categories against the actual billing profile before publishing a local revision. A failed download or invalid catalogue preserves the last validated revision and records its age and the refresh error; it must not replace missing prices with zero. Existing validity and admission checks still apply. Compatible rate updates are automatic; unsupported billing semantics require review.

Each revision records provider/model and applicable tier/region/context band; currency; source URL and retrieval/validation timestamps; effective/review dates; metered units; decimal rates; category inclusion/exclusion rules; and calculation/bound-policy version. Each new run selects a validated revision and stores its immutable contents and digest, referenced by its attempts. Daily updates do not change running or historical executions or reprice their charges.

Reject unknown charge categories, unsupported billing profiles, expired review dates and incompatible currencies before dispatch. A rate table alone is insufficient: the adapter must establish a conservative input bound, enforce the output maximum and cover all applicable charges. Estimates without a justified upper bound do not authorize strict-cap calls. Cache categories must state whether they overlap other counts; never add both a total and its included subtotal.

The [initial OpenAI proposal](openai-initial-profile.md#proposed-initial-bound-published-model-capacity) uses published model capacity and maximum applicable rates for a conservative reservation, then settles by actual reported categories. It may deny a request whose probable cost is small because its defensible reservation exceeds the remaining allowance. Surface that distinction without relabeling the reserve as a charge or silently increasing the budget. Provider capacity/rate assumptions remain explicit; a local reservation cannot enforce a provider's invoice behavior.

Actual reported token counts multiplied by a saved tariff are a calculated cost, not a provider invoice. Record the amount's basis as `usage_times_tariff`, `provider_reported_charge` or `operator_resolution`, together with its evidence. Charges above the bound are recorded in full, stop an affected run if it is still active and block new billable admission using that bound/profile until reviewed; never clamp them to the budget or rewrite a terminal run outcome. Resolving a pricing discrepancy requires explicit review, not an automatic tariff change during the run.

An explicit retry creates a new attempt and reservation. It cannot reuse money committed to an ambiguous earlier attempt. The initial provider profile disables hidden retries. A component's fixed fee and its nested provider charges may coexist only if the billing contract explicitly declares them distinct; no implicit markup is inferred.

## Settlement and missing evidence

Settlement atomically replaces the original obligation with one accounted charge and appends its evidence. Repeated delivery of the same source record has no additional effect. Conflicting evidence is retained for review; it is not treated as a second attempt or silently overwritten. Corrections append an adjustment to the original identities and period.

The first cycle does not need provider-invoice synchronization. When usage is unavailable, keep the obligation visible indefinitely. Release without usage only after authoritative evidence that no billable dispatch occurred, or an explicit operator resolution identifying the amount, reason and supporting evidence. An operator estimate is labeled as such, not as measured usage. No automatic expiry, browser restart or deletion of a trace payload restores allowance.

## Worked acceptance examples

The following synthetic amounts test policy arithmetic; they are not provider tariffs or configured defaults. Other scope limits are assumed sufficient unless stated.

| Case | Given | Required accounting result |
| --- | --- | --- |
| AP01: equality | Cap `1.000000000`, settled `0.600000000`, obligations `0.300000000`, new bound `0.100000000` | Admit; commitments equal the cap exactly. |
| AP02: competing calls | Available `0.000600000`; two callers each request `0.000400000` | At most one is admitted. The second denial stops the run; the first obligation remains until resolved. |
| AP03: settlement and duplicate | Reserve `0.001500000`; complete usage prices at `0.000900000`, delivered twice | Charge once; release `0.000600000` in each applicable scope. |
| AP04: month boundary | Reserve AP03 on `2026-09-30T23:59:59Z`; settle at `2026-10-01T00:00:02Z`, UTC policy | September changes from a `0.001500000` obligation to a `0.000900000` charge; October is unaffected. Run/session totals settle normally. |
| AP05: unknown outcome | Timeout after possible provider acceptance with bound `0.001500000` | Retain the full obligation; no automatic replay or zero-cost settlement. |
| AP06: sub-quantum amount | Exact calculated cost `0.0000000004` | Account `0.000000001`; preserve exact cost and `0.0000000006` rounding adjustment. |
| AP07: excess | Bound `0.001500000`; authoritative cost `0.001700000` | Record the full `0.001700000`, flag the `0.000200000` excess and block further affected dispatch. |
| AP08: one scope fails | Run/session allowance covers `0.001500000`; month allowance is `0.001000000` | Deny in all scopes, create no partial reservation and stop the run. |
| AP09: categories | Synthetic input total 100, including 40 cached tokens | Charge 60 ordinary and 40 cached tokens when categories are disjoint; reject an unspecified category relationship. |
| AP10: policy update | Existing commitments `0.750000000`; requested cap `0.500000000` | Reject the reduction; preserve commitments and policy history. |

These are acceptance specifications. Provider-bound validation, concurrent database transactions and restart behavior require implementation evidence. See [execution semantics](execution.md), [storage proposal](../../../adr/0011-local-persistence.md) and QA06–QA09/QA25.
