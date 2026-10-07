# HTTP adapters

The platform's HTTP surface: the operator API version 2 under `/api/v2`, the model endpoint
`/v1/chat/completions` for components, the `/mcp` endpoint serving the `platform.report` tool, and
the compiled interface at `/` when configured. Routes call the application use cases on the
event-loop thread and never decide anything the use cases own.

Use the [public entry point](__init__.py): `create_http_app(services, settings, lifespan)` with
`HttpServices` and `HttpSettings`; `bootstrap` composes it. Private modules are not an integration
API. Route tests in [`backend/tests/http_adapter`](../../../../tests/http_adapter/http_harness.py)
serve the app over the shared in-memory platform of `backend/tests/support`.

See [specification.md](specification.md) for the interface, behaviour, error codes and acceptance
criteria.
