# Python component interface

**Status: First-cycle implementation in progress.** R02, R08, R27; Q13, Q17, Q20. The declarations below summarize the reference API; executable packages live under `components/`. See the [verification record](../verification.md) for tested behavior and remaining integration work.

## Public values

The `slow_thinker_llm_call` package exports its reference types through its public entry point. The project runtime is pinned in `.python-version`; the type-alias notation below requires Python 3.12 or later.

```python
from dataclasses import dataclass
from typing import Literal, TypedDict

type JsonValue = (
    None | bool | int | float | str
    | list[JsonValue] | dict[str, JsonValue]
)
type JsonObject = dict[str, JsonValue]

@dataclass(frozen=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str

@dataclass(frozen=True)
class ModelResponse:
    text: str

@dataclass(frozen=True)
class OutputIssue:
    path: str
    message: str

class TextOutput(TypedDict):
    format: Literal["text"]

class JsonOutput(TypedDict):
    format: Literal["json"]
    schema: JsonObject

class LLMCallConfig(TypedDict):
    instructions: str
    input_schema: JsonObject
    parameters: JsonObject
    output: TextOutput | JsonOutput

class TextSuccess(TypedDict):
    status: Literal["ok"]
    format: Literal["text"]
    value: str

class JsonSuccess(TypedDict):
    status: Literal["ok"]
    format: Literal["json"]
    value: JsonValue

class SerializedIssue(TypedDict):
    path: str
    message: str

class OutputError(TypedDict):
    code: Literal["invalid_json", "output_schema_mismatch", "output_validation_failed"]
    message: str
    raw_output: str
    issues: list[SerializedIssue]

class FailedOutput(TypedDict):
    status: Literal["error"]
    error: OutputError

type CallResult = TextSuccess | JsonSuccess | FailedOutput
```

Reject non-finite floats at the JSON boundary. Schema validation remains necessary; Python types do not validate external data. Configuration and arguments are supplied as isolated values, not shared mutable conversation state. `ModelResponse` represents a complete textual response; the provider adapter retains its full evidence and usage separately.

## Lifecycle and extension points

The reference component accepts an ordinary `AsyncOpenAI` client configured for the platform's compatible endpoint and its bound model alias. This is an integration dependency of the reference component, not a dependency of core domain contracts. Other component implementations can use the supported LangChain or MCP clients.

```python
from openai import AsyncOpenAI

class OutputValidationError(ValueError):
    def __init__(self, issues: tuple[OutputIssue, ...]) -> None:
        ...

class LLMCall:
    def __init__(
        self, config: LLMCallConfig, client: AsyncOpenAI, model: str
    ) -> None:
        ...

    async def generate(self, arguments: JsonObject) -> CallResult:
        ...

    def build_messages(self, arguments: JsonObject) -> list[Message]:
        ...

    def parse_response(self, response: ModelResponse) -> JsonValue:
        ...

    def validate_result(self, value: JsonValue, arguments: JsonObject) -> None:
        ...
```

`generate` coordinates input validation, `build_messages`, one familiar `client.chat.completions.create(...)` invocation, complete-response checks, `parse_response`, configured output-schema validation, and `validate_result`, then builds the result envelope. The [provider proposal](openai-initial-profile.md#response-preservation-and-functional-interpretation) specifies checks before extracting `ModelResponse.text`; refusal or truncation cannot disappear during text extraction. The default result-validation hook does nothing beyond the common schema checks. Those common checks sit outside replaceable hooks and are also verified at the platform boundary.

The host creates the client with scoped routing authority and explicit retry settings. User parameters cannot replace its endpoint or credentials. Run/activation correlation is supplied through connection setup or adapter context, without extra `generate` arguments; its exact wire mechanism remains Q06.

The stateless hosting proposal constructs a new client and `LLMCall(config, client, model)` object for each invocation, using isolated configuration/input values. This preserves the constructor API while allowing invocation-specific credentials without mutating a shared client. Reuse the host process and immutable loaded code, not the implementation object or conversation state. The host closes the client in a bounded `finally` path after success, failure or cancellation. Readiness validates the class and effective schemas without creating a business invocation.

Compatible subclasses inherit this object-lifetime contract. A subclass requiring retained mutable state must declare a different supported lifecycle instead of depending on accidental object reuse. The configured graph instance and its public identity remain stable across these temporary Python objects.

Authors override the documented hooks and may use `super()`. A different execution algorithm can implement another component contract; redefining behavior does not silently preserve the one-call guarantee of `LLMCall`. Output-check failures raise `OutputValidationError`; the lifecycle retains the original response and returns `output_validation_failed`. The result schema defines JSON serialization of issues.

Keep orchestration telemetry outside the functional hooks. Optional internal reporting can be attached by the host; it must be removable for the future standalone export. A subclass is code loaded into the derived component's process, not another running participant. See the [GroundedReview example](examples/grounded-review.md) and [registration contract](component-installation.md).

## Installed contract discovery

Every registered implementation class provides a synchronous static or class method `describe(config) -> tuple[Operation, ...]`, using the public `slow_thinker_host.Operation` value. It validates configuration and returns nonempty, uniquely named operations with object input/output schemas. It must work without constructing a provider client, obtaining credentials or invoking business operations. `LLMCall` supplies this method and compatible subclasses inherit it. A subclass that overrides the description must also provide a host that publishes and enforces those same specialized schemas; the standard `LLMCallHost` enforces the reference contract.

The backend calls this method in the selected installation's isolated interpreter, with a bounded timeout and an explicit environment without provider credentials or invocation grants. It validates the result and verifies installation integrity before and after successful discovery. Retained evidence includes the exact installation record, effective configuration and operation schemas. Readiness must reproduce those schemas before any business invocation. This is isolation of imports and credentials, not an OS sandbox for untrusted Python code.

Graph configuration is validated against the trusted type descriptor. A trusted host profile may expand it into effective implementation configuration, such as the real model and token limits behind a graph's model alias. Graph data cannot supply that expansion directly. The initial runner requires logical operation names to equal their MCP tool names; unsupported aliases are rejected.
