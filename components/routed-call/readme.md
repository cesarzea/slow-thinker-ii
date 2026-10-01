# RoutedCall

Composes a normal worker and a Redirector through the platform's MCP gateway.
It adds routing to a worker without implementing its reasoning or changing its
result envelope.

`parse_config` freezes the input schema, worker operation/output schema, router
input pointer and declared ports. `RoutedCall(config, endpoint).invoke(arguments,
invocation)` opens a fresh standard MCP client, passes the input unchanged to the
bound worker, validates its result, extracts the configured JSON Pointer and calls
`router.route`. Success is `{"status":"succeeded","port":...,"value":worker_result}`.
Errors retain the failing stage and reason as MCP errors and produce no eligible
port. Neither worker nor router is retried.

`RoutedCallHost.describe(config)` publishes the effective operation;
`RoutedCallHost(config, operation, endpoint)` validates the frozen operation and
requires platform aliases for the `worker` operation and `router.route`.
Trusted bootstrap supplies the endpoint and aliases separately from business
arguments. The composition never opens a peer endpoint directly.

The bundled descriptor constrains its worker slot to the `agent` role and its
router slot to `resource`. This is the initial agent-composition profile. The
Python implementation has no role constraint; another conforming registration
may declare a different worker-role constraint.

Prepare with `python -m tooling.components --component routed-call`. The
[bounded example](../../docs/contracts/examples/bounded-review.md) contains an
ordinary LLMCall reviewer and deterministic selector within this composition.

See [specification.md](specification.md) and [verification record](../../docs/verification.md).
Scoped functional, MCP and offline preparation tests pass. Installed whole-system acceptance and repository verification pass.
