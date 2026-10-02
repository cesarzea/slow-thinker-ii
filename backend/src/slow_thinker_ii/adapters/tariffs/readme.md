# Tariff catalog import

Fetches and validates the Vercel model catalog into immutable local tariff revisions.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

`DeepSeekTariffSource` independently imports the official direct Flash HTML table.
Its bounded parser retains captured HTML and normalized rates, schedule and the
reviewed holiday calendar under one immutable digest. Application composition
owns daily refresh; this package performs no model calls.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
