# Redirector

Runs one deterministic Python selector from its exact installed package environment
and returns one declared output port. It makes no model calls and never retries or
chooses a fallback route.

```python
from slow_thinker_redirector import Redirector, parse_config

config = parse_config(
    {
        "outputs": ["accept", "revise"],
        "selector": "review_rules:choose",
        "input_schema": {
            "type": "object",
            "properties": {"accepted": {"type": "boolean"}},
            "required": ["accepted"],
            "additionalProperties": False,
        },
    }
)
component = Redirector(config, lambda value: "accept" if value["accepted"] else "revise")
```

The public functional interface is `Redirector.route(value) -> str`. Its
configuration is immutable. `RedirectorHost.describe(config)` validates the
configuration and resolves the installed `module:callable` during trusted setup;
the host's `route` operation accepts `{"value": ...}` and returns `{"port": ...}`.
Input validation, selector exceptions and invalid returns fail without a route.
The public constructor also accepts a callable explicitly for ordinary Python use.

Prepare the bundled selector with `python -m tooling.components --component
redirector`; supply `--selector-project /absolute/path` for an explicit trusted
Hatchling project containing another selector. The selector distribution and its
closure enter the exact hashed installation lock. Invocation arguments cannot
supply source, paths or import references. Selectors are trusted Python, not a
sandbox; blocking execution remains subject to platform deadlines and process
termination.

See [specification.md](specification.md), the
[bounded example](../../docs/contracts/examples/bounded-review.md) and
[verification record](../../docs/verification.md). Scoped functional, MCP and offline preparation tests pass. Installed whole-system acceptance and repository verification pass.
