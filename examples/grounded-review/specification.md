# GroundedReview example: specification

Demonstrates an independently packaged LLMCall subclass that validates returned citation identifiers.

## Public boundary

The [public entry point](src/example_grounded_review/__init__.py) is authoritative for exported names and signatures.

- GroundedReview specializes LLMCall.validate_result using the supplied available_sources.

## Required behavior

- Accept only citation identifiers present in the supplied source set.
- Return ordinary LLMCall validation failures while preserving received model content.
- Identifier membership does not establish factual correctness or semantic support.

## Dependencies and ownership

Public LLMCall extension API and an explicit compatible base dependency resolution.

## Acceptance criteria

- An unknown source identifier produces a retained structured output-validation failure.
- The example installs and runs independently without private base-module imports.

## Shared contracts

- [python-component-api](../../docs/contracts/python-component-api.md)
- [0008-component-inheritance-and-versions](../../docs/adr/0008-component-inheritance-and-versions.md)

## Bounded-review selector

`choose(value: JsonValue) -> str` is also exported through the public package root
and `example_grounded_review.review_rules`. It requires a boolean `accepted` and
returns `accept` or `revise` without external calls. Redirector performs full input
schema validation before invoking it. The ordinary LLMCall reviewer in the bounded
example does not use the GroundedReview subclass.
