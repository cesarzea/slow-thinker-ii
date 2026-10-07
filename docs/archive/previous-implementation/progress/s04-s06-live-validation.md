# S04–S06 Live Execution Validation

| Document control | Value |
| --- | --- |
| Report ID | SPRINT-S04-S06-LIVE-001 |
| Owner | Cesar Zea |
| Date | 2026-10-02, Europe/Lisbon |
| Status | Completed; native usage, resource provenance and history audited |
| Scope | Two revisions of one real two-provider resource collaboration |

This supplements the S04, S05 and S06 status reports. CI and browser tests use
simulated inference; these additional runs use the existing authorized provider
credentials and preserve all preceding expenditure within the USD 3 total.

## Scenario and installed composition

The [example graph](../contracts/examples/resource-collaboration.graph.json)
and [task](../contracts/examples/resource-collaboration.input.json) ask for a
90-minute workshop with one break and ticket income for six adults and three
children. Two ContextualCall agents wrap external ResourceAgent workers. The
proposer uses OpenAI `gpt-6-luna`; the reviewer uses DeepSeek `deepseek-flash`.
Both invoke the same deterministic calculator and persistent key/value memory
through MCP. All packages were prepared and installed in independent environments.

| Revision | Run | Outcome | Calls | Recorded cost |
| --- | --- | --- | --- | --- |
| `example-1` | `788acc7addd542ed9e56e2442971f334` | Completed; cleanup confirmed | 15 mediated, 2 real model calls | USD 0.000299100 |
| `example-2` | `1a6a889893f54851842a912da1c02554` | Completed; cleanup confirmed | 15 mediated, 2 real model calls | USD 0.000221500 |

The first reviewer returned a verdict referring to the proposal. The second
revision changed only its instructions to require a complete standalone plan.
It was saved through the production source-patch and immutable revision APIs.
The second result supplies the full seven-part schedule totaling 90 minutes,
one ten-minute break and ticket income of `96`.

## Independent recording checks

For both runs, the reviewer's direct proposal input exactly equals that run's
proposer output, and its shared memory read returns the same value. Calculator
calls return `96`. The second run's first memory read recovers the first run's
review at version 2. Reading the earlier result after the new revision confirms
it is unchanged. Request/response identities and native usage remain recorded;
DeepSeek supplied a response ID but no separate request ID in the captured response.

Independent rational arithmetic prices each call against its frozen tariff and
reconciles every settled charge, including the reviewed DeepSeek off-peak window.
No reservation remains unresolved. The two runs cost **USD 0.000520600** together;
all preceding and current authorized demonstrations total **USD 0.002651950**,
leaving **USD 2.997348050** of the original USD 3 allowance. The October ceiling
also accounts for the preceding month's charge rather than resetting the allowance.

The [sanitized evidence](../evidence/s04-s06-live-execution-20261002.json) retains
run IDs, native usage, reconciliation checks and result digests. Full task/native
recordings remain local; credentials and transport headers are excluded.

## Correction and interpretation limits

An initial installed startup failed because preparation supplied an unused outgoing
MCP client to resource-only hosts. No model request was dispatched. Preparation
now supplies such a binding only when outgoing resources or grants require it;
focused public preparation cases, both installed runs and full verification pass.

These observations establish actual mediated collaboration, persistent sharing,
provider independence and retained history for this case. The instruction change
is an author-created variant, not automatic optimization. No causal influence
analysis, statistical quality improvement or general agent reliability is claimed.
The actual runs were submitted through the authenticated production API; automated
browser journeys separately establish the user-facing configuration/execution path.
