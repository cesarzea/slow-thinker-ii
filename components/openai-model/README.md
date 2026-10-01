# OpenAI Model Resource

The provider resource that sends managed model requests to OpenAI. `LLMCall`
constructs and interprets agent messages; this package handles provider transport.

## Behavior and configuration

The MCP operation `complete` receives a native Chat Completions `request` and
returns the provider response, including usage when supplied, or an error envelope.
The platform handles authorization, budget reservations and cost settlement.

Configuration binds a model alias to the actual provider model and specifies
default and maximum output-token limits. The trusted launch binding supplies the
endpoint and credential separately from graph configuration.

Each invocation makes one HTTP attempt with bounded time and response size.
Automatic retries, redirects and inherited proxy settings are disabled. Reflected
provider credentials are redacted before responses leave the resource.

The current request profile supports text messages, one non-streaming completion
and no reasoning effort. Tool calls and other provider endpoints are outside this
profile. Import its public API from `slow_thinker_openai_model`.

## Development

Requires Python 3.13. From the repository root, run `make setup`, then
`uv run --locked pytest components/openai-model/tests`. Tests use local fixtures
and require no provider key or paid calls.

See the [provider profile](../../docs/contracts/openai-initial-profile.md) and
[managed execution setup](../../CONTRIBUTING.md#enable-local-execution).

## Module contract

See [specification.md](specification.md) for the public boundary and acceptance criteria.
