# Workspace public interfaces and state ownership

**S06-UX-FRONTEND / revision 2 / 2026-10-02.** Owner-authorized implementation; locally verified. Existing compatible exports remain available. See
[interaction](workspace-interaction.md) and [HTTP contracts](workspace-history-api.md).

## Dependency handoffs

All features import only public `api/index.ts` and `ui/index.ts` plus their own
internals. App composes features through public entry points and maps callbacks;
no sibling feature imports, including type-only imports. API owns wire records;
UI owns generic controls and buffers, not experiment state. Feature props reuse
the structural types below without importing another feature's definitions.

| Consumer            | Public source and exact origin                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Collection/Versions | DefinitionClient.experiments/versions/compare; fields defined in history API; existing source/draft/save keep exact text                    |
| Draft               | DefinitionClient.patch(source, operations, signal), preview(source, signal), validate/save; patches use `value_json` strings                |
| Configuration       | ConfigurationClient catalog; components matched by type_id + type_version; presentation, resource_slots, config_schema and schema_documents |
| Model editor        | Selected instance.resources[model_slot] → bound instance.config[provider_profile_pointer] → catalog.models[].provider_profile               |
| Canvas              | Current draft preview detail plus catalog presentation; saved-run definition for run mode; never source parsed with normal JSON.stringify   |
| Run history         | OperatorClient.experimentRuns(graphId, revision-or-null, signal, cursor?); not a filtered session-history page                              |
| Evidence            | OperatorClient.definition/execution and exact activation/call/payload IDs; resultSource supplies original JSON text                         |

Frontend API additions on DefinitionClient: `experiments(signal, query?, cursor?,
limit?)`, `versions(graphId, signal, cursor?, limit?)`, `compare(base, target, signal,
cursor?, limit?)`, `preview(source, signal)`. Read return types exactly match the
validated DTOs in the history contract; preview returns GraphDetail|null and issues.
Operator additions: `experimentRuns(graphId, revision, signal, cursor?)` and
`resultSource(runId, signal)`. Keep normal read timeout/cancellation/byte bounds;
no read failure becomes an uncertain mutation. Save retains existing uncertainty.

## Controlled authoring

UI exports the generic, experiment-independent value:

```typescript
interface FieldBuffer {
  readonly text: string;
  readonly error: string | null;
}
```

Definition-editor extends its public EditorModel with:

```typescript
readonly fields: ReadonlyMap<string, FieldBuffer>;
readonly generation: number;
readonly preview: GraphDetail | null;
readonly previewCurrent: boolean;
stage(key: string, buffer: FieldBuffer, operations: readonly PatchOperation[] | null): void;
flush(): Promise<boolean>;
currentSource(): string;
prepareCommand(): Promise<boolean>;
```

Keys are escaped JSON Pointers into the current source; root is reserved for
advanced raw editing. Staged operations are absolute exact-value patches; null
means the buffer is not currently valid. `stage` replaces that key's pending value,
increments generation and dirty status synchronously, before any async patch.
`flush` returns false for invalid/stale/failed processing and retains all buffers;
true means every captured valid buffer has reached canonical source. Do not turn
schema-validation failure into discarded text. The model owns batching and replay.
`currentSource` reads the latest canonical source after flushing; structural commands
must not use a source captured before asynchronous field processing.
`prepareCommand` flushes and requests an immediate static preview, returning true
only for a valid preview matching the latest source/generation. App supplies it as
GraphCommandDialog's flush adapter. Ordinary controls retain `flush` so incomplete
definitions remain repairable; failed command preparation preserves source/issues.

Workspace's public controlled props add `fields`, `onFieldChange(key, buffer,
operations)`, `selection`, `flush`, `prepareCommand` and `currentSource` to source/catalog/locked/patch. App passes model.stage
directly or through a typed adapter. UI controls accept buffer/onChange props and
report values; they perform no HTTP requests. Existing immediate-patch controls
remain compatible until their S06 callers are migrated together. Child modal fields
commit one staged group only on confirmation. No hidden private Apply buffer remains.
Embedded structural commands use `prepareCommand`; ordinary fields use `flush`.
Generic buffered controls accept an optional asynchronous `flush` before switching
between ordinary text and advanced JSON representations. A failed flush retains
the current mode and text; a successful switch reads the latest canonical value.

Valid field groups flush on blur and before structural commands, preview, Validate
or Save. Process patches sequentially, combining nonoverlapping groups; overlapping
ancestor/descendant edits must flush earlier groups before accepting the next one.
Block switching to root JSON mode until all valid groups flush; invalid fields
offer explicit discard or return to their controls. Root raw edits suspend ordinary
forms until parsing succeeds. No reducer merges conflicting raw JSON and field edits.

Tag requests with credential lifetime, source generation and base source. One patch
is in flight; further edits remain buffered. A confirmed patch may advance source
only from its exact base; clear only buffer generations included in that request.
Newer values survive. Late replies from replaced source/credential state are ignored.
Remove buffers for deleted objects only as part of the confirmed deletion. Failed
patches retain text and a visible retry/error state; no silent autosave occurs.

## Revision lifecycle

`DefinitionSession` accepts an optional opaque `sessionKey`. App supplies its
working-context key, retained across confirmed saves and changed for a genuine
open/import. Credentials still scope the private session lifetime. A promoted saved
reference must not remount or refetch that working context: if the incoming reference
matches its loaded promoted baseline, retain exact source, buffers and receipt.
Standalone callers without this key retain reference-scoped compatibility behavior.

Opening a saved revision retains its exact baseline and parent. Edits create an
in-memory working draft without overwriting that identity. On the first Save of a
dirty saved revision, allocate `r-` plus a fresh UUID hex label (opaque, not a version
number), then atomically patch graph_id/revision/derived_from in the current source.
Do not call the existing draft endpoint on the saved source after editing: that
would discard the edits. Existing imported/new drafts with unoccupied explicit
identities retain them; a collision explains Create new revision or Change identity.

Save flushes, locks edits, validates, freezes the exact submitted text and posts it.
Uncertain outcomes retain the same target/source for Retry; never allocate another
identity while recovery is outstanding. Confirmation promotes submitted source to
baseline and selects its exact reference. A failed collection refresh does not
restore the old source or lose the confirmed identity. The next edit branches from
that saved reference. No-op Save on a clean revision is disabled.

Create variant/Create draft from version use existing source/draft reads only after
the navigation guard resolves the old draft. Discard restores the active baseline.
Unknown-save Discard warns that the frozen revision may exist and leaves a visible
recovery reference; it must not mislabel the save as failed or delete server history.
Run remains blocked until the displayed source is the confirmed saved revision.

Debounce preview by 250 ms after a successful field flush/raw edit; cancel older
reads. While a valid preview is pending, label the graph Updating preview and allow
selection only for identities still present in the current canonical source; ordinary
field buffering must not prevent switching agents. Structural commands flush and
await a matching preview before using its relationships. Invalid source keeps
the last valid graph labeled Preview out of date, with selection/mutation commands
disabled there; the forms/source remain available for repair. Never present an old
saved graph as the current draft without this label. Draft preview invokes no hosts.

## Feature interfaces and presentation ownership

New experiment-library exports `ExperimentCollection` and `ExperimentVersions`.
Both accept credential and explicit refresh generation; Versions also accepts the
selected graphId/reference. Collection callbacks are `onOpen(reference)` and
`onCreate(templateReference)`, `onVariant(reference)` and `onImport(file): Promise<void>`;
Versions callbacks are `onInspectVersion(reference)`
and `onDerive(reference)`. They request navigation, never mutate the global draft.
App handles onInspectVersion as read-only historical inspection while retaining
its active draft; opening a collection item instead selects its editing context.
Versions owns compare selection and reads; app owns the active route.
App guards the existing draft before importing bounded exact source. It reads the
reference with the lossless source parser and supplies optional
`DefinitionEditorProps.initialSource`; the editor treats it as an unsaved imported
draft and never replaces it with a saved-source fetch. Its explicit identity is
retained until collision handling or an explicit identity change.

Workspace exports controlled `AgentInspector`, `ResourceInspector`, `FlowSettings`,
`ExperimentSettings` and `GraphCommandDialog`, retaining useful existing exports.
Selection props are structural records `{kind, id, nodeId?, port?}` scoped by the app;
`kind` is node, component, resource or connection. Activation/call selections are
adapted separately into evidence inspection, never authoring.
command props are `kind: add-agent | add-resource | delete`, selected ID and onClose.
Successful commands call the parent's patch once after flushing pending fields.
They obtain the post-flush source through `currentSource` before computing patches.

GraphView retains graph/detail/execution/onSelect and adds controlled selection,
presentation catalog, readOnly, previewCurrent and onAction. Action values are
add-agent, add-resource, delete; graph-view owns geometry/view toggles, not source
mutation. Connection selection carries exact relationship/route identity, not a
screen coordinate. App opens the relevant workspace editor. No React Flow objects
enter the semantic draft or public API. Unsupported graph shapes retain the generic
view and explicit unavailable editing controls.
Optional `previewSelectionAvailable` permits selection of surviving canonical
agent/resource identities during a valid preview update. App checks their IDs
against its latest parsed source and rejects obsolete connections until relationships
are current. Definition issues or invalid source disable this allowance. Structural
actions always require `previewCurrent`; buffered field generation alone does not
invalidate the already published exact-canonical-source graph.
For supported sequence/bounded-conditional relationships, `nodeId` is the matched
control edge's source and `port` its declared output-port label. Keep `id` opaque;
never split it to construct source pointers. App resolves missing fields against
the exact current preview edge, and workspace verifies that profile/node/port before
editing. Unsupported or missing relationships remain explicitly unavailable.

ExecutionPanel receives selected experiment/revision and the authoring availability
reason independently of the retained run ID. Its lifetime is not keyed to the draft
revision. Experiment history paging is distinct from live polling.
An optional `selectedRunId: string | null` selects an explicit URL/history run only
when it differs from the current store identity. `onRunSelect(runId)` reports
experiment-history selection to app navigation; `onInspect` remains the evidence
panel action. Keep the execution model mounted across contextual-section changes.
Accepted new-start/recovery receipts may also report their selected run through
`onRunSelect`, after authoritative matching run metadata confirms the current
experiment context. Unknown replies allocate no run identity for navigation;
ordinary polling must not independently rewrite the route. Late receipts from
another experiment retain execution recovery without relabeling that run's URL.
Inspector receives
exact run/activation/call selection and appears in the visible run detail panel;
it never scrolls the operator to a distant hidden editor. App manages panel placement.

C owns generic Panel, Dialog, ToolbarToggle and ExpandableTextArea controls, shared
tokens and responsive shell. Feature styles stay scoped. Dialog handles initial
focus, trap, Escape and return focus; a nonmodal inspector must not trap focus.
At narrow widths use the same editor state in a dedicated view, not duplicate forms.

## Authentication and metadata validation

API exports `observeAuthentication(credential, onInvalidated): () => void`.
App subscribes before protected reads. A transport 401/403 invalidates only the
credential lease captured when the request started, while that lease remains
current and the request is not aborted. Reconnecting, including with the same
credential, creates a fresh lease. Forced invalidation aborts protected work and
clears protected state without the voluntary-navigation draft guard. Provider
errors and ordinary retryable read failures do not invalidate authentication.
Credentials are neither persisted nor included in DOM events.

API exports `normalizedPresentation` as the single validator for descriptor UI
metadata. It accepts presentation/status/warning, resource slots, configuration
schema and optional schema documents; it returns validated presentation or null,
presentation status and a nullable warning. Saved descriptor metadata takes
precedence; absent historical metadata may use only the exact-version built-in
compatibility presentation. Current declared metadata cannot silently replace
metadata absent from an admitted historical snapshot.

## Delivery checkpoint — 2026-10-03

The owner-authorized S06 implementation and unchanged mandatory verification are
complete. The [current sprint report](../progress/sprint-06-status-report.md)
records acceptance evidence and preserved compatibility. Contract revision numbers
and runtime/accounting requirements are unchanged; owner usability review is separate.
