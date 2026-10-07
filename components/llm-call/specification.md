# LLM Call component: specification

Package `slow-thinker-llm-call`, import `slow_thinker_llm_call`, declaration
`component.json` shipped as package data, equal to the contract
[example](../../docs/contracts/examples/llm-call.component.json). Entry point:
`python -m slow_thinker_llm_call <bootstrap>`. Placement: `node`. It imports the
[host SDK](../host/specification.md) and `openai` only.

## Public interface

```text
@dataclass(frozen=True)
class LLMCallConfig:
    prompt: str
    llm: str                          # catalog entry id from config.model.llm
    parameters: JsonObject            # config.model.parameters, {} when absent
    input_format: JsonObject | None
    output_schema: JsonObject | None  # set exactly for JSON output

@dataclass(frozen=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str

def parse_config(config: JsonObject) -> LLMCallConfig      # ValueError when not runnable

class LLMCall:                                               # the NodeHandler
    def __init__(self, config: LLMCallConfig) -> None
    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]
    def build_messages(self, message: JsonValue) -> list[Message]        # overridable
    def parse_response(self, reply: str) -> JsonValue                     # overridable
    def validate_result(self, value: JsonValue, reply: str) -> None       # overridable

def main(arguments: Sequence[str], serve: Serve = run_host) -> None
```

## Behaviour

- Startup: the bootstrap must name `llm-call@1.0.0` at position `node`, and
  `parse_config` requires the configuration to validate against the declaration, an
  LLM to be selected (`model` not `null`, with a non-empty `llm`) and both formats to
  be valid local JSON Schemas. Otherwise the host prints
  `LLM Call startup failed: <reason>` to standard error and exits with status 1.
- `activate(message)`:
  1. When `input_format` is a schema, validate the message against it; a mismatch fails
     with `input_format_mismatch` before any model call.
  2. Build messages: `system` = `prompt`; `user` = the message itself when it is a
     string, otherwise its canonical JSON text.
  3. Call `context.llm_client().chat.completions.create` once with
     `model = config.model.llm`, the messages, every key of `config.model.parameters`,
     and, for JSON output, `response_format = {"type": "json_schema", "json_schema":
{"name": "output", "schema": <schema>, "strict": false}}`.
  4. Text output emits the reply content as a string on `out`. JSON output parses the
     content and validates it against the schema; failures are `invalid_json` or
     `schema_mismatch`, with the first 200 characters of the reply in the message.
  5. A platform error from the endpoint fails with `model_call_failed`, keeping the
     platform's code and message: `The model call failed with <code>: <message>`, or
     the HTTP status when the body has none. A connection failure or a reply without
     text content is also `model_call_failed`; the client's own timeout, which is the
     call's remaining budget, is `timeout`.
- Reports, kind `step`, content text: `messages built: <n> messages`,
  `model replied: <length> characters`, then `reply validated` (JSON),
  `reply returned as text` (text) or `reply failed validation: <code>`.
- No retries and no repair calls ([ADR 0010](../../docs/adr/0010-llm-output-validation.md)).
- `build_messages`, `parse_response` and `validate_result` are the extension points
  for future component inheritance; a `HandlerError` they raise fails the activation
  and is reported like a validation failure.

## Acceptance

Tests with a fake OpenAI-compatible endpoint cover message building for text and JSON
input, input-format mismatch, both output formats, every failure code, reports, the
entry point's startup failures, one end-to-end run of the module as a process over
stdio, and the declaration's equality with the contract example. Line and branch
coverage at least 90%.
