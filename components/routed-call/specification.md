# RoutedCall: specification

Composes a normal worker and redirector through mediated MCP calls while exposing one agent operation.

## Public Python boundary

- `RoutedCallConfig` records input schema, worker operation/output schema, router input pointer and declared outputs.
- `parse_config(value: JsonObject) -> RoutedCallConfig` validates the effective configuration.
- `RoutedCall(config: RoutedCallConfig, endpoint: McpEndpoint)` receives trusted client bindings separately from graph arguments.
- `async invoke(arguments: JsonObject, invocation: Invocation) -> ToolReply` calls the worker and router through a fresh standard MCP client.
- `RoutedCallHost` exposes `invoke`; export public contracts through `slow_thinker_routed_call`.

## Behavior and errors

- Pass input unchanged to the configured worker operation; make no model call independently.
- On worker success, extract the declared JSON Pointer and invoke router.route with that value.
- Validate the router port and preserve the worker envelope under the successful result's value.
- Failed worker, extraction or router work has no eligible route and triggers no automatic retry.
- Never call a peer endpoint directly; both subcalls use platform aliases under the active invocation grant.
- Required worker/router bindings and output schemas must be validated during preparation.

## Shared contracts

- [Conditional routing](../../docs/contracts/conditional-routing.md) defines exact wire shapes, configuration and acceptance cases.
- [Managed gateway](../../docs/contracts/managed-gateway.md) defines outgoing client setup and authority.
- [Component installation](../../docs/contracts/component-installation.md) defines packaging and isolated execution.

No backend implementation imports are permitted. First-cycle implementation and local acceptance checks are complete.

The bundled descriptor uses an `agent` worker slot and a `resource` router slot
for this first agent-composition profile. These roles are descriptor constraints,
not hardcoded Python behavior or a platform-wide rule.

Host failures use `MCPError(code=-32603, data={"stage": ..., "reason": ...})`.
The platform preserves the protocol error as a failed operation result. It is not
a `ToolReply` success/error union and has no eligible port; declared output
schemas describe successful structured values only.
