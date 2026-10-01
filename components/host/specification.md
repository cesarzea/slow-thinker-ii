# Component host SDK: specification

Supplies optional common hosting contracts for independently installed local MCP components.

## Public boundary

The [public entry point](src/slow_thinker_host/__init__.py) is authoritative for exported names and signatures.

- HostedComponent declares operations and async invoke behavior.
- Operation, Invocation and ToolReply define operation schemas, trusted invocation context and replies.
- read_bootstrap, create_server and run_stdio implement configured process hosting.
- GRANT_META, DEADLINE_META and PROTOCOL_VERSION define the pinned host wire metadata.

## Required behavior

- Validate effective input/output schemas and keep authority metadata outside business arguments.
- Serve the pinned protocol profile; ordinary component code remains trusted local Python.
- The current host serializes active invocations; it does not claim general concurrent instance support.

## Dependencies and ownership

Pinned MCP SDK and schema-validation dependencies; independent of backend implementation imports.

## Acceptance criteria

- An invalid operation request cannot bypass the declared component schema.
- Host replies preserve structured success/error content and invocation correlation.

## Shared contracts

- [python-component-api](../../docs/contracts/python-component-api.md)
- [component-lifecycle](../../docs/contracts/component-lifecycle.md)

## Implementation gaps

The first-cycle implementation, integration and repository verification checks pass.

## Sprint additions

- [managed-gateway](../../docs/contracts/managed-gateway.md) defines the planned cross-package contract; implement it without changing existing supported behavior.

The public SDK also exports `McpEndpoint`, `McpResource`,
`mcp_endpoint_from_record`, `managed_mcp_client`, `report_component` and the optional
`managed_langchain_tools`. MCP endpoint bindings are immutable records; clients
and credentials are scoped to one invocation. The optional LangChain dependency
uses the existing pinned compatibility candidate and is imported only when used.

## October 2026 maintenance: Generator typing compatibility

The decorated `managed_mcp_client` implementation uses
`AsyncGenerator[Client]` for Pyright 1.1.414. It yields the same managed MCP
`Client`; keep ordinary async iterator interfaces and invocation authority unchanged.
