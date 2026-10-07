# Observation and evidence proposal

**Status: Approved first-cycle contract.** R11–R12, R16, R18–R19, R25–R26; Q10–Q11, Q18. This defines the semantic record needed for inspection and later analysis. The [event envelope](schemas/event.schema.json) defines the common record; concrete projections and configured capture limits are covered by the [verification record](../verification.md).

## What observation means

Record every managed application invocation, including controller decisions, nested resource calls, rejection, failure and cancellation. Capture effective arguments and returned content after mandatory secret removal. Transport bookkeeping is correlated diagnostic evidence; it is not another graph activation or billable attempt. Readiness/discovery and host failures must also be inspectable.

An observed response means the platform observed its delivery. It does not certify the truth of its text, the component's claimed state or its reasoning. Provider-reported token usage and tariff-calculated cost retain their sources even when recorded in an observed boundary event.

Internal instrumentation is optional per component. Record reported progress, state, explanations and provider-exposed reasoning only when supplied. Record their absence as unavailable, not as an empty reasoning transcript or an inferred reconstruction. A provider's reasoning summary remains a summary; opaque reasoning tokens are not readable thought content. The platform must not add hidden prompts or extra model calls to manufacture missing reasoning.

## Identity, ordering and payload references

Every event uses the immutable run/graph identities and platform-assigned per-run sequence from the envelope. `occurred_at` is the platform's UTC observation/receipt time. A component's claimed source timestamp belongs in the payload as `source_occurred_at`; it cannot replace the platform timestamp or order. Use monotonic durations for live timing. Sequence establishes durable receipt order, not a total ordering of internal events across processes.

Call events identify caller, target instance/operation, `call_id`, `parent_call_id` when nested, and `activation_id` when applicable. Put the attempt identity in the event-specific payload. Component reports are stamped with their authenticated call context; components cannot choose another activation. A report received after invocation authority closes is rejected, except for the separate trusted late-settlement channel.

Payload records have their own identity, media type, capture status, size when known, and provenance. Store payloads transactionally with their references; identifiers are storage references, not arbitrary filesystem paths or fetchable URLs. Reuse references where a component output is bound into a later input. Save the resolved downstream input and binding provenance so later analysis can establish what was actually supplied.

Capture statuses are `present`, `redacted`, `unavailable`, `omitted_size_limit` and `deleted`. Empty text, `{}` and `null` can be legitimate present values. Unavailable/deleted content has an explicit reason and no fabricated value. Partial redaction retains permitted content plus field-level markers. Hash only the retained representation by default; do not retain a secret-derived digest under the assumption that it is harmless.

## Initial event catalog

The following names and payload requirements are proposals. All core events below are platform-observed except `component.reported`. State changes append evidence; they do not overwrite history.

| Event | Required payload content beyond the envelope | Causal/validation rule |
| --- | --- | --- |
| `run.created` | Saved-session identity, immutable definition/input/profile references, effective limits | Before host startup or graph work; transaction T1. |
| `run.started` | Saved-session and run-input references, readiness evidence | Once all required hosts are ready. The existing single-event fixture illustrates this event, not a complete trace. |
| `run.stop_requested` | Primary/secondary cause, intended outcome, initiating authority | Admission closes atomically with acceptance of the stop. |
| `run.finished` | Terminal state, reason, cleanup and settlement summaries | One terminal outcome; later financial updates do not change it. |
| `host.state_changed` | Host/instance identities, previous/new state, readiness or failure details | Process identity is distinct from component instance and invocation. |
| `activation.started` | Node, participant, resolved input and binding references | Each repeated use of a participant has a distinct activation. |
| `activation.finished` | Outcome, output/error references, duration, child-call references | Success cannot bind an output while the parent still has outstanding child work. |
| `call.requested` | Authenticated caller, target, operation, argument references, deadline | Record before dispatch; parent/activation links come from platform context. |
| `call.rejected` | Requested operation, rejection stage and reason | No target dispatch. Requests with no authenticatable run context belong to local security diagnostics, not a caller-selected run. |
| `call.dispatch_authorized` | Attempt, resolved target, saved request reference, reservation reference if billable | Durable T3 boundary; not proof of external provider acceptance. |
| `call.response_received` | Attempt, response/error reference, source metadata, receipt time, late-response flag | Retain late delivery without changing a terminal call or publishing downstream output. |
| `call.cancel_requested` | Call/attempt, cause, transport action and whether its delivery is known | Cancellation is a request, not proof that execution or billing stopped. |
| `call.finished` | Terminal call disposition, response/error references if available, measured duration, transport uncertainty | One terminal disposition; a later receipt or charge does not rewrite it. |
| `usage.recorded` | Attempt, usage source/reference, reported categories and missing fields | Duplicates and corrections retain source identity; no implicit zero categories. |
| `accounting.changed` | Attempt, change kind, reservation/charge references, amount basis, tariff/policy references, original scopes | Covers reservation, settlement, release and adjustment; one contribution per attempt. |
| `component.reported` | Report kind, schema/version, payload reference, optional source timestamp | Evidence is `reported`; actor is the authenticated component. Kinds include progress, state, explanation and exposed reasoning. |
| `cleanup.changed` | Owned host/call, cleanup state, reason | Cleanup can change after a terminal run without changing its outcome. |
| `evidence.gap` | Affected object, missing category/interval when known, reason | Never invent a missing-event count or content. The gap remains visible to analysis. |

Reported reasoning delivered inside a response can reuse its payload reference in `component.reported`; the response boundary remains observed, while the explanation remains reported. A later analyzer has a separate namespaced event/schema, evidence `inferred`, source-event references and analyzer version. No first-cycle influence conclusion is generated by this catalog.

Readiness and discovery requests use the call events with a bootstrap/protocol classification and no graph activation. These remain distinguishable from component business calls and do not gain business-call authority. The platform records the metadata needed to diagnose their failures without duplicating protocol round trips as model attempts.

Extension reports require a registered namespaced kind and versioned payload schema. Unknown/unvalidated reports are retained as rejected diagnostics within configured bounds; they cannot impersonate a core event or change execution state. Complete field schemas, extension registration and diagnostic limits remain Q10/Q18.

## Capture failure and retention

Validate request size before dispatch. For oversized responses, retain usage and boundary metadata where possible, mark omitted content explicitly and fail the affected operation with a capture-limit error; do not pass an unrecorded response downstream. Evidence-rate and storage limits also need explicit failure policies. Dropping events silently is not an acceptable way to keep a run green.

If durable storage fails, close new admission and attempt cancellation. The interface reports a recording failure from current process state; it must not claim an event was saved when its write failed. On recovery, append a gap where the missing interval can be established, and preserve unresolved accounting as specified in [ADR 0011](../../../adr/0011-local-persistence.md).

Propose retaining local experiment evidence until explicit operator deletion for the first cycle; scheduled expiry is later work. Deletion scope and confirmation still require Q10 review. Removing payload content must preserve absence markers and the accounting facts needed to avoid resetting budgets. Provider credentials, bearer grants and authentication headers are excluded from recording from the outset. Additional configured redaction is applied before persistence and shown as missing evidence; it cannot be described as full-content capture.

## Inspection and later analysis

The inspector should expose effective inputs, outputs, calls, available internal reports, errors, timing, usage and costs with unresolved amounts separate. The trace is operator-visible; agents do not gain trace-reading authority merely because they appear in it. All totals link back to leaf attempts rather than duplicate parent charges.

A future influence analysis can compare before/after artifacts and the proposals actually received, including multiple possible sources. It can use reported explanations as supporting evidence while keeping similarity, self-report and causal inference distinct. Missing/redacted content limits the claim and must travel with the analysis result. Repeated endorsement can be evidence of deference, but is not by itself proof that independent assessment was absent.

QA05, QA12, QA21 and QA26 cover this contract. Acceptance requires a captured run with nested calls, repeated participant use, one absent internal report, one redaction and one late/failed response. A generic event-envelope schema check alone does not establish recording completeness.
