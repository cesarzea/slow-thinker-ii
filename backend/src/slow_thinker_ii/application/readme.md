# Application

The S06 use cases — graph library, runs, the LLM gateway, component reports and usage — and
the ports that the adapters implement: stores, the budget ledger, host launching, LLM providers
and the clock. No framework, persistence, process, network or provider imports.

Use the [public entry point](__init__.py); private implementation files are not an integration API.
In-memory fakes of every port, for adapter and use-case tests, are in
[`backend/tests/support`](../../../tests/support/__init__.py).

See [specification.md](specification.md) for the interface, behaviour and acceptance criteria.
