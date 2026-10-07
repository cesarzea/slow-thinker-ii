# Component host SDK

The Python side of the [component protocol](../../docs/contracts/component-protocol.md):
it reads the bootstrap document, serves the position's MCP tool over standard input
and output, enforces each call's time budget and concurrency, validates arguments and
results, and gives handlers a context with the remaining time, reports and an
OpenAI-compatible client bound to the platform's LLM service.

```python
from slow_thinker_host import Emission, read_bootstrap, run_host


class Echo:
    async def activate(self, message, context):
        await context.report("step", "echoing")
        return [Emission("out", message)]


run_host(read_bootstrap(path), node=Echo())
```

Raise `HandlerError(code, message)` to fail a call with your own code. Components
ship their `component.json` inside their package; `read_declaration` and
`check_bootstrap` check a bootstrap against it at startup.

Tests: `uv run --locked pytest components/host/tests`. See
[specification.md](specification.md) for the public interface and error codes.
