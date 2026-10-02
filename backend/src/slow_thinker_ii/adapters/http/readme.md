# HTTP boundaries

Exposes operator queries, immutable personal experiment authoring and familiar model calls through authenticated local HTTP routes.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.

Execution-enabled composition installs `definition_router` behind the operator boundary.
Source/draft responses supply canonical domain JSON text for authoring, preserving numeric values.
S03 targeted HTTP/Start tests cover authoring, strict transport, authority, paging,
exact identities and bounded failures. Whole-system local verification is complete.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
