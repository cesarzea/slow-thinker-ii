# ADR 0019: Platform LLM service with provider-declared parameters

- Status: Accepted
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR04, CR10, CR13
- Supersedes: the per-graph model resource of the previous implementation

## Context and problem statement

LLMs are provided by the platform, configured once with server-side credentials.
A component that needs an LLM shows the platform's list and, for the selected
entry, the invocation parameters that its provider supports. Parameters were
previously owned by the consumer and validated by three disagreeing layers.

## Decision outcome

The operator configures providers and models in the server configuration. Each
catalog entry publishes a JSON Schema of its invocation parameters, produced by
the provider adapter from the model's reviewed capabilities. The same schema is
rendered by the interface, validated when a graph is saved and validated again
before each call. Components call the platform's OpenAI-compatible endpoint with
their invocation grant; parameter names follow the Chat Completions convention so
that familiar client libraries keep working. Provider adapters run in the platform
process with bounded transport, one attempt per call and redacted capture. See the
[LLM service contract](../contracts/llm-service.md).

## Consequences

Credentials never reach component processes. Adding a provider means adding an
adapter and catalog entries; no component changes. Per-user or per-workspace
catalogs later reuse the same schema-driven contract.
