# Component protocol

| Contract control | Value                                                                              |
| ---------------- | ---------------------------------------------------------------------------------- |
| Contract ID      | CORE-PROTOCOL-1                                                                    |
| Decisions        | [ADR 0004](../adr/0004-component-packaging.md), [ADR 0007](../adr/0007-mcp-profile.md), [ADR 0023](../adr/0023-container-ready-component-boundary.md), [ADR 0026](../adr/0026-memory-position.md) |
| Transport        | MCP protocol revision `2026-07-28`, Python SDK `mcp==2.2.0`                        |

A component from a package runs as its own process, called a host. The platform
talks to the host over MCP on the host's standard input and output. The host talks
back to the platform only through the platform's HTTP endpoints, authenticated by
the invocation grant it received.

## Launch and bootstrap

The platform launches the host's installed entry point with one argument: the path
of a bootstrap document, read once at startup. The host must not depend on any
other file written by the platform.

```json
{
  "format": "slow-thinker.bootstrap/1",
  "component": "llm-call@1.0.0",
  "node": {"id": "proposer", "name": "Proposer"},
  "position": "node",
  "config": {"prompt": "…", "model": {"llm": "openai/gpt-6-luna", "parameters": {"max_completion_tokens": 300}}, "input_format": null, "output_format": {"type": "text"}},
  "platform": {"llm_base_url": "http://127.0.0.1:8000/v1", "mcp_url": "http://127.0.0.1:8000/mcp"},
  "limits": {"max_concurrent_invocations": 4}
}
```

`position` is `node` for a graph node, `output` for an embedded output component and
`memory` for an embedded memory.
The environment contains no provider credentials.

## Readiness

After MCP initialization the platform lists the host's tools. A host exposes exactly
`activate` when its position is `node`, exactly `select_output` when its position is
`output`, and exactly `recall` and `remember` when its position is `memory`, with the
schemas below. Any other set of tools, an initialization error
or no readiness within the platform's startup timeout (default 20 s) fails the run
with `startup_failed`.

## Operations

| Tool            | Arguments                                   | Result                                                   |
| --------------- | ------------------------------------------- | -------------------------------------------------------- |
| `activate`      | `{"message": <JSON value>}`                 | `{"emissions": [{"port": string, "payload": <JSON value>}]}` |
| `select_output` | `{"received": <JSON value>, "node_input": <JSON value>}` | `{"port": string, "payload": <JSON value>}`  |
| `recall`        | `{"message": <JSON value>}`                 | `{"message": <JSON value>}`: what the node receives instead |
| `remember`      | `{"received": <JSON value>, "replied": <JSON value>}` | `{}`                                    |

For a node with an embedded memory, the platform calls `recall` with the message the
node receives and passes the node what `recall` returns. After the node's `activate`
it calls `remember` once per emission, with the message the node received (before
`recall`) and the emission's payload, before any embedded output component chooses a
port. The memory decides what it keeps, for how long and how it adds it to a message;
the platform knows only these two operations.

Every call carries these `_meta` entries:

| Key                          | Meaning                                                              |
| ---------------------------- | -------------------------------------------------------------------- |
| `slow-thinker/grant`         | Opaque invocation grant; the bearer credential for calls back to the platform |
| `slow-thinker/budget-ms`     | Remaining time for this call in milliseconds, relative to its receipt |
| `slow-thinker/activation-id` | Identifier of the activation, for the host's own logging             |

Exact tool schemas, compared at readiness:

```json
{"activate": {
  "input": {"type": "object", "properties": {"message": {}}, "required": ["message"], "additionalProperties": false},
  "output": {"type": "object", "properties": {"emissions": {"type": "array", "items":
    {"type": "object", "properties": {"port": {"type": "string"}, "payload": {}},
     "required": ["port", "payload"], "additionalProperties": false}}},
    "required": ["emissions"], "additionalProperties": false}},
 "select_output": {
  "input": {"type": "object", "properties": {"received": {}, "node_input": {}},
    "required": ["received", "node_input"], "additionalProperties": false},
  "output": {"type": "object", "properties": {"port": {"type": "string"}, "payload": {}},
    "required": ["port", "payload"], "additionalProperties": false}},
 "recall": {
  "input": {"type": "object", "properties": {"message": {}}, "required": ["message"], "additionalProperties": false},
  "output": {"type": "object", "properties": {"message": {}}, "required": ["message"], "additionalProperties": false}},
 "remember": {
  "input": {"type": "object", "properties": {"received": {}, "replied": {}},
    "required": ["received", "replied"], "additionalProperties": false},
  "output": {"type": "object", "properties": {}, "required": [], "additionalProperties": false}}}
```

A failed operation returns an MCP tool error whose text is
`{"code": string, "message": string}`. `code` matches `^[a-z][a-z0-9_]{0,63}$` and
`message` is English. Results and errors must arrive within the time budget. Codes
produced by the host SDK itself:

| Code                | Cause                                                                   |
| ------------------- | ----------------------------------------------------------------------- |
| `unknown_tool`      | The call names a tool other than the position's ones                    |
| `invalid_request`   | Missing or invalid `_meta` entries                                      |
| `invalid_arguments` | Arguments that do not match the tool's input schema                     |
| `invalid_result`    | A handler result that does not match the tool's output schema           |
| `timeout`           | The budget expired; the handler was cancelled                          |
| `component_error`   | An unexpected exception in the component                               |

Components add their own codes, for example `input_format_mismatch`, `invalid_json`,
`schema_mismatch`, `model_call_failed`, `undeclared_output` and `script_error`.

The platform adds its own codes for failures it observes on the host's side:

| Code                | Recorded in        | Cause                                                              |
| ------------------- | ------------------ | ------------------------------------------------------------------ |
| `launch_failed`     | `host.failed`      | The component is not installed, or its bootstrap or process could not be created |
| `exited`            | `host.failed`      | The host exited before it was ready                                 |
| `not_ready`         | `host.failed`      | No readiness within the startup timeout                             |
| `tools_mismatch`    | `host.failed`      | Other tools than the position's, or schemas other than these        |
| `protocol_error`    | `host.failed`      | Wrong protocol revision or capabilities, or invalid output          |
| `stopped`           | `host.failed`      | Stopped before readiness because another host failed or the run ended |
| `timeout`           | `component.called` | No answer within the call's time budget                            |
| `message_too_large` | `component.called` | Arguments or an answer above the platform's message limit (1 MiB)  |
| `invalid_result`    | `component.called` | A result or tool error outside the shapes above                    |
| `host_failed`       | `component.called` | The host stopped answering                                          |

A `host.failed` message names the component and node, for example `Router in Judge
could not start: Router startup failed: The script has a syntax error at line 1:
expected ':'`; it becomes the detail of the failed run.

A stateless host accepts up to `max_concurrent_invocations` concurrent calls. A
stateful host processes one call at a time; the platform never sends it a second
concurrent call.

## Calls back to the platform

| Purpose        | Endpoint                                          | Contract                         |
| -------------- | ------------------------------------------------- | -------------------------------- |
| Model calls    | `POST {llm_base_url}/chat/completions`, bearer grant | [LLM service](llm-service.md)    |
| Reports        | MCP over HTTP at `mcp_url`, bearer grant, tool `platform.report` | Below                |

`platform.report` takes `{"kind": "step" | "progress" | "state" | "explanation" |
"reasoning", "content": <JSON value>}`, with content up to 64 KiB. Each report is
recorded as reported evidence for the activation identified by the grant. A grant
expires when its call ends; later use is rejected with `401 invalid_grant`.

## Shutdown

When the run ends the platform closes the host's standard input, waits up to 5 s,
then terminates and finally kills the process. Hosts keep no state between runs: a
memory that keeps its exchanges in its process lasts for the run.

## Host SDK

The Python package `slow-thinker-host` implements this protocol. The backend does not
import it; both implement this contract, and a backend test compares the platform's
expected tool schemas with the SDK's `tool_schemas()` and `position_tools()`. A
component provides handlers for its operations (`NodeHandler`, `OutputHandler` or
`MemoryHandler`); the SDK reads the bootstrap, serves MCP,
enforces concurrency and time budgets, validates arguments and results, and gives
each handler a context with `report(kind, content)`, the time remaining and an
OpenAI-compatible client bound to `llm_base_url` with the grant as its key and
retries disabled.
