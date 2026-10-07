# Provider adapters

The OpenAI, DeepSeek and simulated providers behind the application port `LlmProvider`, for the
[LLM service](../../../../../docs/contracts/llm-service.md). `HttpProvider` makes one bounded,
redacted HTTP attempt per call to a reviewed origin and normalizes the reported usage for
accounting. `SimulatedProvider` answers deterministically without network access, for tests
and demonstrations.

Use the [public entry point](__init__.py); private implementation files are not an integration API.
Tests run the HTTP adapters over `httpx.MockTransport` and never contact a provider.

See [specification.md](specification.md) for the interface, behaviour and acceptance criteria.
