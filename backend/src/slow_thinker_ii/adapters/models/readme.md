# Reviewed model request and billing policies

`ModelProfile` selects the reviewed OpenAI or direct DeepSeek request profile.
`ModelPricePolicy` implements the existing quote/reconcile boundary against one
frozen tariff revision. These policies perform no provider network I/O.

OpenAI delegates to its existing public policy. DeepSeek reserves peak capacity,
checks native cache/usage totals and settles only an uninterrupted reviewed billing
interval. Missing or ambiguous evidence retains unresolved exposure.

Use the [public entry point](__init__.py); see [specification.md](specification.md)
and the [shared contract](../../../../../docs/contracts/model-resources.md).
Acceptance tests and mandatory shared verification pass; simulated transports
are distinguished from actual execution in the verification record.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
