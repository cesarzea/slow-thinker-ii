# Structured experiment workspace

The public entry point exports structured source forms, discovered component and
resource inventories, configuration discovery, and effective settings. The app
composes these with the public definition editor and execution features.

Forms preview raw source ranges without reconstructing the complete graph in the
browser. Apply sends individual JSON values to the backend patch service; JSON and
form modes share the editor's source, baseline, validation and save recovery. A
field buffer changes the draft only after Apply. Bound resources grant no implicit
permission. Unknown schema constructs keep an explicit JSON editing path.

Trusted local schema documents resolve registered `$ref`, `allOf` and fragment
properties without network access. Preview depth is bounded to 64 levels; schema
resolution is bounded to 20 levels and 1,000 visits. Unsupported preview/schema
content remains editable through raw JSON.

Settings freeze each submitted command body and replay it unchanged after an
uncertain response. Discovery refresh does not discard a pending command. All
credentials and protected state remain in memory.

The [specification](specification.md) and
[shared contract](../../../../docs/contracts/product-workspace.md) govern behavior.
The component/graph/capability tests cover canonical and external registered
schemas, model choices, explicit child/resource bindings, input/route/order patches
and permissions. Resource tests distinguish draft consumers from admitted run
activity. Discovery and settings tests cover aborts, stale replies, typed errors,
pending locks and unchanged uncertain commands. Production browser journeys cover
configured personal authoring and server settings recovery. The deterministic
browser workers prove interface, HTTP/storage and scheduling composition; actual
provider/resource behavior requires separate runtime evidence.

Shared verification is recorded in [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02).

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
