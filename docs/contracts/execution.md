# Execution semantics

| Contract control | Value                                                                  |
| ---------------- | ---------------------------------------------------------------------- |
| Contract ID      | CORE-EXECUTION-1                                                       |
| Decisions        | [ADR 0017](../adr/0017-message-driven-execution.md), [ADR 0018](../adr/0018-derived-authorization.md), [ADR 0022](../adr/0022-budgets-and-request-reservations.md), [ADR 0025](../adr/0025-runs-of-changes-and-run-mode.md), [ADR 0026](../adr/0026-memory-position.md) |
| Journeys         | V02, V03, V08, V09, J1–J3                                              |

A run executes one saved graph document, an activated version or a change of the
working copy, with one input message. The platform
mediates every step and records it as defined in the [recording contract](recording.md).

## Run lifecycle

| Status      | Meaning                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------- |
| `starting`  | Admitted; component hosts are being launched                                            |
| `running`   | The trigger has fired; deliveries and activations are in progress                       |
| `completed` | No delivery is pending and no activation is running                                     |
| `stopped`   | A limit was reached: `activation_limit`, `time_limit`, `budget_run`, `budget_day` or `budget_month` |
| `failed`    | `startup_failed`, `activation_failed`, `interrupted` (backend restart) or `internal_error` |
| `cancelled` | The operator stopped the run                                                            |

Terminal statuses are `completed`, `stopped`, `failed` and `cancelled`. Each
terminal status records a reason code and an English detail naming the node,
limit or error, for example `Reviewer activation 2 failed: the script returned
the undeclared output "maybe".`

## Admission and startup

1. The operator starts a run with a graph identifier, a version and an input
   message. The input defaults to the Trigger's configured message.
2. The platform validates the version against the current catalog. A version that
   is no longer valid, for example because an LLM entry was removed, is rejected
   with its diagnostics.
3. The platform launches one component host for each node and each embedded
   component that comes from a package, concurrently, and checks each host's
   readiness as defined in the [component protocol](component-protocol.md).
   Trigger and Output run inside the platform. Any launch or readiness failure
   fails the run with `startup_failed`.
4. The run's deadline starts when it becomes `running`.

## Messages and activations

- **Trigger.** The run's first activation is the Trigger's. It emits the input
  message on `out`.
- **Emission and delivery.** When a node emits a payload on a port, the platform
  creates one delivery per connection leaving that port, in document order, and
  records each as a message. An emission on a port without connections is
  recorded as discarded.
- **Scheduling.** Deliveries wait in a first-in, first-out queue. A delivery
  starts an activation of its target node when the number of running activations
  is below `max_running_nodes`. Starting an activation when `max_activations`
  activations have already started stops the run with `activation_limit`.
- **Concurrency.** A stateless node may have several activations running. A
  delivery to a stateful node that is still running an activation fails that
  activation with `node_busy`.
- **Embedded memory.** When the node has one, the platform first calls its `recall`
  operation with the delivered message, and the host receives what it returns. After
  the host's `activate`, the platform calls `remember` with the delivered message and
  each emission's payload, before any embedded output component. A memory is
  stateful, so the node is too.
- **Package node activation.** The platform calls the host's `activate` operation
  with the delivered message, or what the memory recalled. The result lists emissions; each must name one of
  the host component's declared outputs.
- **Embedded output component.** When the node has one, each emission of the host
  is passed to it: the platform calls its `select_output` operation with the
  emission's payload as `received` and the activation's message as `node_input`.
  The returned port must be one of the embedded component's configured outputs,
  and the returned payload is emitted on that port. The host's own port is not
  visible outside the node.
- **Output node.** Its activation records the received payload as a run result,
  named after the node, and emits nothing.
- **Payloads.** Messages are JSON values: text is a JSON string, structured data
  a JSON object or array. A payload is limited to 256 KiB when serialized.

## Limits and termination

- The run completes when the queue is empty and no activation is running. Its
  results are the payloads received by Output nodes, in order of arrival.
- When a limit is reached, when an activation fails, or when the operator stops
  the run, no further activation starts. Running activations are cancelled and
  recorded as cancelled; pending deliveries are recorded as dropped. The run ends
  with the corresponding status. The first cause recorded wins.
- An activation fails when its component returns an error, when its result
  violates the protocol, when an emission names an undeclared port, when a model
  call it depends on fails, or when its time budget expires. Under the proposed
  policy of [ADR 0017](../adr/0017-message-driven-execution.md), a failed
  activation fails the run with `activation_failed`.
- Every activation receives a time budget equal to the smaller of the run's
  remaining time and the platform's maximum activation time (default 300 s).
- A budget denial for a model call stops the run with the scope that was
  exhausted; see the [accounting contract](accounting.md).

## Several runs

Several runs may be active at the same time, up to a platform limit (default 4).
Each run has its own component hosts, queue and limits. Daily and monthly budgets
are shared by all runs.

## Restart

When the backend starts, runs that are not terminal are marked `failed` with
`interrupted`, their open reservations are settled at the reserved amount and
marked estimated, and their component processes are terminated. Runs are never
resumed or replayed automatically.
