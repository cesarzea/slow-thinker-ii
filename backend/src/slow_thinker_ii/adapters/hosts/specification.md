# adapters.hosts: specification

Launches and calls component hosts as local processes, implementing the application
port `HostLauncher`, whose `RunHosts` implement the engine port `Hosts`, per the
[component protocol](../../../../../docs/contracts/component-protocol.md). It imports
`application`, `engine`, `graphs`, `catalog`, `contracts`, the MCP SDK and `anyio`;
never another adapter or a component package.

## Public interface (`slow_thinker_ii.adapters.hosts`)

```text
@dataclass(frozen=True)
class HostSettings:
    workspace: Path                   # absolute; per-run directories for bootstrap documents
    llm_base_url: str                 # e.g. "http://127.0.0.1:8000/v1"
    mcp_url: str                      # e.g. "http://127.0.0.1:8000/mcp"
    startup_seconds: float = 20
    shutdown_seconds: float = 5
    max_message_bytes: int = 1_048_576   # at least 65,536
    max_concurrent_invocations: int = 4

class LaunchTarget(Protocol):         # implemented by adapters.installations
    def interpreter(self, ref: ComponentRef) -> Path
    def module(self, ref: ComponentRef) -> str

class LocalHostLauncher(HostLauncher):
    def __init__(self, targets: LaunchTarget, settings: HostSettings) -> None
    async def launch(self, run_id: str, plan: RunPlan, log: RunLog) -> RunHosts

def protocol_tool(position: Position) -> tuple[str, JsonObject, JsonObject]          # the first tool
def protocol_tools(position: Position) -> tuple[tuple[str, JsonObject, JsonObject], ...]  # every tool
```

`protocol_tool` gives the tool a host at `position` must expose (name, input and output
schema), as the protocol contract lists them; a test compares it with the host SDK's
`tool_schemas()`. Invalid settings raise `ValueError`.

## Launch

- First `launch` looks up `interpreter(ref)` and `module(ref)` once per distinct
  component of the plan, in worker threads (`asyncio.to_thread`) and all at once,
  because a launch target may verify an installation for a second or more. Every host
  of that component shares the result. When a lookup fails, no host is started: each
  host of that component records `launch_failed` (`it is not installed: …`), every
  other host records `stopped`, and `StartupFailed` names the first such host.
- Then `launch` starts one host per package node (`node`) and per embedded component
  (`output`, `memory`), all at once. Each gets `<workspace>/<run id>/<node id>.<position>.json`,
  a `slow-thinker.bootstrap/1` document with the node, configuration, platform URLs and
  `max_concurrent_invocations`, and runs `<interpreter> -B -I -m <module> <bootstrap>`
  in `<workspace>/<run id>/`, in its own session, with only `PATH` (the interpreter's
  directory) in its environment.
- Readiness, within `startup_seconds` of the spawn: `server/discover` must list protocol
  `2026-07-28` and only the `tools` capability, and `tools/list` must be exactly the
  position's tools (two for `memory`) with the protocol's schemas, on one page.
- Every host gets exactly one record, with `node_id`: `host.ready` `{position,
component, startup_ms}`, or `host.failed` `{position, component, error: {code,
message}}` where the message is the run's detail `<Component label> in <Node name>
could not start: <cause>`:

  | Code             | Cause                                                                                                                                            |
  | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
  | `launch_failed`  | `it is not installed: …` (the launch target failed), `its bootstrap document could not be written: …`, `its interpreter could not be started: …` |
  | `exited`         | The host closed its output first: its last line of standard error, or `it exited with status <n> before it was ready.`                           |
  | `not_ready`      | `it was not ready within <n> seconds.`                                                                                                           |
  | `tools_mismatch` | `it exposes <tools> instead of only the <tool> tool.` or `its <tool> tool does not have the protocol's schemas.`                                 |
  | `protocol_error` | Wrong protocol version or capabilities, an error answer to the handshake, invalid or oversized output                                            |
  | `stopped`        | `<Component> in <Node> was stopped before it was ready.` (another host failed, a component is not installed, or the launch was cancelled)        |

- On the first failure every other host is stopped, the run directory is removed and
  `StartupFailed` is raised with that host's detail, for example `Router in Judge could
not start: Router startup failed: The script has a syntax error at line 1: expected
':'`. Unexpected exceptions propagate unchanged. A cancelled launch stops its hosts.

## Calls

- `activate`, `select_output`, `recall` and `remember` route by node id and position (a
  node's memory host is `(node, "memory")`) and send one
  `tools/call` with `_meta` `slow-thinker/grant`, `slow-thinker/budget-ms` (the
  context's `budget_ms`) and `slow-thinker/activation-id`, and waits at most `budget_ms`
  plus 0.5 s: the engine's own timers decide between `timeout` and `time_limit` first,
  and hosts built on the SDK answer `timeout` at their budget. Cancelling the caller or
  the expired wait cancels the request in the host.
- Results are checked against the protocol's output schemas and returned as engine
  values; a tool error's text `{"code", "message"}` becomes `CallFailure(code,
message)`. The adapter's own failures:

  | Code                | When                                                                                                                                        |
  | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
  | `timeout`           | `The component did not answer within <n> ms.`, after the budget plus 0.5 s                                                                  |
  | `message_too_large` | Arguments with their envelope above `max_message_bytes`, refused before sending, or a host line above it, which ends that host's connection |
  | `invalid_result`    | A result or tool error outside the protocol's shapes                                                                                        |
  | `host_failed`       | No host serves the node, or the host stopped answering (exited, broken pipe)                                                                |

- Each host runs in a task of its own that owns its process and MCP session; calls may
  come from any task, concurrently.

## Shutdown

`close` stops every host at once: close standard input, wait a third of
`shutdown_seconds`, terminate, wait, kill, wait; then it removes the run directory. It
never raises and may be called again. Standard error is drained continuously; its last
4 KiB are kept only to explain startup failures.

## Acceptance

Integration tests launch fixture hosts built on the host SDK, a raw JSON-RPC fixture
that breaks the protocol on purpose, and the real LLM Call and Router packages with a
local fake Chat Completions endpoint, a slow counting launch target (one lookup per
component, the event loop kept free), including a run of the story-triage journey by
the engine and a real-clock run that a silent host lets end at the time limit. They cover launch and isolation, concurrent startup, every readiness
failure, startup timeout, calls with emissions and errors, budget timeout and
cancellation reaching the host, oversized messages in both directions, invalid results,
broken hosts and the full shutdown escalation. Line and branch coverage at least 90%.
