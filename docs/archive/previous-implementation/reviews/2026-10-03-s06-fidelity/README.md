# S06 visual fidelity correction

| Document control | Value |
| --- | --- |
| ID | S06-FIDELITY / 1 |
| Owner | Cesar Zea |
| Date | 2026-10-03, Europe/Lisbon |
| Status | Locally verified correction; owner usability acceptance pending |
| Authority | Owner rejected S06 and instructed continued delivery |

The [last reviewed concept](design-reference.png) is the visual reference. Later
[DR12–DR14](../2026-10-02-ui-usability/design-review-notes.md) supersede its large
credit figures, require explicit illustrative account presentation and add Versions.
The image is a reference for layout and hierarchy, not invented runtime data.

The owner rejected [report 0.0.6.3](../../progress/sprint-06-status-report-0.0.6.3.md).
The [rejected screenshot](rejected-checkpoint.jpg) preserves the actual starting UI.
Its passing technical checks remain valid historical evidence. They did not prove
visual fidelity or user acceptance. Observed defects include a large empty canvas
with small cards, excessive vertical inspector space, absent ordinary model controls
for historical resource metadata, undifferentiated actions and prominent opaque IDs.

## Complete correction and acceptance

- **F01 — Shell:** full-width workspace with a roughly 210–230 CSS pixel desktop
  rail. Brand belongs visually to the rail; collection back link precedes the
  experiment caption/name. Contextual navigation uses quiet icon/text rows and a
  soft selected state. Persistent Workspace settings, small credit bar/figures and
  explicitly illustrative account row remain at the bottom. Real operator access
  remains reachable and independent of the preview.
- **F02 — Header:** readable experiment name, short saved/unsaved status and clear
  Discard / primary Save revision / Run actions. Exact identities remain accessible
  in a details disclosure; uncertain-command recovery references stay immediately
  visible. Successful discovery must not insert a large refresh row above the title.
- **F03 — Graph:** a titled Collaboration panel with truthful counts; compact
  grouped editing/visibility/layout toolbar. Pressed states differ from actions.
  Desktop 1440×900 shows complete input, output and feedback routes and readable
  two-agent cards (at least 185 CSS pixels wide, preferably 210–260). Initial
  framing places collaboration in the upper/middle canvas rather than a small
  island below empty space. Explicit Arrange fits all content; polling preserves
  positions and user interaction. Resources attach to plain borders, never ports. A compact resources strip below
  the canvas identifies actual configured consumers and supports existing selection;
  model infrastructure stays abstracted from this visible collaboration layer.
- **F04 — Inspector:** selected agent name/type and concise context; instructions
  and model appear first without repeated component headings. At 1440×900 the
  compact prompt and model can both be seen without scrolling the inspector.
  Reasoning/output controls form a compact row where available. Response, configured
  components, connected resources and advanced controls use progressive disclosure;
  Add component and Connect resource remain discoverable. Unsupported empty settings
  use concise truthful capability information; stored incompatible values remain
  visible with explicit repair. Generic schema/JSON fallback remains available.
- **F05 — Lifetimes:** retain one canonical draft, flush/invalid buffers, exact
  numbers, frozen recovery, navigation guards, immutable saving/history, admitted
  run/evidence identities, explicit grants and current budget behavior.
- **F06 — Verification:** direct reference comparison plus actual 1440×900,
  1920×1080 and narrow 390×844 inspection; ordinary edit/save/version, structural
  configuration and saved run/evidence journeys. Add behavioral regressions only
  after combined source review, then pass unchanged `make verify` including
  existing coverage, source limits, boundaries, dead code and pinned CodeQL.

## Exact shared handoffs

Public inputs remain `GraphViewProps` in
[graph-view/types.ts](../../../../../frontend/src/features/graph-view/types.ts),
`ControlledWorkspaceProps` / `ComponentFormProps` in
[workspace/types.ts](../../../../../frontend/src/features/workspace/types.ts), and
[workspace frontend interfaces](../../contracts/workspace-frontend-interfaces.md).
No public prop removal, sibling-private import or new service/API is authorized.

`ToolbarToggleProps` gains optional `children: ReactNode` and `className: string`.
The existing `label` remains the accessible name; children provide short visible
text/icon. Default behavior remains the label when children are absent. Native
button `aria-pressed`, disabled state and callbacks retain their meanings.

Workspace supplies semantic classes `.agent-overview`, `.inspector-section`,
`.model-grid`, `.generation-grid`, `.component-list`, `.connected-resource-list`,
`.inspector-advanced`, `.capability-note`. App owns their shared styling. Graph owns
its own toolbar/canvas/card styles; App owns outer panel/inspector dimensions.
Existing aria labels and command eligibility remain stable where semantics do not
change. Icons must be decorative and have accessible text/button names.

Representative source is the actual
[bounded-review definition](../../contracts/examples/bounded-review.graph.json):
`/nodes/review/component = reviewer`; `/components/reviewer/resources/worker =
review-worker`; resolved instructions come from
`/components/review-worker/config/instructions`; model binding comes from
`/components/review-worker/resources/model`. Proposer binds `proposer-model`.
A normalized descriptor declares `model_slot`, `provider_profile_pointer` and
`model_pointer`. The coordinator adds an exact-version compatibility profile for
`example.model-resource@0.1.0-example`, whose unchanged descriptor declares
`/provider_profile` and `/model`. This is data-side compatibility, not client
inference from a type name. Profile choices originate in `ConfigurationCatalog.models`;
all current model/temperature confirmation and repair rules remain authoritative.
Missing metadata still exposes generic bound-resource configuration under Model
instead of silently dropping it. No provider/model inference or undocumented defaults.

Configured agent names come from `/extensions/slow-thinker:display/nodes/<nodeId>/name`,
then `/extensions/slow-thinker:display/components/<componentId>/name`, then the exact
instance ID. Declared presentation display_name identifies type, not instance.
Do not infer a configured name from an opaque ID.

Data and errors come from the existing catalog, canonical source/field buffers,
DefinitionClient and retained ExecutionPanel observations. Invalid metadata, unknown
model profiles, shared workers, blocked commands, pending previews and uncertain
saves retain their established fallback/repair states. No account API, paid call,
new spending allowance or destructive source migration is included.

## Exclusive delivery ownership and phases

| Owner | Complete owned packages | Verification ownership |
| --- | --- | --- |
| C — Shell | frontend/src/app and frontend/src/ui | App/UI tests and all browser journeys/shared harness |
| B — Inspector | frontend/src/features/workspace | Workspace feature tests |
| D — Graph | frontend/src/features/graph-view | Graph feature tests |
| Coordinator | Shared contracts/docs, exact compatibility metadata | Compatibility regression, composition review and unchanged runner |

Source phase first; deliver code/acceptance mapping and local choices, no functional
test changes yet. Static checks may establish source form. Review all three deliveries
and the actual whole UI; group necessary corrections. Only then release scoped test
tickets. Shared fixtures have one owner (C). Test files remain exclusively assigned
by package/function. No overlap or unrelated refactor. Scope does not activate S07.

### Ownership cutoff — 2026-10-03

The shell assignment encountered two model-capacity failures after writing its
source. At the explicit cutoff, the coordinator took the complete app/UI assignment
and its test/harness ownership, preserving those files. B and D remain unchanged;
no simultaneous app/UI writer is authorized. This is an operational reassignment,
not a change to M06 or the delivery scope.

## Verified delivery checkpoint — 2026-10-03

The correction passes the unchanged complete `make verify`, confirmed at 03:46:19
UTC: 2,280 Python tests, 791 frontend tests and 34 browser journeys, with all
independent coverage and strict static/security gates retained. Source review
preceded the independent test assignments. Actual inspection covers measured CSS
viewports 1440×900, 1920×1080 and 390×844 without document horizontal overflow.
The native disclosure's three Refresh consumers required test setup corrections;
their original security/conflict assertions remain unchanged.

[Report 0.0.6.4](../../progress/sprint-06-status-report.md) maps F01–F06 to evidence.
The [sanitized record](../../evidence/s06-fidelity-verification-20261003.json)
retains full verification, actual demonstration identities and image digests.
Compare the reviewed concept above with actual [1440 desktop](corrected-desktop-1440.jpg),
[1920 desktop](corrected-desktop-1920.jpg), [narrow inspector](corrected-mobile-390.jpg)
and [narrow graph](corrected-mobile-graph-390.jpg). Narrow graph framing used explicit
Arrange after changing viewport; user interaction is otherwise preserved.
Owner acceptance and publication remain separate and pending.

## Inspector review follow-up — 2026-10-03

**Status: open review finding; the following proposal is not yet approved.**
English summary of the owner's Spanish review comment: the selected-agent panel
is confusing; Agent instructions may be clearer as Prompt, and that section should
support collapsing consistently with Model and the other groups.

Proposed correction: use one consistent visual pattern for independently collapsible
Prompt, Model, Response, Components, Connected resources and Advanced sections.
Prompt and Model start open, preserving immediate access to both; other sections
start closed. Use compact truthful summaries when closed and show component/resource
counts with their add/connect actions on the section header. Remove redundant visible
instruction labels and move ordinary technical instance identifiers to Advanced.
Keep the prompt's expansion icon inside its editor. Reduce nested visual containers;
schema details remain progressively disclosed rather than exposed by default.

Collapsing must preserve the canonical draft and pending/invalid buffers. Closed
sections must signal validation or compatibility issues without concealing the
stored values or repair controls. Generic extension presentation and exact JSON
remain available. This note does not change implementation, approve new behavior
or establish owner acceptance.

## Repeated-review flow review — 2026-10-03

**Status: open review findings; corrective behavior has not been approved.**
English summary of the owner's Spanish question: does Proposer contain a component
that supplies its apparent two outputs, and where is that configured?

The exact `repeated-review / example-2` definition uses an ordinary LLMCall Proposer
without contained components. Its fixed sequence is draft, review-1, revise-1,
review-2, revise-2, declared in `/components/sequence/config/steps`. There is no
conditional redirector or two-port decision in this Proposer.

Actual browser inspection found two usability defects. Cards are positioned in
structure enumeration order (draft, review-1, review-2, revise-1, revise-2), which
differs from execution order. The review-2 to revise-2 edge passes behind the
revise-1 card and looks like a second output; revise-1's actual output is the curved
edge to review-2. Repeated visits also share ordinary agent labels. The Experiment
settings page reports ordinary flow controls unavailable for this historical
example because its source has no explicit supported execution_profile. The sequence
is presently inspectable through Advanced definition and validation, not ordinary
flow controls. The inspector correctly reports no internal components.

Proposed corrections for review: frame supported sequences in their actual execution
order and prevent unrelated routes from crossing cards; expose the validated
sequence configuration for compatible historical examples without inventing routing,
changing exact source implicitly or inferring extension semantics from type names.
These findings qualify usability readiness; prior technical checks are retained
as checkpoint evidence and do not establish owner acceptance.

## Collection, navigation and routing follow-up — 2026-10-03

**Status: open owner review; no corrective implementation is authorized by this note.**
English summary of the owner's Spanish observations: the experiment collection
does not resemble the proposed images; Resources and Run tabs are not visible
within the experiment; the owner asks whether Redirector should be used inside
the repeated-review Proposer.

Actual collection inspection shows tall list cards with repeated experiment IDs,
prominent opaque revision IDs, verbose search guidance and a native file-upload
control. This is insufficiently refined for ordinary product use. The retained
visual reference covers the experiment workspace, not a separate collection
screen; it cannot establish collection fidelity. The previous fidelity correction
concentrated on the workspace and did not adequately review the collection.

Resources and Runs are implemented as experiment-scoped sidebar destinations,
alongside Design and Versions, rather than horizontal tabs. The retained final
concept and navigation contract both use this sidebar arrangement. Record the
owner's discoverability concern without reporting the destinations as absent or
silently introducing a second navigation scheme.

Redirector is the existing deterministic routing component, usable separately
or through composition. The historical repeated-review example has a fixed
two-review sequence and no conditional decision. The bounded-review example
implements the requested acceptance loop: Reviewer is a RoutedCall containing
an LLMCall worker and Redirector; accept finishes and revise returns to Proposer.
Proposer has one output in that example. Other user-defined agents may compose
a Redirector when their own behavior requires multiple exits.

Proposed follow-up: present a compact experiment collection with readable names,
descriptions and collaboration summaries; disclose exact technical identities
progressively. Label fixed-sequence and conditional-review examples clearly and
make experiment navigation discoverable. Preserve the exact legacy definitions;
changing repeated-review into a conditional loop would be a separate agreed
configuration change. Owner usability acceptance remains pending.

## Design-page technical disclosures follow-up — 2026-10-03

**Status: open owner review; relocation proposals are not yet approved.**
English summary of the owner's Spanish observation: Explore graph and evidence
and Advanced definition and validation remain below the graph/resource summary,
although their placement is inconsistent with the reviewed product design.

Source inspection confirms that GraphView always appends a technical graph list,
including resources, components, steps, control connections and any supplied
execution evidence. DesignPage additionally appends the definition editor as a
separate disclosure. These preserve useful capabilities, but retaining the old
panels below the new workspace is an incomplete product adaptation. Collapsing
them does not resolve their scope, duplication or placement.

Proposed correction: make an accessible graph-list view an explicit graph-toolbar
option, separate from execution evidence, which belongs to the selected run in
Runs. Expose exact definition editing through a clearly labeled advanced action
and focused editor using the existing canonical draft. Keep normal validation
with fields and Save revision; retain detailed diagnostics where relevant. Do
not remove keyboard access, generic extension configuration or exact-source
recovery. The reviewed compact resource summary remains below the canvas and
identifies configured consumers, with detailed management in Resources.

This note records the product correction needed; it does not change application
behavior, establish owner acceptance or authorize removal of existing capabilities.
