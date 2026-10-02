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

## S04–S06 active delivery

Follow [the shared contract](../../../../../docs/contracts/model-resources.md). Implementation owner: A.

Retain existing OpenAIProfile/OpenAIPricePolicy compatibility and verified rate/usage semantics. New provider-neutral policy registry may delegate to this public API without changing existing tests or historical pricing.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## S04–S06 development compatibility review

The public profile/pricing implementation remains unchanged. Provider-neutral
`ModelProfile` and `ModelPricePolicy` delegate OpenAI request, quote and settlement
to these public interfaces, preserving existing digest/rate/usage semantics.
A06–A07 legacy accounting and historical-evidence regression verification remains
pending in the assigned M06 testing phase.

## S04–S06 scoped testing evidence

The assigned A acceptance/regression suite passes 532 tests using recorded official
prices, isolated SQLite state and simulated native provider transport. Ordinary
OpenAI SDK, LangChain and unchanged LLMCall requests cross actual loopback gateway,
managed authority, real model host/transport and pricing boundaries. Separate
caller grants select independent providers; cross-agent binding requests fail
before native dispatch. Exact cache/timing/calendar charges, source retention,
quanta rounding and historical quote/snapshot preservation pass.

Preparation evidence uses production InstalledWorkflowPreparer with explicitly
description-only installations; it does not claim installed inference. No paid
provider calls occurred. Scoped static checks pass. Coordinator review and full
unchanged verification remain pending; the complete S04–S06 delivery is not yet
claimed verified.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
