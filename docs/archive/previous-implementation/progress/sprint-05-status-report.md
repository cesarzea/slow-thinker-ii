# Sprint Status Report — S05

| Document control | Value |
| --- | --- |
| Report ID | SPRINT-S05-001 |
| Report version | **0.0.5.1** — V0.0, Sprint 5, Revision 1 |
| Owner | Cesar Zea |
| Reporting date | 2026-10-02, Europe/Lisbon |
| Scope | External components, calculator and private/shared memory |
| Delivery status | Locally verified, including installed real collaboration |
| Publication status | Delivery preparation; hosted checks and owner review pending |

This is a development checkpoint, not a product release. Package versions remain
Python `0.1.0.dev1` and frontend `0.1.0-dev.1`.

## Delivered outcome

Users can prepare a trusted external Python component with an explicit descriptor,
registration and exact dependency closure, then run it as an independent MCP host.
The ResourceAgent example extends LLMCall without becoming a platform-owned type.
Existing package preparation remains available through the same tooling.

Calculator provides bounded, exact Decimal arithmetic without executable input.
KeyValueMemory provides version-checked durable state with explicit namespaces,
run-local or persistent retention, and private or shared bindings. ContextualCall
composes memory, calculation and a managed worker; ordinary and routed workers
remain usable. All nested calls pass through platform permissions, recording,
deadlines and applicable budgets. Resource sharing grants no implicit authority.

## Acceptance evidence

The [delivery block](../specification/s04-s06-delivery.md) defines A08–A14 and A22;
the [resource contract](../contracts/tools-memory.md) defines configuration and
failure behavior. Component and integration tests exercise external wheel builds,
offline installation, subprocess MCP calls, private isolation, persistent/shared
state, compare-and-set races, cancellation and failures after paid work.

The [live demonstration](s04-s06-live-validation.md) executed two independent
installed workers using OpenAI and DeepSeek. The calculator returned `96`; the
reviewer received the exact proposal and shared memory value. A later revision
recovered the preceding review from persistent memory while retaining the earlier
result. An initial unused-client bootstrap defect was corrected before any paid
dispatch; installed startup and the complete suite then passed.

The shared runner passed **2,204 Python tests, 340 frontend tests and 20 browser
journeys**, including all mandatory static/security/build and independent coverage
gates. See the [verification record](../verification.md#provider-resource-and-workspace-delivery--2026-10-02).

## Boundaries and next checkpoint

These are the first tool and memory implementations. mem0, graph memory,
untrusted-code isolation, parallel joins and simultaneous multi-port emissions are
later scopes. The [workspace guide](../workspace.md) describes supported resource
configuration. Hosted verification and owner review remain publication requirements.
