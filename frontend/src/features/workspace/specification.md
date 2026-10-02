# Structured experiment configuration: specification

## Active S04–S06 contract

Follow [the shared contract](../../../../docs/contracts/product-workspace.md) and the
[delivery ownership/acceptance matrix](../../../../docs/contracts/../specification/s04-s06-delivery.md).
Implementation owner: C.

Implement schema-driven component/resource and supported graph editing, shared dirty source and guarded source patches, model/reasoning selectors, child bindings, permission actions and configuration settings. Consume public validated APIs only; no sibling feature internals or browser reconstruction of complete graph JSON. Integrate with existing authoring/save/recovery APIs.

Use exact public dependency entry points named in the shared contract. Keep
implementation-local choices local; report missing cross-package decisions.
Constructors/imports perform no external business I/O. All managed calls retain
permissions, deadlines, evidence and applicable budgets.

Development delivery must map acceptance IDs to code and identify verification
remaining. Test implementation belongs to the later testing phase under M06.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
