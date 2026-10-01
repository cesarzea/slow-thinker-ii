# GroundedReview

An example of extending `LLMCall` through Python inheritance. It adds a validation
rule: every citation identifier in a structured review must belong to the
`available_sources` supplied with the input.

## Behavior

`GroundedReview` overrides `validate_result` and reuses the base component's
message construction, single model call, parsing and schema validation. Unknown
citation identifiers produce an `output_validation_failed` result containing the
model text and validation details.

This checks citation identifiers, not whether the cited sources support the
claims. Ordinary reviewer agents can use `LLMCall` directly; this example shows
when custom validation requires a code extension.

The package is installed independently and exposes `generate` through the same
managed MCP host and model gateway as `LLMCall`. Its public class is available
from `example_grounded_review`.

## Development

Requires Python 3.13. From the repository root, run `make setup`, then
`uv run --locked pytest examples/grounded-review/tests`. Tests use simulated
responses and require no provider credentials.

See the [base component](../../components/llm-call/README.md),
[configured instance](../../docs/contracts/examples/grounded-review.instance.json)
and [inheritance example](../../docs/contracts/examples/grounded-review.md).

## Module contract

See [specification.md](specification.md) for the public boundary and acceptance criteria.

## Packaged selector example

The same distribution also exports `choose` from its public root and the public
`example_grounded_review.review_rules` module. This deterministic function maps a
validated review's `accepted` boolean to `accept` or `revise` for the
[bounded review example](../../docs/contracts/examples/bounded-review.md).
The bounded example uses ordinary LLMCall reasoning; it does not instantiate the
GroundedReview subclass. The Redirector preparation recipe retains this selector
wheel in its exact hashed installation closure.
