# Engine

The run scheduler of the [execution contract](../../../../docs/contracts/execution.md): FIFO
deliveries, activations within the plan's limits, the embedded output pipeline, per-call time
budgets and grants, and termination with the first stop cause. Pure `asyncio` behind ports; it
launches no processes and does no I/O.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for the interface, behaviour and acceptance criteria.
