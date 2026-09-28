# Component and invocation lifecycle

**Status: Proposed first local profile, 2026-09-28.** R02, R05, R08–R16; Q05, Q08, Q17. This makes the initial per-run hosting proposal reviewable; it does not close those questions or implement a host.

## Independent lifetimes

| Object | Initial ownership and lifetime |
| --- | --- |
| Component type/package | Installed independently; exact artifact resolution retained with each run. |
| Configured instance | Belongs to one run with immutable configuration and resolved bindings. |
| Host process | One per configured instance per run; reused for its sequential invocations. |
| LLMCall implementation object | Fresh Python object for each invocation, including inherited implementations; distinct from the stable configured-instance identity. |
| Invocation context | New for every admitted operation; contains platform-assigned authority and causal identity. |
| Agent-private state | Declared by the component; the first LLMCall profile retains no conversation between invocations. |
| Resource data | Governed by explicit ownership, persistence and reset rules, independently of host lifetime. |
| Evidence and accounting | Retained by the platform after execution; unsettled obligations can outlive it. |

An activation is one scheduled graph-node use. Nested operations have their own call identities and contexts while retaining the originating activation. A process identity is never used as a substitute for any of them.

## Start and readiness

1. Validate the complete selected definition, effective schemas, permissions, resource bindings and supported execution modes. Resolve trusted installation, limits and model profiles before launch.
2. Persist the admitted run and its exact configuration. Launch the required hosts through trusted installation records; do not install or update packages during a run.
3. Validate protocol discovery and effective operation schemas for every instance. Complete all required readiness checks before scheduling the first graph activation.
4. If a host exits, fails discovery or exceeds the configured startup deadline, stop admission, tear down hosts already started and record a startup failure. No automatic host restart or paid replay is part of this profile.

Constructors and readiness checks do not initiate model/tool business operations. A model warm-up, memory population or other billable initialization must be explicit managed work, not a hidden launch side effect. Required bindings may refer to peers being launched; readiness must not execute peer operations or impose an implicit topological sort on resource references.

Startup consumes the run deadline. No readiness event or progress message extends that deadline. Numeric startup and shutdown settings belong to the resolved configurable limits profile; their defaults remain Q18.

## Host states

| State | Meaning and exits |
| --- | --- |
| `pending` | Resolved but not launched; can start or be skipped when the run stops. |
| `starting` | Process launched; discovery/readiness pending. Becomes `ready`, `failed`, or `stopping`. |
| `ready` | Can receive an authorized operation while the run permits admission. Becomes `busy`, `stopping`, or `failed`. |
| `busy` | An operation is in flight. Becomes `ready` after completion, or `stopping`/`failed`. |
| `stopping` | Accepts no new work; cancellation and process cleanup are in progress. Becomes `stopped` or `cleanup_failed`. |
| `stopped` | Owned process exit verified; transient credentials and connections released. |
| `failed` | Unexpected process/handshake failure; blocks further invocation and starts cleanup. |
| `cleanup_failed` | Exit could not be verified; show the unresolved owned-process handle and forbid reuse. |

These are host states, separate from the run's terminal outcome and financial settlement. A successful result must not hide failed process cleanup.

## Invocation and reuse

The finite-sequence scheduler admits one graph-node activation at a time. While it waits, the platform must service that activation's permitted nested calls and usage reporting. Never hold the scheduling/admission transaction while awaiting a component or provider.

For this first profile, a host handles one operation at a time. A nested request targeting an already busy ancestor instance fails before dispatch; it is not queued behind an operation waiting for that same request. Later concurrency profiles may permit additional behavior explicitly. A descriptor's `independent` capability allows safe independent invocations; it does not require this initial scheduler to run them simultaneously.

Every invocation receives fresh client context. Reusing a process does not reuse its previous authority or implicitly supply history. A component cannot return a successful result while managed child calls remain active: the platform treats that as a lifecycle violation, stops the unfinished children and fails the parent operation. Financial settlement may still remain pending after all execution has ended.

For the proposed stateless LLMCall profile, readiness loads and validates the class/configuration and publishes its effective schemas. Each subsequent invocation constructs a fresh configured OpenAI client and a fresh implementation object, calls `generate` once, then closes/discards both in a bounded `finally` path. The host process and configured component ID remain the same. A reused object with a mutated API key is not equivalent. Constructors must remain free of business I/O; resource access stays inside the admitted operation.

This object-lifetime policy belongs to LLMCall and its compatible descendants. It does not require every future stateful component or memory resource to recreate its implementation object. Such components must declare how per-call authority is supplied independently of retained state. Immutable code/schema caches may survive within the host; prompts, mutable inputs and invocation credentials may not be reused implicitly.

Configured business-call count and nesting-depth bounds supplement time and cost limits, including for zero-cost operations and controller calls. Discovery, schema listing and transport continuations are protocol traffic with separate message/rate limits; they do not create extra activations or business attempts. Host/bootstrap traffic is also bounded. Exact numeric limits remain Q18. Reject unsupported concurrency/state profiles before starting the run; do not silently serialize or discard requested semantics.

## Stop and cleanup

1. Persist the stop/completion decision and close admission atomically, including new nested calls. Revoke invocation authority for further work.
2. Request cancellation of in-flight managed calls using their supported transport mechanism. Preserve identities and outstanding reservations.
3. Allow a configured bounded cancellation/cleanup period. Then terminate only processes owned by this run, using recorded handles; never kill unrelated processes by name.
4. Verify owned process exit. Record forced termination or unresolved cleanup separately. Clear transient context without deleting resource data, evidence or unresolved spending records.

The run outcome follows the [execution transition policy](execution.md#transition-and-race-policy). Cleanup and late cost reconciliation continue independently; they cannot schedule more graph work. A browser disconnect does not trigger this sequence. Backend recovery invalidates old invocation authority, marks unfinished execution interrupted and reconciles owned processes without replaying operations.

Remote provider work may continue after local cancellation or forced process exit. Cleanup cannot prove it stopped or that its charge is zero. The accounting contract retains that uncertainty until reconciliation.

## Resource extension boundary

The initial examples use run-owned hosts and stateless components. Later persistent/shared resources must declare who owns their service and data, who may bind them, and what reset means. Ending a run may close its adapter connection without stopping a shared external service. Binding memory does not inject context automatically; private memory can persist, and shared memory can be temporary.

Acceptance cases must cover two runs without accidental state reuse, a stateless agent accessing stateful memory, and two explicit bindings to the same resource. Current schemas do not yet define all persistent-resource modes; these remain Q05/Q22.

## Verification cases

Review and later implement checks for startup failure after another host is ready; discovery mismatch; nested-call progress while the parent waits; a busy-ancestor call; invocation-authority reuse; fresh LLMCall object/client construction in a reused host; child calls remaining after parent return; completion racing with stop; forced teardown; backend loss; and persistent data surviving host exit. QA03, QA04, QA08, QA11, QA14 and QA22–QA24 cover these cases. Documentation review is not execution evidence.
