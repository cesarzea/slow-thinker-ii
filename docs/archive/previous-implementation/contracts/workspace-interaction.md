# Workspace interaction contract

## Current completion amendment — 2026-10-03

The owner authorized [whole-interface completion](../specification/s06-ui-completion.md).
U01–U10 supersede incompatible placement/presentation clauses below. Design no
longer appends technical graph/evidence or definition panels. Exact definition
editing opens from an explicit action; graph-list access belongs to the toolbar
and recorded activity to Runs. Standard validation remains visible in the normal
save workflow. All canonical draft, authorization and recovery contracts remain.
Absent execution_profile for schema_version 0.1-draft means sequence, matching
the existing backend GraphRecord contract without changing stored source.

**S06-UX-INTERACTION / revision 1 / 2026-10-02.** Owner-authorized implementation; locally verified. Governing scope: [S06-UX](../specification/s06-workspace-redesign.md).

## Navigation and scopes

The collection has Experiments, Component library and Workspace settings. Opening
an experiment replaces the contextual navigation with its name, **All experiments**,
Design, Resources, Versions, Runs and Experiment settings. Do not mark Experiments
selected while showing its detail. Global Workspace settings remains at the bottom
left above the explicitly illustrative account and credit footer.

Use browser history/hash routes for navigable identities, not for credentials,
prompts or task input: `#/experiments`, `#/components`, `#/workspace-settings`, and
`#/experiments/<encoded graph_id>/<section>`. Optional `revision` and `run` query
values are encoded exact opaque identities. Unsupported sections/identities show a
recoverable unavailable state. Back/Forward uses the same draft guard as clicks.

Experiment settings edits the current draft's name, description, task-input schema
and existing profile-specific configuration. Workspace settings edits only the
existing effective limits and shows available model profiles. Explain that these
limits apply to new runs across experiments; credentials and provider installation
remain outside this UI. Component library describes installed types and versions;
Resources lists instances belonging to the selected experiment, not a global pool.

Navigation within an experiment preserves the active draft and editor buffers.
Leaving an experiment with changes offers Save, Discard or Cancel; invalid fields
disable Save with an explanation. Browser unload warns when unsaved; no durable
browser storage of source, prompts or credentials. Disconnect confirms discarding
pending edits, clears protected state and aborts reads. Forced credential invalidation
clears protected state immediately. Operator access remains real and separate from
the decorative account preview. No multi-experiment draft cache is required.

## Design workspace

Use the available width. At desktop sizes, keep the graph and selected inspector
adjacent with separate scrolling. At narrow sizes, selection opens a full-width
editor with a clear Back to graph action. Collapsing navigation must retain access
to global settings. Document scrolling must not be necessary to discover selection.

The header shows experiment name, exact base revision, draft/unsaved status, Discard,
Save revision and Run. Run opens setup for the saved selected revision; it never
saves implicitly. Disabled actions explain dirty, invalid, pending or unavailable
state. Existing active-run Stop/recovery controls remain usable when authoring is
blocked. The execution profile still permits only its supported active workflow.

The graph toolbar contains Add agent, Add resource, Delete, Configuration, Resources,
System, Arrange and a labeled overflow menu. Visibility controls are native buttons
with `aria-pressed`; editing actions are not toggles. Configuration, Resources and
System start off to preserve the agent-focused default. The preview image showing
Resources on illustrates a selectable state. Preserve choices within the session.

Agent cards identify component type and configured name on separate lines; internal
IDs remain in details. An AI icon requires declared agent/presentation semantics;
unknown extensions use a generic icon. Execution ports stay visible. Entry/terminal
arrows end in empty space. No controller, model registry or output box is added.

Resources on shows one card per bound resource instance with dashed, non-directional
binding lines touching plain agent borders, never execution circles. List bindings
through contained children with the actual child/slot identified. Ignore unrelated
resources until explicitly selected from Resources; model configuration stays on
the agent card and inspector. Highlight only configured consumers, not presumed
runtime use. System markers retain the existing noninteractive black-circle model;
future marker evidence navigation is not invented for this delivery.

Preserve positions/viewport for the same working graph during edits and polling.
Place new cards in free space; do not reorganize existing cards automatically unless
overlap cannot be resolved locally. Arrange explicitly recomputes layout. Geometry
and view settings remain outside semantic graph revisions.

## Selection and configuration

App owns selection by exact graph context and planned step, component, resource or
connection identity. Agent selection exposes the selected component's configuration,
declared internal components and connected resources. Primary-child metadata may
bring a worker's prompt/model into the parent inspector, with the actual edited
component identified. Warn when the same instance affects more than one step.

Instructions are the configured prompt portion, not an assertion that all prior
messages are supplied. Place the expand icon inside the textarea's upper corner,
with an accessible label and hit area. Expanded editing is a modal using the same
buffer, Escape/focus restoration and internal scrolling; closing does not discard.

Use [presentation metadata](component-presentation.md) and schemas, not universal
Tools & memory/Routing sections or type-name heuristics. Configured components are
listed first. Add component selects an available declared slot, a compatible type
and its configuration; Connect resource selects an existing compatible instance.
Neither action injects context, duplicates shared state nor grants permissions.
Show required operations and let the user explicitly confirm any permission edits.

Model changes show incompatible current settings and offer explicit removal/reset
before applying a coherent patch. Existing unsupported values remain visible and
removable; disabled controls must never trap a stale temperature/reasoning value.
Unknown schema constructs retain Advanced JSON value editing without data loss.

## Editing commands and validation

All fields use the shared draft lifecycle in [the public interfaces](workspace-frontend-interfaces.md).
No per-field Apply is required. Structural dialogs stage changes until explicit
confirmation; Cancel leaves source untouched. Add agent creates the selected
instance, step, required mappings and profile placement as one patch. Offer only
declared operations; absent schema defaults require input, not fabricated values.
Incomplete existing advanced drafts remain editable, but cannot be saved/run.

Connections opens from a route or Design's flow settings. Sequence exposes ordering
and valid earlier-output mappings; it does not offer conditional routes or an
ineffective final-result selector. Bounded-conditional exposes entry, named exits,
feedback, activation limit, Finish and result source under the existing contract.
Preserve optional feedback/missing-value fields unless deliberately changed.
Task inputs uses ordinary labeled schema fields; technical paths remain in details.

Delete first lists every affected node, route, mapping, binding, containment and
permission. Node deletion is distinct from deleting its reused component. Retain
unreferenced resources by default. Known references must be repaired in the same
confirmed operation; otherwise block deletion and link to the affected fields.
Do not guess references inside opaque extension values; explain that limit and
require normal validation. Arbitrary extension semantics remain their author's
responsibility. Never silently delete unrelated components or broad permissions.

## Versions, runs and footer

Versions lists saved revisions with exact labels, real save metadata and lineage;
missing dates are Unavailable, bundled definitions are Templates. A draft is marked
separately, not inserted as a saved history entry. Read-only historical inspection
cannot edit the active draft. Compare two exact references, defaulting to an
available parent; explain cross-experiment lineage. Restore is **Create draft from
this version**, producing a new revision when saved, never overwriting history.
Definition differences cover configuration, components, nodes, connections, grants
and metadata; this is not a comparison of quality or execution results.

Runs defaults to all revisions/sessions of this experiment, with optional exact
revision filtering. New-run setup includes real session selection, task inputs and
effective budgets/deadlines. Saved-run detail uses only its admitted graph; a
selected node offers its recorded activations instead of silently choosing the last.
Final results, intermediate outputs, failures and unavailable content are distinct.
Exact raw result text must not be reconstructed through JavaScript numbers.

Footer: a static illustrative bar and small readable figures under it, labeled
Demo credits; account identity labeled Account preview. Menu items explain Not yet
available and perform no account/billing actions. Do not change illustrative credits
on actual runs. Actual USD spending/reservations remain in Runs/Workspace settings.
The fake identity is never a version author or an authentication state.

Empty, loading, invalid, unavailable, stale, pending and uncertain states require
specific explanations and recovery actions. All authored text is English; preserve
user content. Keyboard alternatives, visible focus, labeled controls and text cues
accompany icons/colors. No tooltip-only action or status is sufficient.

## Delivery checkpoint — 2026-10-03

The owner-authorized S06 implementation and unchanged mandatory verification are
complete. The [current sprint report](../progress/sprint-06-status-report.md)
records acceptance evidence and preserved compatibility. Contract revision numbers
and runtime/accounting requirements are unchanged; owner usability review is separate.
