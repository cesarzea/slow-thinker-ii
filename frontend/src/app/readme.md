# Browser application composition

Composes access, graph selection, execution and inspection into one local operator workspace.

Use the [public entry point](app.tsx); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

Product-authored interface text and accessible labels are English. User content and saved evidence retain their original language.

Connected operators select an exact graph ID and revision from the paged personal
and bundled library. Refresh starts a fresh listing; Load more continues its fixed
window. Viewer access keeps the bundled catalogue. A confirmed save searches a new
listing for its exact revision, retains its identity if listing fails and offers
selection recovery. An explicit selection cancels that search.

The app composes the JSON editor, saved-definition canvas and execution through
public feature entry points. Dirty drafts and unresolved save selection disable
Start with an explanation. Existing run controls, live evidence and retained-run
inspection keep their independent saved identities. Credential changes reset the
library/editor workspace and abort stale requests.

The [catalog tests](../../tests/catalog-model.test.ts) and companion recovery tests
cover bounded fixed-page navigation, saved lookup and superseding requests.
[App tests](../../tests/app-authoring.test.tsx) and companion paging tests cover
dirty Start gating, confirmed identity recovery and retained run evidence.
The [authoring journey](../../tests/journeys/personal-authoring.spec.ts) and
[exact-identity journey](../../tests/journeys/personal-identity.spec.ts) verify
production HTTP/storage composition and saved-run inspection. The browser fixture
executes deterministic operations; it does not establish provider behavior.

## S04–S06 workspace

The workspace has Experiments, Components, Resources, Runs and Settings pages.
Page navigation keeps draft/run/settings state mounted; credential changes remount
protected state. DefinitionSession shares one source with structured forms and JSON.
Runs retain their independent admitted definition. Optional evidence opens a visible
technical drawer. Execution stays outside the revision-keyed source session so
selecting another experiment preserves the admitted run and its result. Runs
shows exact source-read errors and dirty/pending Start reasons.

The [navigation tests](../../tests/app-navigation.test.tsx) cover keyboard page
selection and retained draft/settings buffers. The
[workspace authoring journey](../../tests/journeys/workspace-authoring.spec.ts)
verifies production discovery, raw numeric patch preservation and personal
collaboration history. Settings and disconnect journeys verify server ceilings,
exact uncertain replay, stale revision recovery and protected-state clearing.
Responsive journeys retain actual canvas geometry and page-width assertions.
Shared verification is recorded in [verification record](../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02).

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
