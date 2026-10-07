# LLM service

| Contract control | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| Contract ID      | CORE-LLM-1                                                                  |
| Decisions        | [ADR 0019](../adr/0019-platform-llm-service.md), [ADR 0018](../adr/0018-derived-authorization.md), [ADR 0022](../adr/0022-budgets-and-request-reservations.md) |
| Journeys         | V05, V06, V09, J1–J3                                                         |

The platform provides LLMs as a service. The operator configures providers and
models on the server; graphs select catalog entries; components call the selected
entry through the platform. Provider credentials never leave the platform process.

## Server configuration

```json
{
  "llm": {
    "providers": {
      "openai": {"base_url": "https://api.openai.com/v1", "credential_env": "OPENAI_API_KEY", "timeout_seconds": 120},
      "deepseek": {"base_url": "https://api.deepseek.com", "credential_env": "DEEPSEEK_API_KEY", "timeout_seconds": 120}
    },
    "models": [
      {
        "id": "openai/gpt-6-luna",
        "label": "OpenAI · GPT-6 Luna",
        "provider": "openai",
        "model": "gpt-6-luna",
        "max_output_tokens": 128000,
        "default_output_tokens": 1024,
        "reasoning_efforts": ["none"],
        "temperature": "unsupported",
        "tariff": {"…": "see the accounting contract"}
      }
    ]
  }
}
```

| Model field             | Rule                                                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------- |
| `id`                    | `^[a-z][a-z0-9-]*/[a-z0-9][a-z0-9.-]*$`, unique                                              |
| `label`                 | 1–60 characters, shown to users                                                              |
| `provider`              | A configured provider with a platform adapter: `openai` or `deepseek` in S06, plus `simulated` for tests and demonstrations |
| `model`                 | The provider's model name                                                                    |
| `max_output_tokens`     | Reviewed provider maximum                                                                    |
| `default_output_tokens` | Default for new selections, at most `max_output_tokens`                                     |
| `reasoning_efforts`     | Reviewed values; the first is the default                                                    |
| `temperature`           | `unsupported`, `supported`, or `without_reasoning` (only when reasoning is `none`)            |
| `tariff`                | Reviewed rates, see the [accounting contract](accounting.md)                                 |

Only the exact configured `base_url` origins are contacted. The `simulated` provider
returns deterministic replies without network access and is used by required tests.

## Catalog entries and parameter schemas

The catalog served to the interface lists each model as
`{"id", "label", "provider", "parameters"}`. The provider adapter generates
`parameters`, a closed JSON Schema object, from the model's reviewed fields:

| Property                | Present when                         | Schema                                                                  |
| ----------------------- | ------------------------------------ | ----------------------------------------------------------------------- |
| `max_completion_tokens` | Always; required                     | integer, title “Max output tokens”, 1 to `max_output_tokens`, default `default_output_tokens` |
| `reasoning_effort`      | More than one reviewed effort        | enum of `reasoning_efforts`, title “Reasoning”, default the first        |
| `temperature`           | `temperature` is not `unsupported`   | number 0–2, title “Temperature”, default 1                               |

For `without_reasoning`, the schema adds `"if": {"properties": {"reasoning_effort":
{"const": "none"}}}, "else": {"properties": {"temperature": false}}`. Parameter names
follow the Chat Completions convention so that ordinary client libraries work.
The [catalog example](examples/llm-catalog.json) shows both S06 providers.

## Selection in a graph

A component declares `{"service": "llm", "pointer": …}`. The value at that pointer is
`null` or `{"llm": "<entry id>", "parameters": {…}}`. Graph validation reports
`service_not_selected`, `unknown_service_entry` and `invalid_service_parameters` as
defined in the [graph document contract](graph-document.md).

## Calls

Components call `POST {llm_base_url}/chat/completions` with
`Authorization: Bearer <invocation grant>`. The body is a Chat Completions request:

| Field             | Rule                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `model`           | A catalog entry id. It must be the entry selected at one of the calling component's declared uses; otherwise `403 model_not_allowed` |
| `messages`        | 1–100 messages with role `system`, `user` or `assistant` and string content                    |
| `response_format` | Optional: `{"type": "text"}`, `{"type": "json_object"}` or `{"type": "json_schema", "json_schema": {"name", "schema", "strict"}}` |
| Parameters        | Every other field must validate against the entry's parameter schema                         |

`stream`, `n` other than 1, tools, functions, logit options and other unsupported
fields are rejected with `400 invalid_request` before any reservation or provider
call. Missing parameters take their schema defaults, so every dispatched request
carries an explicit output limit.

For an accepted request the platform:

1. Authorizes the grant, which identifies the run, the node or embedded component
   and the activation.
2. Validates the request and computes the reservation bound.
3. Reserves the bound against the run, day and month budgets. A denial returns
   `402 budget_exhausted` with the scope and stops the run.
4. Calls the provider adapter: one attempt, no redirects, bounded response size,
   timeout equal to the smaller of the call's remaining time and the provider timeout.
5. Normalizes usage, settles the reservation and records the call.
6. Returns the provider's response in Chat Completions form, including any
   `reasoning_content`, or an error.

| Status | Code                   | Meaning                                                   |
| ------ | ---------------------- | --------------------------------------------------------- |
| 400    | `invalid_request`      | Unsupported field or parameters outside the schema        |
| 401    | `invalid_grant`        | Missing, unknown or expired grant                         |
| 402    | `budget_exhausted`     | A reservation was denied; the run stops                   |
| 403    | `model_not_allowed`    | The entry is not selected in the caller's configuration    |
| 502    | `provider_error`       | The provider rejected the request or failed               |
| 504    | `provider_timeout`     | No complete response within the time budget               |

Error bodies are `{"error": {"code": string, "message": string, "type": string}}`.
Provider messages are passed on after credential redaction.

## Provider adapters

| Adapter    | Mapping                                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------------------- |
| `openai`   | Chat Completions request with `store: false`, `service_tier: "default"`; fields unchanged             |
| `deepseek` | `max_completion_tokens` → `max_tokens`; `reasoning_effort: "none"` → `thinking: {"type": "disabled"}`, other efforts → thinking enabled with that effort; `json_schema` output → `json_object` with the schema stated in a system instruction; only `system`, `user` and `assistant` roles |
| `simulated`| Deterministic reply derived from the request; configurable replies for tests                           |

A request without `reasoning_effort` (an entry with a single reviewed effort has no
such parameter) is sent with the reviewed default. DeepSeek accepts only `json_object`
output, so a `json_schema` request is sent as `json_object`, and the instruction
`Answer with one JSON object that conforms to this JSON Schema: <schema>` is appended
to the first system message or sent as a new first one. The caller still validates the
reply; DeepSeek may return empty content in this mode. `llm.called` records the request
as the platform dispatched it, before this adaptation.

Each adapter normalizes usage into input, cached input, cache write and output
tokens for the [accounting contract](accounting.md) and redacts credentials from
everything it returns or records.
