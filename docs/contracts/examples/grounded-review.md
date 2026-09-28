# GroundedReview: code inheritance specimen

**Status: Implemented and tested as an independent Python package.** This example adds cross-input validation through code: every citation in a structured review must name a source supplied to that activation. It does not verify that a source supports a claim.

The [descriptor](grounded-review.component.json) reuses `LLMCall`'s public result/configuration contract and restricts its configuration to the review input and output schemas. The [instance](grounded-review.instance.json) configures JSON output; [input](structured-review.input.json) supplies the allowed source identifiers.

Module `example_grounded_review` uses only public SDK exports; the executable source is in `examples/grounded-review`:

```python
from slow_thinker_llm_call import (
    JsonObject,
    JsonValue,
    LLMCall,
    OutputIssue,
    OutputValidationError,
)


def _strings(value: JsonValue) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("Expected a validated string array.")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise TypeError("Expected a validated string array.")
        result.append(item)
    return result


class GroundedReview(LLMCall):
    def validate_result(self, value: JsonValue, arguments: JsonObject) -> None:
        super().validate_result(value, arguments)
        if not isinstance(value, dict):
            raise TypeError("Expected a validated review object.")
        allowed = set(_strings(arguments["available_sources"]))
        cited = set(_strings(value["citations"]))
        unknown = cited - allowed
        if unknown:
            issue = OutputIssue(
                path="/citations",
                message=f"Unknown sources: {', '.join(sorted(unknown))}",
            )
            raise OutputValidationError(issues=(issue,))
```

Common input/output-schema validation occurs before this hook. Type errors indicate a violated SDK invariant, not another LLM attempt. The hook makes no model/resource calls, stores no mutable activation state and returns no replacement result. A valid review retains its parsed JSON value. An unknown reference produces the [structured validation failure](grounded-review-reference-error.result.json), retaining the exact model text.

The package dependency uses ordinary Python metadata:

```toml
[project]
name = "example-grounded-review"
version = "0.1.0.dev1"
dependencies = ["slow-thinker-llm-call==0.1.0.dev1"]
```

This excerpt matches the installable example and base packages. Development versions are fixed exactly. For a future stable base, the requirement can instead be `slow-thinker-llm-call==1.1.0` or `slow-thinker-llm-call>=1.1.0,<2.0.0` as agreed. A changed requirement needs a new derived-package release; selecting a permitted newer dependency creates a new lock.

The [trusted registration](grounded-review.registration.json) maps the concrete type to this public class and records its base relationship. MCP exposes only the resulting component operations. The four initial graphs remain ordinary `LLMCall` instances; this separate specimen exercises code specialization without conflating it with role configuration.
