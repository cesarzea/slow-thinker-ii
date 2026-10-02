# Workspace discovery: specification

Coordinator-owned S04–S06 adapter. Public WorkspaceCatalog.read returns the exact
[workspace catalogue](../../../../../docs/contracts/product-workspace.md).
Consume public ComponentCatalog, ResourceSettings/model_capabilities and injected
profile/tariff readers. Do not invoke/install components or expose credentials.
Preserve unavailable registered types and explicit tariff/review status.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
