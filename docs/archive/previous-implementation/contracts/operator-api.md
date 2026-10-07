# Operator API proposal

**Status: Approved first-cycle contract.** R01, R13–R20; Q06, Q08–Q11, Q18. This is the browser/backend boundary. It neither replaces MCP nor gives components operator authority.

## Scope and routes

Use authenticated, same-origin JSON HTTP requests under the proposed `/api/v1` prefix. The browser sends no provider credentials, executable launch commands or component grants. The initial implementation uses an explicitly configured bearer credential, exact local origins/hosts and no ambient cookie authentication. Browser login and configuration-file bootstrap remain application work; loopback binding alone is not authentication. Payloads are data and must never be rendered as executable HTML.

| Method and path | Request / result |
| --- | --- |
| `GET /workspace` | Current saved sessions, active-run identity, admission availability/reason and effective budget/profile references; bounded lists use cursors. |
| `POST /sessions` | Command identity and a display name; creates one saved session and returns its receipt. |
| `GET /graphs` | The bundled graph identities, exact revisions, titles and separate input schemas. |
| `GET /graphs/{graph_id}/revisions/{revision}` | That exact bundled definition and validated structural projection. No implicit latest-version substitution. |
| `POST /runs` | Command identity, saved session, exact graph revision, input and selected approved configuration revision; returns a durable admission receipt. |
| `GET /commands/{command_id}` | The stored admission/rejection receipt, including any resulting run/session identity. Reading cannot execute work. |
| `POST /commands/{command_id}/withdraw` | Idempotently withdraw a Start intent, including one whose receipt is missing; return its durable withdrawal disposition. |
| `POST /runs/{run_id}/stop` | Command identity; atomically closes admission if still open and returns the accepted/current stop disposition. |
| `GET /sessions/{session_id}/runs` | Bounded run summaries for saved history. |
| `GET /runs/{run_id}` | Consistent current run projection, including terminal, cleanup and settlement states. |
| `GET /runs/{run_id}/definition` | The run's immutable admitted definition/configuration snapshot, with secret references removed. |
| `GET /runs/{run_id}/events` | Bounded durable event pages with a fixed upper sequence. |
| `GET /runs/{run_id}/activations/{activation_id}` | Effective input/output and binding references, status, calls and exposed-report references. |
| `GET /runs/{run_id}/calls/{call_id}` | Caller/target, parent, attempts, request/response references, outcome, usage and cost references. |
| `GET /runs/{run_id}/payloads/{payload_id}` | Capture status and bounded content, or an explicit absence marker. |

All referenced objects must belong to the requested run/session. Session creation does not create a new monthly allowance. Reads cannot refresh agent authority, repeat provider calls, resume a sequence or reset accounting. Resource bindings do not authorize access to these operator routes.

The first profile has no graph upload/edit, pause/resume, trace-deletion or reconciliation-mutation endpoint specified here. Their policies require separate decisions. Limits are selected through versioned backend configuration; the wire schema for that configuration remains Q07/Q18. An invalid selection cannot mean unlimited execution.

## Start command and durable receipts

Before submitting Start, the browser creates and locally retains an opaque command identity. Retain the identity only, not prompts or credentials, in browser persistence. A new intentional run gets a new identity; transport retries of the same intent never do. Command identity is a deduplication key, not authentication or evidence of an accepted run.

Illustrative request for the existing review-cycle fixture; `local-example-1` is an unresolved configuration reference, not an installed profile:

```json
{
  "schema_version": "0.1-draft",
  "command_id": "start-example-1",
  "session_id": "session-example-1",
  "graph_id": "proposal-review",
  "graph_revision": "example-2",
  "configuration_revision": "local-example-1",
  "input": {"problem": "Suggest a plan for organizing a small technical workshop."}
}
```

An accepted Start returns HTTP 202 with a receipt such as:

```json
{
  "schema_version": "0.1-draft",
  "command_id": "start-example-1",
  "kind": "start",
  "disposition": "accepted",
  "target_id": "run-example-1",
  "reason": null,
  "replayed": false
}
```

This acknowledges durable creation, not ready hosts, funded future calls or completed work. The UI obtains current state from the run projection. Graph/configuration/input validation precedes admission; failures create no run or hosts. The backend checks current configuration, deadline/budget-policy validity and the single-workflow constraint again when admitting the command.

Persist command identity, its comparable validated request, receipt, run snapshot and `run.created` together at T1. A database uniqueness constraint serializes simultaneous submissions with that identity. A second request with identical content returns the original receipt and creates no run or dispatch. Different content with the same identity returns `command_conflict`; it cannot overwrite the original. Apply equivalent deduplication to session creation and Stop.

Retain rejected command receipts too, when authentication and request syntax permit a valid command identity. The same identity cannot silently become accepted after configuration or available budgets change; a corrected/new intent gets a new identity. Unauthenticated or malformed traffic belongs to bounded diagnostics, not a caller-selected command/run. If storage cannot durably accept the command, do not claim a receipt exists.

Command comparison follows input retention/redaction rules. If discarded content prevents proving that a repeated command is identical, return `command_not_comparable` with its existing result reference; never execute it again. Keep command identities and result tombstones for the store's lifetime in the initial profile. Future deletion must not turn a previously used identity into an unused key.

## Lost replies, stops and recovery

After a lost Start reply, disable a new Start and query the saved command identity. An accepted receipt opens the existing run; a rejected receipt shows its reason. A missing receipt does not prove that an earlier HTTP request cannot still arrive. Keep the action unconfirmed. The operator may explicitly resubmit the same command identity and unchanged body; the uniqueness rule still permits at most one accepted run. No automatic mutating retry or fresh command identity is allowed during recovery.

On browser reload, resolve any retained pending command and read workspace state before enabling Start. On backend restart, an existing receipt remains associated with its original run, even if that run is now interrupted. Reading or repeating the command cannot resume it. If local input was lost and no receipt can be found, do not fabricate the old body or silently create another intent; show the uncertainty for explicit resolution.

To resolve an unconfirmed Start without resubmitting it, the operator can withdraw that command identity. Serialize withdrawal against T1. If Start has not been admitted, persist a withdrawal tombstone that rejects any later arrival with that key. If it was admitted, retain the original receipt and apply the normal stop gate to its run; report that outcome separately. Repeating withdrawal has no new effect. Reject withdrawal of a known non-Start command. This requires no missing input to be reconstructed and does not claim to undo work already dispatched.

Stop acceptance and the execution admission gate share the [transaction/race policy](execution.md#transition-and-race-policy). An accepted Stop returns HTTP 202 while finalization can remain pending. For an already terminal run, return HTTP 200 with `already_terminal` and the existing outcome. Neither acknowledgement promises that a provider stopped charging. Multiple Stop commands cannot replace the first accepted primary cause; their own receipts remain inspectable.

Enforce one admitted nonterminal run in the backend, including across browser tabs. A second distinct Start receives `active_run_exists` with the active run identity. When cleanup cannot establish that old managed processes have stopped, admission remains unavailable with an explicit reason even if the old run is terminal. Unsettled costs alone remain budget obligations and do not imply that a process is still running.

## Authoritative read model

Build each projection from one consistent backend read snapshot. The run projection contains the run/session identities, exact graph revision, lifecycle outcome/reason, timestamps, cleanup and settlement summaries, planned-node and activation summaries, call references, costs/obligations and references to detailed evidence. Money remains decimal strings with currency and basis; the browser never recomputes authoritative balances.

Include `last_event_sequence` for evidence correlation, not as the only cache version. Shared session/month policy and balances can change without adding a run event. Return an opaque `view_token` and matching ETag covering every supplied field and the effective monthly-period identity. A conditional read may return 304 only when that complete representation is unchanged. Run elapsed time can be displayed from its recorded timing values without treating every clock tick as a new durable event.

The browser permits at most one outstanding read per selected resource. Associate it with a local selection generation; discard a reply after changing run, view or backend connection generation. A different opaque view token means changed content, not a sortable version. A lower run-event sequence on reconnect triggers recovery/refresh handling rather than overwriting a newer view. Backend continuity information must distinguish restart/recovery from ordinary polling; its concrete wire field belongs to the schema review.

Render Start/Stop acknowledgement independently of the latest projection. After an accepted command, a stale cached projection cannot re-enable Start or make Stop appear unrequested. Revalidate using reads; show stale/unknown state on disconnection rather than inventing a terminal outcome. Continue bounded refresh for outstanding cleanup/settlement after a run finishes, as proposed in the [visual model](../architecture/visual-model.md#proposed-live-update-behavior).

## Paging, payloads and errors

The first event page captures `through_sequence`, the highest durable sequence in its read snapshot. Subsequent opaque cursors bind run, filters, upper boundary and last delivered sequence. Return events in ascending order with no duplicates or skipped existing events within that boundary. Later events appear in a fresh read. Invalid/foreign cursors fail explicitly; clients cannot supply another run inside a cursor to bypass access checks. Historical run lists use an equivalent stable boundary.

Payload absence is successful inspection of a known record: return its `unavailable`, `redacted`, `omitted_size_limit` or `deleted` status and reason, without fabricated content. Use 404 for an unknown or mismatched object. Paginate metadata lists; do not split JSON into invalid fragments or silently truncate text. Content exceeding the approved per-response limit is reported explicitly. Payload/schema/list limits remain Q18.

Use a versioned error envelope with stable `code`, diagnostic `message`, request reference and optional structured field issues. Proposed mappings are 400 for malformed syntax, 401/403 for operator authentication/authorization failure, 404 for absent objects, 409 for command/state/revision conflicts, 422 for invalid graph/input/configuration, 413 for excess size and 503 for unavailable backend/storage. HTTP diagnostics never expose stack traces, credentials or local filesystem paths. These operator errors are separate from native model-client errors.

## Acceptance and remaining decisions

Verify simultaneous duplicate Starts, conflicting bodies, lost replies before/after T1, explicit same-key resubmission, two browser tabs, rejected-command replay after a policy change, backend restart, repeated Stop, late settlement, stable paginated reads while events arrive, foreign cursors, tombstoned payloads and equal event sequences with changed budget projections. Count actual accepted runs and provider attempts; a disabled button is insufficient evidence of idempotency.

Q11 records the approved first-cycle command/read semantics; machine-readable HTTP schemas, authentication/bootstrap and the polling/capacity controls remain implementation obligations. The implemented persistence boundary and its verification scope are recorded below.

## Implemented persistence boundary

`SqliteOperatorStore` implements saved session creation, immutable configuration revisions, atomic Start admission, durable rejection receipts, Stop and withdrawal. Configuration is supplied by trusted backend composition; no browser or component receives this storage API. `PreparedStart` is the result of trusted graph/input/component preflight, not a user-submitted execution object. The installed graph checks exercise that path after compiling each example.

T1 compares the canonical intention, rechecks the active configuration and saved session, rejects a regressed UTC admission clock, checks the single-workflow/cleanup gate, and writes the run, frozen configuration/input snapshot, budget scopes, command receipt and `run.created` together. A `CommandResult` distinguishes a replayed receipt from a newly accepted command; only the latter can hand new work to a runtime owner. Reading a receipt never starts a runtime. Withdrawals retain the original Start receipt and store their disposition separately; a missing Start receives a permanent tombstone.

The initial trusted configuration has independent limits and resource-reference JSON under one immutable configuration revision. Explicit activation preserves settled/reserved amounts and refuses caps below commitments; it changes saved-session caps and the current UTC month cap, while existing run caps and old-month caps remain unchanged. The preparation adapter validates provider/installation selections; the JSON startup loader supplies the trusted profile; a configuration editor remains outside this cycle. Resource-reference JSON must contain references rather than credentials.

Stop closes the durable admission gate in the receipt transaction. `ExecutionCoordinator` then revokes transient authority and cancels owned work. The authenticated HTTP command routes now use that coordinator. Terminal runs continue blocking admission until their recorded cleanup confirms no pending calls and all hosts stopped or never started. Backend restart does not replay work or infer process exit from a saved PID. Startup reconciles durable owned-process identities; unverifiable ownership remains unconfirmed and blocks admission.

Schema version 4 adds these records to the existing store, retaining a verified pre-migration backup. Tests cover duplicate/conflicting Starts, concurrent Start/withdrawal, durable rejections, lost-reply recovery through receipt reads, rollback of session/Start/Stop/withdrawal writes, configuration changes, shared monthly balances and migration from existing data. This evidence does not establish authenticated HTTP routes, paginated projections or browser execution controls.

## Runtime command ownership

`ExecutionCoordinator` retains pending commands independently of HTTP waiters. Cancelling a browser request cannot cancel an accepted run or abandon an admission still being committed. Concurrent identical intentions share one pending task; conflicts fail explicitly. Stored receipts are compared before preparation, so replay after restart does not depend on the continued availability of the original component packages. Only a newly accepted Start is assigned a runtime owner.

Trusted preparation supplies the frozen start record, permission policy, unstarted environment, graph program and model bindings. The coordinator checks the prepared intention and backend runtime identity before T1. Preparation has a finite timeout and capacity bound; tasks that delay cancellation remain tracked until they finish. Start and control commands have separate capacity bounds, so preparation saturation does not consume Stop/withdrawal capacity.

Runtime construction uses admitted deadlines and call limits. Failed construction records a terminal outcome and confirms that no hosts were launched, when storage remains available. The owner's native model gateway accepts only that run's current invocation grants. Stop, withdrawal and backend shutdown reach both the durable gate and transient authority. A command-recording failure closes live authority rather than continuing unrecorded work.

Closing the coordinator rejects new commands, cancels preparation, stops owned runs and waits within its shutdown bound. Its result explicitly lists outstanding command, preparation and run tasks; a timeout does not prove that they stopped. Admission already in flight remains owned and cannot launch business work after shutdown begins. Process-cleanup evidence and startup orphan reconciliation remain separate obligations. Application lifespan handling must respect an incomplete shutdown result.

Tests include cancelled command waiters, replay after component removal, Stop during work, shutdown during T1, unresponsive preparation, expired admitted deadlines, recording loss and actual MCP process cleanup. Five additional installed checks execute all four bundled graphs through the coordinator/native gateway and stop a fifth run during its simulated upstream request, retaining its uncertain cost. These checks now use `InstalledWorkflowPreparer` for production preparation. JSON startup configuration and browser execution controls are implemented.

`InstalledWorkflowPreparer` selects exact installed versions and registered host adapters from validated resource settings. It freezes original/effective configurations, operation contracts, installation evidence and the validated tariff revision before T1. Provider credentials resolve only through explicitly registered references and are excluded from that snapshot. Daily revalidation renews tariff freshness without replacing historical revisions. Preparation rejects stale or mismatched prices; T1 rechecks its admission cutoff so delayed preparation cannot outlive the reviewed pricing window. No business host starts during preparation.

## Implemented HTTP boundary

`create_app(..., execution_setup=...)` composes saved-session creation, Start, Stop, withdrawal, receipt reads, workspace state, run state, admitted definition and paginated session history. `ExecutionSetup` supplies trusted dependencies; browser bodies cannot select executables or supply prepared snapshots. The `configured_app` factory reads `SLOW_THINKER_CONFIGURATION`; without that variable it serves the viewer. Invalid configuration prevents startup rather than silently disabling execution. Graph-detail/input-schema endpoints remain outstanding; the trace and activation reads below are implemented.

Execution-enabled applications require operator authority on every `/api/v1/` route, including catalogue reads. The native `/v1/` route retains separate invocation authority. Bounded strict JSON rejects duplicate keys, nonfinite numbers and undeclared fields; diagnostics omit internal exceptions. Session creation joins the coordinator's owned command tasks, so a disconnected waiter cannot abandon its transaction.

Read projections use one SQLite transaction, exact decimal money, a backend generation and an opaque `view_token` matching the ETag. Tokens cover shared budget changes, not only run events. Signed cursors bind the query/session and initial row boundary. Inspection does not update cleanup flags. The application closes the coordinator during shutdown; incomplete shutdown raises an explicit error and retains its database lease.


`GET /api/v1/runs/{run_id}/result` returns the recorded final JSON for a completed
run, or an explicit `unavailable` disposition when no final output is publishable.
Unknown runs return 404. It uses the same operator authority, read transaction,
response bound and complete-representation ETag as other inspection routes.


## Implemented trace inspection

Event reads return at most the configured page size in ascending durable sequence,
with `through_sequence` fixed on the first page. Signed cursors bind the run and
upper boundary. Events expose receipt timestamps, call identities and payload
references; large content is retrieved separately. Returning to the first page
obtains a fresh boundary. Event reads never replay work or append evidence.

Call reads expose the persisted caller/target, parent, activation/node and attempt
identities, disposition, request/pricing references and the attempt's own ledger
amounts. Receipt pages retain successful, failed and late responses, distinguishing
receipt success from permission to publish downstream. Their signed cursors bind
the run, call and initial receipt window. Parent calls do not aggregate child costs.

Payload reads resolve only retained database records belonging to the requested
run. Present JSON `null`, empty text and empty objects are content, not absence.
Missing usage/pricing has `unavailable` status and a reason; unknown objects return
404. Oversized HTTP representations return `response_too_large` (413), without
truncating JSON. All reads share operator authentication and complete-content ETags.
The current representation exposes retained records; it does not establish complete
internal reporting, field-level redaction provenance or the full proposed event
catalog. Those recording capabilities remain implementation work.

The browser inspector links events, calls, parent calls, arguments, response and
usage payloads. Each evidence panel has explicit refresh and bounded paging;
closing or replacing a panel discards late read replies. Main run/budget state
continues its existing polling independently. Inspection never dispatches a command.


Activation reads use the recorded activation identity and its unique originating
call. They expose participant/node identities, the effective request, eligible
published output, binding provenance and a bounded page of the activation's calls.
Repeated uses of the same participant remain separate. Failed or unfinished
activations have no published-output reference; their retained responses remain
accessible through call inspection. Ambiguous originating records fail explicitly.

Binding inspection labels its source as the admitted definition. For the initial
sequence profile, run-input bindings link to the saved input and node-output
bindings link to one unambiguous earlier published response, retaining the JSON
Pointer. Multiple candidate activations are reported as unavailable rather than
chosen by recency. Missing historical inputs retain an absence marker. These are
binding references and recorded arguments, not claims of causal influence or
reconstructed reasoning.

## S03 authoring extension

The [personal experiment library](personal-experiments.md) specifies additional
authenticated definition routes, exact query identities, raw JSON writes and bounded
errors. Existing execution, accounting and inspection routes retain their behavior.
