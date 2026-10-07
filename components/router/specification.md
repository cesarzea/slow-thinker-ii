# Router component: specification

Package `slow-thinker-router`, import `slow_thinker_router`, declaration
`component.json` shipped as package data, equal to the contract
[example](../../docs/contracts/examples/router.component.json). Entry point:
`python -m slow_thinker_router <bootstrap>`. Placements: `node` and `output`. It
imports the [host SDK](../host/specification.md) only.

## Public interface

```text
@dataclass(frozen=True)
class RouterConfig:
    outputs: tuple[str, ...]
    script: str

type Route = Callable[[JsonValue, JsonValue], object]

class ScriptError(ValueError): ...                         # English, names the line

def parse_config(config: JsonObject) -> RouterConfig       # ValueError when invalid
def load_route(script: str) -> Route                       # ScriptError when unusable

class Router:                                              # NodeHandler and OutputHandler
    def __init__(self, config: RouterConfig, route: Route) -> None
    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]
    async def select_output(self, received: JsonValue, node_input: JsonValue,
                            context: Context) -> Emission

def main(arguments: Sequence[str], serve: Serve = run_host) -> None
```

## Behaviour

- At startup the host checks the bootstrap against the declaration, then compiles
  `config.script` as `<script>` and runs it in a fresh namespace with the normal
  built-ins, and looks up a callable `route` that is synchronous and accepts two
  positional parameters. A syntax error, an exception while the script loads, a
  missing or unsuitable `route` stops the host before readiness with exit status 1,
  printing `Router startup failed: <reason>` to standard error, for example
  `The script has a syntax error at line 2: invalid syntax`.
- `select_output(received, node_input)` calls `route(received, node_input)`.
- `activate(message)` calls `route(message, message)` and emits one emission.
- The script receives copies of the values. The result must be a two-item tuple or
  list `(output, payload)`: `output` one of `config.outputs`, `payload` a JSON value
  (tuples, sets and non-finite numbers are not). Otherwise the call fails with
  `undeclared_output` (`The script returned the undeclared output "maybe".`) or
  `invalid_result`.
- An `Exception` or `SystemExit` raised by the script fails the call with
  `script_error`, naming the exception type, message and script line, for example
  `The script raised KeyError: 'score' at line 2.`
- Reports (kind `step`): `route returned <output>`.
- The script runs synchronously in a daemon thread so that the host stays responsive
  and a script that never returns cannot keep the process alive once standard input
  closes; when the call's budget expires, the late result is discarded. The script is
  trusted user code in S06.

## Acceptance

Tests cover both operations, every failure code, startup failures, non-JSON payloads,
reports, the entry point, end-to-end runs of the module as a process over stdio at
both positions with exit on stdin closure, and the declaration's equality with the
contract example. Line and branch coverage at least 90%.
