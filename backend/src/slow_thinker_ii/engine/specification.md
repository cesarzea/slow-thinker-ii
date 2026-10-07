# engine: specification

Implements the scheduling part of the [execution contract](../../../../docs/contracts/execution.md)
for one run: deliveries, activations, the embedded memory and output pipeline, limits and
termination. Pure `asyncio` code behind ports; it launches no processes and does no I/O.

## Public interface (`slow_thinker_ii.engine`)

```python
Position = Literal["node", "output", "memory"]

@dataclass(frozen=True)
class Emission:
    port: str
    payload: JsonValue

@dataclass(frozen=True)
class CallFailure:
    code: str                          # ^[a-z][a-z0-9_]{0,63}$
    message: str                       # English

@dataclass(frozen=True)
class CallContext:
    run_id: str
    node_id: str
    position: Position
    activation_id: str
    grant: str                         # issued by the engine for this call only; not in repr
    budget_ms: int                     # time remaining for this call

class Hosts(Protocol):                 # implemented by adapters.hosts for package nodes
    async def activate(self, context: CallContext, message: JsonValue) -> tuple[Emission, ...] | CallFailure
    async def select_output(self, context: CallContext, received: JsonValue, node_input: JsonValue) -> Emission | CallFailure
    async def recall(self, context: CallContext, message: JsonValue) -> JsonValue | CallFailure
    async def remember(self, context: CallContext, received: JsonValue, replied: JsonValue) -> None | CallFailure

class RunLog(Protocol):                # implemented by the application; appends to the event log
    def record(self, kind: str, data: JsonObject, *, node_id: str | None = None,
               activation_id: str | None = None) -> None

class Clock(Protocol):
    def monotonic(self) -> float

class GrantIssuer(Protocol):           # satisfied by slow_thinker_ii.access.Grants
    def issue(self, caller: Caller, ttl_seconds: float) -> str   # ttl = the call's budget
    def revoke(self, token: str) -> None

StopReason = Literal["activation_limit", "time_limit", "budget_run", "budget_day",
                     "budget_month", "activation_failed", "cancelled", "internal_error"]
RunStatus = Literal["completed", "stopped", "failed", "cancelled"]

@dataclass(frozen=True)
class RunResult:
    node_id: str
    name: str
    message_id: str
    payload: JsonValue

@dataclass(frozen=True)
class RunOutcome:
    status: RunStatus
    reason: StopReason | None          # None when completed
    detail: str                        # English; empty when completed
    results: tuple[RunResult, ...]     # in order of arrival
    activations: int                   # activations started, Trigger and Output included
    messages: int                      # messages sent

class RunEngine:
    def __init__(self, run_id: str, plan: RunPlan, hosts: Hosts, log: RunLog,
                 grants: GrantIssuer, clock: Clock, *, max_activation_seconds: int = 300) -> None
    async def run(self, input_message: JsonValue) -> RunOutcome    # never raises (except its own cancellation)
    def stop(self, reason: StopReason, detail: str) -> None         # call from the event loop; first cause wins
```

## Behaviour

- `run` records `run.running`, starts the deadline (`time_limit_seconds` from the
  plan), then runs the Trigger activation with `input_message` and `message_id` null.
- Identifiers: messages `m1, m2, …` and activations `a1, a2, …` in creation order,
  unique within the run.
- Events and their data follow the [recording contract](../../../../docs/contracts/recording.md):
  `message.sent`, `message.discarded`, `message.dropped`, `activation.started`,
  `activation.completed`, `activation.failed`, `activation.cancelled`,
  `component.called` and `run.result`. The engine does not record `run.started`,
  `host.*` or `run.finished`.
- Scheduling is first-in, first-out with at most `max_running_nodes` concurrent
  activations. The `max_activations`-plus-one start request stops the run with
  `activation_limit`.
- A delivery to a stateful node that is running fails the new activation with
  `node_busy`.
- Embedded memory: before `activate`, call `hosts.recall` with its own grant for
  `(run, node, "memory", activation)` and `component.called` record (operation
  `recall`); the host receives what it returns. After `activate`, call `hosts.remember`
  once per emission with the delivered message and the emission's payload (operation
  `remember`), before any output component. A failure of either fails the activation.
  The engine keeps nothing of a memory itself.
- Package activation: issue a grant for `(run, node, "node", activation)`, call
  `hosts.activate`, revoke the grant, record `component.called`. Each emission's port
  must be one of the host component's declared outputs, otherwise `undeclared_port`.
  With an embedded output component, call `hosts.select_output` once per emission,
  in order, with its own grant and `component.called` record; the returned port must
  be one of the node's effective outputs.
- Trigger activation emits the input on `out`. Output activation records
  `run.result` with the node's name and emits nothing.
- Every call's `budget_ms` is the smaller of the run's remaining time and
  `max_activation_seconds`, minus the time already spent in the activation; a call
  that does not return in time is cancelled and fails with `timeout`.
- Termination: the first cause wins. `stop` (from the application, for budgets or
  the operator), a failed activation, a deadline or the activation limit prevents
  new starts, cancels running activations (`activation.cancelled`), records pending
  deliveries as `message.dropped`, and returns the outcome. With nothing pending and
  nothing running, the run is `completed`.
- Outcome statuses: `activation_limit`, `time_limit` and budgets → `stopped`;
  `activation_failed` and `internal_error` → `failed`; `cancelled` → `cancelled`.
  The detail names the node and cause, for example
  `Reviewer activation 2 failed: the script returned the undeclared output "maybe".`
- Unexpected exceptions inside the engine stop the run with `internal_error`; they
  never escape `run`.

## Decided details

- **Event attribution.** `message.sent` and `message.discarded` carry the sending node
  and activation; `message.dropped` carries the target node and no activation;
  `activation.*`, `component.called` and `run.result` carry their node and activation.
  `activation.completed.emitted` has one `{"port", "message_ids"}` entry per emission,
  in order, with an empty list for a discarded emission.
- **When messages exist.** An activation's emissions pass through the whole pipeline
  first; its messages are created only when it completes. An activation that fails or
  is cancelled midway sends nothing.
- **Recorded calls.** `component.called` has `arguments` and `result` exactly as the
  [component protocol](../../../../docs/contracts/component-protocol.md) operations
  (`{"message"}`, `{"emissions"}`, `{"received", "node_input"}`, `{"port", "payload"}`),
  never the grant. A call cut off by the run's end is recorded with error `cancelled`;
  a host call that raises is recorded with error `internal_error` and stops the run
  with `internal_error`.
- **Cancellation records.** Every started activation ends with exactly one of
  `activation.completed`, `activation.failed` or `activation.cancelled`. Running
  activations, including those cancelled before their first step, are recorded
  `activation.cancelled` with the stop reason (`cancelled` when the task running `run`
  is itself cancelled). An activation that finishes on its own after the run's cause is
  set is also recorded `activation.cancelled` and sends nothing.
- **`node_busy`** is decided when the delivery starts its activation: it counts as a
  started activation, records `activation.started` then `activation.failed`, and fails
  the run with `activation_failed`.
- **Time.** Every real wait is armed from a fresh `Clock.monotonic()` reading: the
  run's deadline wait, and a call's own timeout. A call gets a timeout only when the
  activation's remaining time is smaller than the run's; otherwise the deadline governs,
  so a hanging host ends the run with `time_limit`, not `timeout`. A deadline wait that
  expires stops the run with `time_limit`. A call with less than 1 ms left is not made
  and fails with `timeout` (`The activation has no time left to call its component.`),
  or stops the run with `time_limit` when the run's deadline has passed; the same
  applies to a `timeout` failure returned at or after the deadline. `budget_ms` is
  rounded up to the next millisecond when the run's deadline binds, so a host that times
  out after `budget_ms` never answers before the deadline and the engine decides
  `time_limit`; it is rounded down when the activation's own limit binds, where the
  engine's timeout for the call decides. It is never negative, and the grant lives
  `budget_ms / 1000` seconds.
- **Payload limit.** Each emission (the Trigger's input included) whose serialized
  payload exceeds 262,144 UTF-8 bytes fails its activation with `payload_too_large`.
- **Details.** `<Node name> activation <n> failed: <cause>`, where the cause is the
  failure's message with its first letter lowered when the second is lower case (so
  `JSON …` keeps its case); `The run reached its limit of <n> activations before
  <Node name> could start.`; `The run reached its time limit of <n> seconds.`;
  `The run failed unexpectedly: <Type>: <error>` for errors outside activations. The
  engine's own failure messages are `The component emitted on the undeclared output
  "<port>".`, `The output component selected the undeclared output "<port>".`,
  `The node is still running an earlier activation.`, `The component did not answer
  within <n> ms.` and `The output "<port>" carries <n> bytes; messages are limited to
  262144 bytes.`
- **Stops outside a run.** `stop` before `run` makes `run` return that outcome at once,
  with no events and no activations; `stop` after `run` returned has no effect.

## Acceptance

Tests use fake `Hosts`, `RunLog`, grants and a controllable clock, with no sleeps
longer than 50 ms. They cover J1, J2 and J3 plans compiled from the contract
examples; fan-out concurrency bounded by `max_running_nodes`; FIFO order; the
activation limit with pending deliveries; time limit with a hanging host; external
stop for budget and cancellation while activations run; `node_busy`; undeclared
ports from host and embedded component; failures from both operations; event
ordering and identifiers; grants issued and revoked per call. Branch coverage of the
package is at least 90%.
