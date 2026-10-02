# Redirector: specification

Executes one user-authored deterministic Python selector and returns a declared output port.

## Public Python boundary

- `RedirectorConfig` is an immutable record containing unique `outputs`, the selector import reference and canonical input-schema JSON.
- `parse_config(value: JsonObject) -> RedirectorConfig` rejects unsupported or inconsistent configuration.
- `Redirector(config: RedirectorConfig, selector: Callable[[JsonValue], str])` receives the configured callable explicitly.
- `Redirector.route(value: JsonValue) -> str` validates input, invokes the callable once and validates the chosen port.
- `RedirectorHost` implements `HostedComponent` and exposes `route({"value": ...}) -> {"port": ...}`.
- Export the public contracts through `slow_thinker_redirector`; private modules stay private.

## Behavior and errors

- Validate the declared input schema and nonempty unique output names before hosting.
- Resolve `module:callable` only from the exact installed package environment during trusted setup/description.
- Reject coroutine functions, asynchronous-generator functions and callable objects
  with asynchronous `__call__` implementations before publishing the selector.
- A selector error, invalid return or undeclared output fails without a fallback or repeat invocation.
- Enforce platform deadlines by host process control; do not claim arbitrary Python is sandboxed.
- Preserve errors as inspectable managed-call failures without injecting agent state.

## Shared contracts

- [Conditional routing](../../docs/contracts/conditional-routing.md) defines exact wire shapes, configuration and acceptance cases.
- [Managed gateway](../../docs/contracts/managed-gateway.md) defines outgoing client setup and authority.
- [Component installation](../../docs/contracts/component-installation.md) defines packaging and isolated execution.

No backend implementation imports are permitted. First-cycle implementation and local acceptance checks are complete.

Host failures use `MCPError(code=-32603, data={"stage": ..., "reason": ...})`.
The platform preserves the protocol error as a failed operation result. It is not
a `ToolReply` success/error union and has no eligible port; declared output
schemas describe successful structured values only.

## S04–S06 active delivery

Follow [the shared contract](../../docs/contracts/tools-memory.md). Implementation owner: B.

Retain deterministic packaged selectors and declared output ports. New structured authoring exposes existing options; standalone and embedded use remain supported.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
