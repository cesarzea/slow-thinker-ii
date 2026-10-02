# Static definition validation: specification

Implements the definition-only checks in the
[personal experiment contract](../../../../../../docs/contracts/personal-experiments.md)
under the [catalog specification](../specification.md). This package is private to
the catalog adapter and does not define a separate cross-package contract.

`LocalSchemas` loads trusted schema resources and resolves references locally.
`validate_definition` consumes raw graph data, local schemas and the registered
descriptor directory; it returns a canonical immutable library record and roles
for the existing detail projection. Other files separate schema diagnostics,
descriptor/configuration checks, literal inputs, graph references and profile
semantics. The public catalog constructor defers these local file reads until use.

Configuration checks follow registered descriptors, declared schemas and the
[public LLMCall policy](../../../../../../docs/contracts/llm-call.md). Errors use
bounded JSON Pointers and fixed messages. No component startup, SDK discovery,
installation description, provider call or database access occurs here.

Acceptance and remaining review/testing work belong to the parent catalog ticket.
Focused S03 validation acceptance and scoped static checks pass; complete
coordinator verification remains pending.
