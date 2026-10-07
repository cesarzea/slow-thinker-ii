# adapters.providers: specification

Provider transports for the [LLM service](../../../../../docs/contracts/llm-service.md),
implementing the application port `LlmProvider`.

## Public interface (`slow_thinker_ii.adapters.providers`)

```python
@dataclass(frozen=True)
class ProviderEndpoint:
    provider: Literal["openai", "deepseek"]
    base_url: str                     # exact reviewed origin or loopback for tests
    api_key: str = field(repr=False)
    timeout_seconds: float = 120
    max_response_bytes: int = 524_288

    @property
    def url(self) -> str              # <base_url>/chat/completions, the only URL contacted

class HttpProvider(LlmProvider):
    def __init__(self, endpoints: Mapping[str, ProviderEndpoint],
                 transport: httpx.AsyncBaseTransport | None = None) -> None

class SimulatedProvider(LlmProvider):
    def __init__(self, replies: Mapping[str, Sequence[str]] | None = None) -> None
```

Both providers implement `complete(model, request, timeout_s) -> ProviderReply` of the
[application](../../application/specification.md): status 200, 502 or 504, aware UTC
`started_at` and `ended_at`. `request` is the gateway's dispatched request, whose `model` is
the catalog entry id.

## Endpoints

- `ProviderEndpoint` accepts as `base_url` its provider's reviewed origin
  (`https://api.openai.com/v1` or `https://api.deepseek.com`, a trailing slash allowed), or an
  `http` loopback URL on `127.0.0.1` or `::1` with an explicit non-zero port and the path
  `/v1`, never with user information, query or fragment. The key is printable ASCII without
  spaces, the timeout finite and positive, the response limit a positive integer. Violations
  raise `ValueError` whose message repeats neither the URL nor the key; `repr` omits the key.
- `HttpProvider` endpoints are keyed by provider name, and each key must equal its endpoint's
  `provider` (`ValueError`). A call uses the endpoint of `model.settings.provider`; without
  one it is answered 502 and nothing is sent.

## Requests

`model` becomes `model.settings.model`. A request without `reasoning_effort` (the schema of a
model with a single reviewed effort has no such parameter) takes the reviewed default, the
first of `reasoning_efforts`; a model without reviewed efforts sends none.

- `openai`: every field unchanged, the effort as above, plus `store: false` and
  `service_tier: "default"`.
- `deepseek`: `max_completion_tokens` → `max_tokens`; effort `none` → `thinking:
  {"type": "disabled"}` without `reasoning_effort`; another effort → `thinking:
  {"type": "enabled"}` with that `reasoning_effort`; `temperature` unchanged. A message whose
  role is not `system`, `user` or `assistant` is answered 502 and nothing is sent.
- `deepseek` JSON output: DeepSeek supports only `json_object`
  ([JSON mode](https://api-docs.deepseek.com/guides/json_mode)). A `response_format`
  `{"type": "json_schema", "json_schema": {"name", "schema", "strict"}}` becomes
  `{"type": "json_object"}`, and the instruction `Answer with one JSON object that conforms
  to this JSON Schema: <schema>` is added, the schema as canonical JSON (sorted keys, no
  spaces; `{}` when the format names none). When the first message is `system`, the
  instruction is appended to its content after a blank line (`\n\n`); otherwise it is
  inserted as a new first `system` message. `{"type": "text"}`, `{"type": "json_object"}`
  and a request without `response_format` keep their format and messages.

Mappings build new values: the received request, which the gateway records, is unchanged.

## Transport and replies

One POST per call with bearer authentication, JSON `content-type` and `accept`,
`accept-encoding: identity`, no redirects, `trust_env=False` and a client of its own, closed
after the call, also on cancellation. `asyncio.timeout(min(timeout_s, timeout_seconds))`
bounds the connection, the headers and the whole body, which is read up to
`max_response_bytes` decoded bytes. Only the configured origins are contacted.

| Outcome                                                       | Status | `code`, message                                                     |
| ------------------------------------------------------------- | ------ | ------------------------------------------------------------------- |
| HTTP 200 with a UTF-8 JSON object                             | 200    | The body, redacted; usage normalized                                |
| HTTP 200 with any other body                                  | 502    | `provider_error`, `The provider's response is not a JSON object.`   |
| Any other HTTP status, redirects included                     | 502    | `provider_error`, `The provider answered with HTTP <status>: <detail>` |
| A body over `max_response_bytes`                              | 502    | `provider_error`, `The provider's response exceeds <limit> bytes.`  |
| An asyncio or httpx timeout                                   | 504    | `provider_timeout`, `The provider did not answer within <s> seconds.` |
| No time left: the smaller timeout is not positive             | 504    | `provider_timeout`, `No time was left for the provider call.`; nothing is sent |
| Any other httpx error                                         | 502    | `provider_error`, `The connection to the provider failed (<exception type>).` |

Error bodies are exactly `{"error": {"code", "message", "type"}}`, with type `provider_error`
(502) or `timeout_error` (504), as the gateway's own. The provider's status is kept in the
message: `<detail>` is the provider's `error.message`, followed by ` (<error.code>)` when the
code is a non-empty string, else the stripped body text, else `no details.`; it is redacted,
then cut to 500 characters ending in `…`. Exception texts are never kept. A cancellation
propagates once the client is closed; any other exception propagates and the gateway answers
502.

Redaction replaces every occurrence of the key with `[redacted]`, in the keys and strings of
a returned body and in error messages. Headers are never returned.

## Usage normalization

`Usage.input` counts uncached input only.

- OpenAI: input = `prompt_tokens` − `prompt_tokens_details.cached_tokens` −
  `prompt_tokens_details.cache_write_tokens`; cached input and cache write are those two
  counts; output = `completion_tokens`.
- DeepSeek: input = `prompt_cache_miss_tokens`, cached input = `prompt_cache_hit_tokens`,
  cache write 0, output = `completion_tokens`.

Usage is `None` (estimated settlement) when `usage` or one of these counts is missing, a count
is not a non-negative integer (booleans excluded), cached input plus cache write exceed the
prompt, DeepSeek's `prompt_tokens` differs from hits plus misses, or a `total_tokens` differs
from prompt plus completion.

## Simulated provider

`SimulatedProvider` never uses the network and answers any model at once, whatever its
provider. For each model id it cycles through the configured replies in call order, shared by
all runs of the process; an empty sequence counts as none, and configured replies take
precedence over the requested format. Without configured replies it answers:

- for `json_schema` output, the smallest deterministic instance of the schema (`{}` when the
  request has none), as canonical JSON text (sorted keys, no spaces): the first `enum` value;
  the `const` value; otherwise by type, the first non-null one of a list and `object` when
  absent: objects with their required properties only (`{}` for an undeclared one), integers
  and numbers at `maximum` if present, else `minimum`, else 0 (an integer bound rounds
  inwards), strings `"simulated"`, booleans `true`, arrays empty, `null` and unknown types
  `null`; a schema that is not an object gives `{}`;
- for `json_object` output, `{}`;
- otherwise `Simulated reply to: <first 200 characters of the last user message>`, empty
  after the colon when no message has the role `user`.

Its usage is deterministic: input = UTF-8 bytes of the canonical request ÷ 4 rounded up,
output = reply bytes ÷ 4 rounded up, no cached input or cache write. Its body is
`{"id": "chatcmpl-simulated", "object": "chat.completion", "created": 0, "model":
<settings.model>, "choices": [{"index": 0, "message": {"role": "assistant", "content"},
"finish_reason": "stop"}], "usage": {"prompt_tokens", "completion_tokens", "total_tokens"}}`.

## Porting

Ported from `archive/s06-c11-wip~1` (commit `a844514`),
`components/model-provider/src/slow_thinker_model_provider/`: `_requests.py` (the adapter
mapping only, since the gateway validates requests), `_transport.py`, `_capture.py` and
`_endpoint.py`, with `httpx` instead of `httpx2` and `contracts` instead of host SDK types;
and from `origin/main`, `adapters/openai/_usage.py` usage extraction. The model-provider tests
`test_model_provider_requests.py`, `test_model_provider_transport.py`,
`test_model_provider_endpoints.py` and `test_model_provider_cancellation.py` are carried as
`backend/tests/providers/`.

## Acceptance

Tests with `httpx.MockTransport` cover both adapters' mapping, every error path,
redaction, bounded bodies, timeout, usage normalization and the simulated provider's
cycling and determinism. Branch coverage at least 90%.
