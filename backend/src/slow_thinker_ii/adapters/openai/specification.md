# OpenAI request and pricing policy: specification

Validates the supported OpenAI model profile and calculates managed cost evidence without calling the provider.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- OpenAIProfile validates supported requests and output bounds.
- OpenAIPricePolicy implements quote and reconcile against a frozen tariff revision.

## Required behavior

- Reject unsupported request options explicitly; do not silently drop them.
- Use a conservative reservation and retain the tariff revision used for each attempt.
- Missing or invalid usage remains unresolved rather than becoming a zero charge.
- Provider HTTP I/O belongs to the independently hosted model component.

## Dependencies and ownership

Public accounting and application contracts; no provider network client in this adapter.

## Acceptance criteria

- Supported requests yield a bounded charge basis before dispatch.
- Reconciliation separates usage categories and does not release unresolved exposure.

## Shared contracts

- [openai-initial-profile](../../../../../docs/contracts/openai-initial-profile.md)
- [accounting-policy](../../../../../docs/contracts/accounting-policy.md)
