# Recording

| Contract control | Value                                                                 |
| ---------------- | --------------------------------------------------------------------- |
| Contract ID      | CORE-RECORDING-1                                                      |
| Decisions        | [ADR 0021](../adr/0021-supervision-and-recording.md)                  |
| Journeys         | V11, the step 1.2 activity view                                       |

Every run has an append-only event log. The platform writes it as it mediates the
run; nothing is reconstructed afterwards. Activity views, results and totals are
read from it.

## Envelope

| Field           | Rule                                                                       |
| --------------- | -------------------------------------------------------------------------- |
| `run_id`        | Run identifier                                                             |
| `seq`           | 1, 2, 3… without gaps within the run                                       |
| `at`            | UTC timestamp, RFC 3339 with milliseconds                                  |
| `elapsed_ms`    | Milliseconds since the run was admitted                                    |
| `kind`          | One of the kinds below                                                     |
| `evidence`      | `observed` for everything the platform saw; `reported` for component reports |
| `node_id`       | Node concerned, or `null`                                                  |
| `activation_id` | Activation concerned, or `null`                                            |
| `data`          | Kind-specific object                                                       |

## Kinds

| Kind                   | `data`                                                                                                   |
| ---------------------- | -------------------------------------------------------------------------------------------------------- |
| `run.started`          | `graph_id`, `graph_version` (`null` for a change never activated), `graph_change`, `input`, `limits`, `budgets` with `run_usd`, `day_usd`, `month_usd` |
| `host.ready`           | `position`, `component`, `startup_ms`                                                                     |
| `host.failed`          | `position`, `component`, `error` with `code`, `message`                                                   |
| `run.running`          | Empty; the run's time limit starts                                                                       |
| `message.sent`         | `message_id`, `from` and `to` with `node_id`, `port`; `payload`                                          |
| `message.discarded`    | `from`, `reason` `no_connection`, `payload`                                                              |
| `message.dropped`      | `message_id`, `to`, `reason` `run_ending`                                                                |
| `activation.started`   | `message_id` or `null` for the Trigger, `number` (the node's 1-based activation count)                   |
| `activation.completed` | `emitted`: list of `{"port", "message_ids"}`, `duration_ms`                                               |
| `activation.failed`    | `error` with `code`, `message`; `duration_ms`                                                             |
| `activation.cancelled` | `reason`                                                                                                  |
| `component.called`     | `position` (`node`, `output` or `memory`), `component`, `operation` (`activate`, `select_output`, `recall` or `remember`), `arguments`, `result` or `error`, `duration_ms` |
| `llm.called`           | `call_id`, `llm`, `provider_model`, `request`, `response` or `error`, `usage` (`input`, `cached_input`, `cache_write`, `output` tokens), `reserved_usd`, `cost_usd`, `estimated`, `rates`, `status`, `duration_ms` |
| `report`               | `kind`, `content`; evidence `reported`                                                                    |
| `run.result`           | `name`, `message_id`, `payload`                                                                           |
| `run.finished`         | `status`, `reason`, `detail`, `totals` with `duration_ms`, `activations`, `messages`, `llm_calls`, `input_tokens`, `output_tokens`, `cost_usd`; `dropped` |

`node_id` and `activation_id` are set on every event that concerns one. Amounts are
decimal strings.

In `llm.called`, `status` is the HTTP status answered to the component and `error` is
the `error` object of that answer. `request` is the request as dispatched (with
parameter defaults), or the received body when the call was refused before dispatch.
`llm`, `provider_model`, `usage` and `rates` are `null` when the call was refused
before they applied or the provider reported no usable usage.

## Bounds and redaction

A serialized payload, argument, result, request or response larger than 256 KiB is
replaced by `{"truncated": true, "bytes": <size>, "preview": <first 4 KiB as text>}`.
Grants, provider credentials and authorization headers are never recorded.

## Retention

Events are kept until the operator deletes the run; step 1 provides no deletion.
