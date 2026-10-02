# JSON experiment authoring

Imports and edits personal experiment definitions through the connected operator
library. Source and credentials remain in memory.

Use the public entry point; implementation files remain private.
See [specification.md](specification.md) for its contract.

Import UTF-8 JSON or edit the text, then validate before saving. The editor limits
files and text to 1 MiB (1,048,576 UTF-8 bytes); configured backend limits may be
smaller. Submitted text is preserved, so the backend can reject duplicate keys and
invalid definitions without silently rewriting the draft. Saved sources load as
exact text, preserving numeric values without a browser JSON reconstruction.

Create a draft from the selected saved definition for a new revision or variant.
Keep the graph ID for a new revision, or change it for a variant; both record the
exact selected identity in `derived_from`. Draft creation freezes editing while
the server prepares the unsaved text. Save creates an immutable definition.
Definition validation does not guarantee future execution inputs or availability.

A pending save freezes editing. If its outcome is unconfirmed, retry the same
source to recover idempotently. Discarding such a draft does not establish whether
the previous save succeeded. Selection or credential changes discard stale replies;
disconnecting clears the editor. After confirmed Save, the editor restores the
currently selected source until the library selects the confirmed saved revision;
its saved identity remains visible if library refresh fails. Run controls remain
unavailable for dirty drafts.

The [component tests](../../../tests/definition-editor.test.tsx) and companion
import, stale, recovery, failure and callback-guard tests cover raw numeric source,
UTF-8 limits, validation invalidation, pending locks and unchanged-source replay.
The [authoring journey](../../../tests/journeys/personal-authoring.spec.ts) covers
production HTTP/storage import, editing, saving, reload, variants and execution;
the [recovery journeys](../../../tests/journeys/personal-recovery.spec.ts) cover
lost responses and post-confirmation listing failure. Browser execution uses
deterministic operations; provider behavior is verified separately.

## S04–S06 development

DefinitionSession exposes the public EditorModel to app composition. Source patches
lock conflicting changes and preserve the previous source on rejection. Structured
and JSON edits share the same baseline and existing immutable save/replay behavior.
Review and functional verification are complete; see [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02).

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
