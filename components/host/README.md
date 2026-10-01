# Component Host

Shared Python SDK for exposing independent Slow Thinker II components through
MCP over standard input/output. This is hosting infrastructure, not an agent.

## Responsibilities

- Declare operations with JSON input and output schemas.
- Validate requests and replies at the MCP boundary.
- Pass invocation grants and deadlines to component implementations.
- Read platform-supplied bootstrap configuration and run the component server.

Components implement the `HostedComponent` protocol: `operations()` describes
their interface and `invoke()` handles an invocation. Import the public API from
`slow_thinker_host`; `Operation`, `Invocation`, `ToolReply` and `run_stdio` are its
main building blocks.

The current host accepts one active invocation at a time. The platform remains
responsible for authorization, execution supervision, accounting and persistence.
This package does not provide an operating-system sandbox.

## Development

Requires Python 3.13. From the repository root, use `make setup` to install the
development environment and `uv run --locked pytest components/host/tests` to run
this package's tests. No provider credentials are needed.

See the [component API](../../docs/contracts/python-component-api.md) and
[lifecycle contract](../../docs/contracts/component-lifecycle.md).

## Module contract

See [specification.md](specification.md) for the public boundary and acceptance criteria.

First-cycle implementation and local acceptance checks are complete.

## Managed outgoing calls and optional reports

`mcp_endpoint_from_record` reads the trusted `clients.mcp` bootstrap entry into an
immutable `McpEndpoint`. It carries explicit loopback `/mcp` URL, timeout/cleanup
limits and `(slot, operation) -> alias` resource bindings. For each invocation:

```python
from slow_thinker_host import managed_mcp_client

async with managed_mcp_client(endpoint, invocation) as client:
    reply = await client.call_tool(endpoint.alias("worker", "generate"), arguments)
```

The helper provides the ordinary pinned MCP client with a fresh bearer grant,
explicit wire discovery and the remaining deadline. It disables inherited proxy
configuration, redirects and shared discovery caches, and performs no business
calls or retries on the component's behalf. Discovery and calls are mediated by
the platform; bindings alone grant no authority.

`report_component(endpoint, invocation, report)` optionally records `progress`,
`state`, `explanation` or `reasoning` evidence via `platform.report`. A successful
reply confirms durable recording; the platform assigns identity and redacts data.
Missing reports are valid and remain explicit. No provider credentials are used.

Install `slow-thinker-host[langchain]` to use the optional
`managed_langchain_tools(endpoint, invocation)` adapter. It exposes discovered
permitted operations as normal `StructuredTool` instances, preserving their input
schemas and structured results. Each async tool call obtains a fresh scoped MCP
client; errors and cancellation propagate. These bindings retain the invocation's
authority and cannot extend its lifetime. No incompatible MCP adapter is installed.

Scoped tests verify standard MCP wire behavior with simulated HTTP, cancellation,
deadlines, bounded close, reporting receipts and the LangChain tool binding.
Real gateway, storage and installed composition acceptance checks pass with simulated providers.
