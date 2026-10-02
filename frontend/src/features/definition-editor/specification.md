# JSON experiment authoring: specification

## S03 personal experiment library

Follow the [shared contract](../../../../docs/contracts/personal-experiments.md) for wire values, data origins,
public interfaces, validation scope, errors, immutable identity, paging and failure
handling. Implementation owner: C.

Implement the DefinitionEditor public skeleton. Fetch selected exact raw text
through DefinitionClient.source; GraphDetail remains a canvas projection. Import
a bounded UTF-8 JSON file; edit, validate, save and discard. Create revisions or
variants through the abortable DefinitionClient.draft operation with exact source
and target identities; never reconstruct graph JSON with browser parse/stringify.
Lock editing during pending draft generation and Save. Preserve raw JSON on POST,
dirty/validation/error states and a frozen pending save source.
Recover uncertain saves by replaying that source. Discard stale async replies after
identity/credential changes. No localStorage source/credential writes or automatic
paid calls. Styling and internal hook/file structure are local choices; maintain
accessibility and existing unit-size/complexity rules.

After confirmed Save, restore source and baseline to the originally selected raw
text and clear validation until catalogue selection actually changes. Retain the
confirmed saved identity through onSaved and its visible message. Listing failure
must leave the displayed source and any subsequent draft parent consistent with
the still-selected saved identity.

Acceptance follows the shared S03 scenarios. Development delivery does not claim
testing is complete. Keep module-private choices within these public contracts.

Editor-local import/submission cap: 1,048,576 UTF-8 bytes. Display the limit;
backend limits remain authoritative. No new capability endpoint is introduced.

## S04–S06 active delivery

Follow [the shared contract](../../../../docs/contracts/product-workspace.md). Implementation owner: C.

Integrate structured forms with the same source/draft/dirty/validation/save state. Extend public props or export controlled authoring state as needed without sibling feature internals. Guard asynchronous source patches and preserve uncertain-save recovery.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
