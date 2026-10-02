# OpenAI request and pricing policy

Validates the supported OpenAI model profile and calculates managed cost evidence without calling the provider.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

Provider-neutral policies delegate OpenAI request and billing behavior to this
unchanged public API; DeepSeek pricing belongs to the separate models adapter.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
