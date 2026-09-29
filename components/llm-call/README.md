# LLMCall

A configurable agent component that makes one LLM call per invocation. Proposer,
planner and reviewer are roles configured with this same component.

## Behavior and configuration

The `generate` operation validates a JSON object against `input_schema`, builds
messages from `instructions` and that input, then uses the OpenAI client interface
through the platform's managed gateway. The model is supplied by its resource
binding; `parameters` contains permitted generation settings.

`output` selects text or JSON validated against a schema. Successful results
contain `status`, `format` and `value`; output-validation failures retain the model
text and structured error details. The component does not automatically repair
or retry a response.

The host creates a fresh component and client for each invocation. Context comes
from the supplied input; there is no built-in conversation memory or agent loop.
All provider access and spending controls remain mediated by the platform.

## Customization

Import `LLMCall` from `slow_thinker_llm_call`. Subclasses can override
`build_messages`, `parse_response` and `validate_result`. See the
[GroundedReview example](../../examples/grounded-review/README.md).

## Development

Requires Python 3.13. From the repository root, run `make setup`, then
`uv run --locked pytest components/llm-call/tests`. Tests use simulated responses.
For managed installation and execution, follow the
[development instructions](../../CONTRIBUTING.md).

See the [component contract](../../docs/contracts/llm-call.md),
[text configuration](../../docs/contracts/examples/llm-call-text.config.json) and
[JSON configuration](../../docs/contracts/examples/llm-call-json.config.json).

## Module contract

See [specification.md](specification.md) for the public boundary and acceptance criteria.
