# S06-UX delivery preparation review

| Record | Value |
| --- | --- |
| ID / date | UX-S06-001-P01 / 2026-10-02 |
| Scope | Analysis, contracts and module tickets for the revised workspace |
| Baseline | `a844514`; existing audit/design notes retained |
| Method | M06; coordinator preparation, no implementers launched |
| Result | Documentation handoffs reviewed; application development and tests pending |

## Prepared delivery

[S06-UX](../../specification/s06-workspace-redesign.md) defines the whole correction
through delivery, four exclusive implementation assignments, 14 acceptance criteria
and test ownership. Four shared contracts define interaction, read/history APIs,
component presentation and frontend interface sketches. ADR 0013 records the
architectural tradeoff. Sixteen module directories have current responsibility,
specification and pending-task documents, including the new experiment-library
feature. Roadmap revision 4 is preserved; revision 5 records the open S06 correction.

The owner-selected account/credit placeholders remove real identity and billing
as blockers. Graph revisions, definition comparison and historical inspection are
functional scope. Paid execution, application implementation and database migration
were not performed during this preparation.

## Representative handoff walkthroughs

These are contract/source reviews, not executed tests or proof of usability.

| Case | Contract trace and result |
| --- | --- |
| Edit Reviewer and save | App selection carries node/component identity → workspace stages a pointer and exact value → definition-editor flushes through DefinitionClient.patch → static preview → fresh revision/parent patch → validate/save → confirmed source becomes baseline. No saved-source derivation discards edits. |
| Invalid numeric field or delayed patch | UI retains text/error → editor marks dirty immediately → pending generations survive replies → invalid fields block Save/Run, not same-experiment navigation. Valid preview updates do not freeze ordinary agent selection. |
| Lost save reply | Frozen identity/source stays in editor → Retry uses the same request → repository returns exact replay → original insertion time remains unchanged. No second revision, implicit run or duplicate charge is created. |
| Shared memory and contained worker | Descriptor slot/operations + presentation choose controls → actual resource reference and containment identify target → explicit grant action remains separate → graph projects configured consumers. No universal memory use or extra private copy is inferred. |
| Versions across pages and restore | Signed experiment-scoped window → real insertion ordering, nullable old dates → exact-source comparison → onInspectVersion opens read-only context → onDerive starts a new draft after guarding old edits. Runs keep admitted snapshots. |
| Older run while editing a newer graph | Separate app authoring/run lifetimes → experimentRuns lists all sessions → definition(run) selects admitted graph → resultSource retains response text → exact activation/call selection opens the visible evidence panel. |
| Unknown installed component | Catalog returns schema/slots and valid optional metadata or generic fallback → generic fields preserve unknown values → no type-name-specific behavior or additional execution capability is implied. |

## Gaps resolved during preparation

- Existing revision records lacked save timestamps: migration 8 records future
  insertions; old dates remain unavailable and ordering uses existing sequence.
- Collection and run screens could not be implemented by filtering one existing
  page: additive complete server-filtered read APIs now own that requirement.
- Presentation metadata cannot rewrite installed immutable descriptors: optional
  declared metadata and exact-version compatibility profiles cover both paths.
- Field buffers, save confirmation and current draft preview need one owner:
  definition-editor owns them; app owns selection and lifecycle composition.
- Historical inspection and editing need different callbacks: Versions explicitly
  requests read-only inspection or derivation, preserving the working draft.

## Verification boundary and next phase

Preparation verification passed: 506 local links across the 69 targeted Markdown
documents, four parsed JSON examples, the configured Markdown formatter and
`git diff --check`. No tracked non-document files changed. The pre-existing host
lockfile and audit evidence were left intact. Runtime interfaces remain sketches in the shared
contracts; development implements and type-checks them before private behavior.
No source-level compatibility, migration, browser or usability test is claimed yet.

Before launching implementation, the coordinator registers the planned feature's
source location and reviews the implemented public declarations against these
sketches. This is a bounded development setup task, not a new design question.
Whole-system review, test implementation, mandatory local verification and owner
demonstration remain separate phases under the delivery specification.

No additional owner product decision is required to implement this bounded design.
Credit/account semantics, nested graphs and automatic evaluation remain explicitly
deferred. The detailed ADR remains proposed until accepted; this preparation does
not claim authorization to deploy or publish the application.
