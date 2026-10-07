# Component host SDK: specification

Python implementation of the host side of the
[component protocol](../../docs/contracts/component-protocol.md). Package
`slow-thinker-host`, import `slow_thinker_host`. It may import the MCP SDK,
`jsonschema`, `httpx2` and `openai`, never the backend.

## Public interface

```text
type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]
type Position = Literal["node", "output"]

@dataclass(frozen=True)
class Emission:
    port: str
    payload: JsonValue

class HandlerError(Exception):
    def __init__(self, code: str, message: str) -> None    # code: ^[a-z][a-z0-9_]{0,63}$
    code: str
    message: str                                           # non-empty English

class Context(Protocol):                                   # valid while the handler runs
    @property
    def activation_id(self) -> str
    def remaining_seconds(self) -> float
    async def report(self, kind: str, content: JsonValue) -> None
    def llm_client(self) -> AsyncOpenAI

@dataclass(frozen=True)
class Bootstrap:
    component: str
    node_id: str
    node_name: str
    position: Position
    config: dict[str, JsonValue]
    llm_base_url: str
    mcp_url: str
    max_concurrent_invocations: int

class NodeHandler(Protocol):
    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]
class OutputHandler(Protocol):
    async def select_output(self, received: JsonValue, node_input: JsonValue,
                            context: Context) -> Emission
class MemoryHandler(Protocol):
    async def recall(self, message: JsonValue, context: Context) -> JsonValue
    async def remember(self, received: JsonValue, replied: JsonValue, context: Context) -> None

def read_bootstrap(path: Path) -> Bootstrap
def read_declaration(package: str) -> JsonObject           # the package's component.json
def check_bootstrap(bootstrap: Bootstrap, declaration: JsonObject) -> None
def create_server(bootstrap: Bootstrap, *, node: NodeHandler | None = None,
                  output: OutputHandler | None = None, memory: MemoryHandler | None = None,
                  stateful: bool = False) -> Server[object]
def run_host(bootstrap: Bootstrap, *, node: NodeHandler | None = None,
             output: OutputHandler | None = None, memory: MemoryHandler | None = None,
             stateful: bool = False) -> None
def position_tools(position: Position) -> tuple[tuple[str, JsonObject, JsonObject], ...]
def tool_schemas(position: Position) -> tuple[str, JsonObject, JsonObject]   # the first tool

PROTOCOL_VERSION = "2026-07-28"; BOOTSTRAP_FORMAT = "slow-thinker.bootstrap/1"
GRANT_META = "slow-thinker/grant"; BUDGET_META = "slow-thinker/budget-ms"
ACTIVATION_META = "slow-thinker/activation-id"; REPORT_TOOL = "platform.report"

def decode_json(text: str) -> JsonValue; def encode_json(value: JsonValue) -> str
def json_value(value: object) -> JsonValue; def json_object(value: object) -> JsonObject
def check_schema(schema: JsonObject) -> None
def validate_value(value: JsonValue, schema: JsonObject) -> None
```

`create_server` builds the same MCP server that `run_host` serves, for in-process
tests and fixture hosts. All validation failures raise `ValueError`.

## Tools

A host exposes exactly the tools of its position, `position_tools(position)`: one,
or two for `memory`. Every schema object is
`{"type": "object", "properties": …, "required": [all properties],
"additionalProperties": false}`; `{}` accepts any JSON value.

| Position | Tool            | Properties of the input          | Properties of the output                   |
| -------- | --------------- | -------------------------------- | ------------------------------------------ |
| `node`   | `activate`      | `message: {}`                    | `emissions: {"type": "array", "items": E}` |
| `output` | `select_output` | `received: {}`, `node_input: {}` | those of `E`                               |
| `memory` | `recall`        | `message: {}`                    | `message: {}`                              |
| `memory` | `remember`      | `received: {}`, `replied: {}`    | none                                       |

`E` is the emission object with properties `port: {"type": "string"}` and `payload: {}`.

## Behaviour

- `read_bootstrap` accepts exactly the fields of `slow-thinker.bootstrap/1`; the
  component is `type@major.minor.patch`; both platform URLs are `http` or `https`
  with a host and without credentials, query or fragment; the concurrency limit is a
  positive integer. Unknown fields are rejected.
- `check_bootstrap` requires the bootstrap's component to equal the declaration's
  `type@version`, its position to be a declared placement and its configuration to
  validate against the declared `config_schema`.
- `run_host` serves MCP over standard input and output and returns when standard
  input closes; running calls are then cancelled. Requests of any protocol other than
  `2026-07-28` are refused with a JSON-RPC error. The handler for the position must
  be given; the other one is ignored.
- Each call reads `_meta`: a non-empty grant, a finite budget of zero or more
  milliseconds and a non-empty activation id. The budget, measured from receipt, is
  applied with `asyncio.timeout` around both the wait for a free slot and the handler.
- A stateless host runs up to `max_concurrent_invocations` calls at once and a
  stateful host one; further calls wait for a slot and are never rejected.
- Failures are tool errors whose text is `{"code", "message"}`, without structured
  content:

  | Code                | Cause                                                                                                            |
  | ------------------- | ---------------------------------------------------------------------------------------------------------------- |
  | `unknown_tool`      | The call names a tool other than the position's                                                                  |
  | `invalid_request`   | Missing or invalid `_meta` entries                                                                               |
  | `invalid_arguments` | Arguments that do not match the tool's input schema                                                              |
  | `invalid_result`    | A result that is not emissions of JSON values matching the output schema                                         |
  | `timeout`           | The budget expired; the handler is cancelled                                                                     |
  | _handler's code_    | `HandlerError` raised by the handler                                                                             |
  | `component_error`   | Any other exception, with its type and up to 300 characters of its message; the traceback goes to standard error |

- `Context.report` sends one `platform.report` request, `{"kind", "content"}`, over
  MCP HTTP to `mcp_url` with the grant as bearer token. Any failure, including an
  unknown kind or non-JSON content, which are not sent, is logged to standard error
  and never retried or raised, so reports never fail the handler.
- `Context.llm_client` returns an `AsyncOpenAI` client with `base_url = llm_base_url`,
  `api_key` = grant, `max_retries = 0`, timeout = the remaining budget, no proxy from
  the environment and no redirects. The host closes it when the call ends.
- `validate_value` reports the most relevant violation as `<JSON Pointer>: <reason>`;
  references must be local and `pattern` follows ECMA-262 (`$` matches only at the end).
- The SDK holds no credentials and reads no environment variables. Standard output
  carries only MCP.

## Acceptance

Tests cover the three positions, exact tool exposure and schemas, bootstrap and declaration
errors, metadata, argument and result errors, budget timeout including the wait for a
slot, concurrency limits for stateless and stateful hosts, error mapping, reports
against a real MCP endpoint, the LLM client against a fake Chat Completions endpoint,
and stdin closure. Line and branch coverage at least 90%.
