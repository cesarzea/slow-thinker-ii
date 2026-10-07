# S06 — Complete product interface

| Document control | Value                                                                                |
| ---------------- | ------------------------------------------------------------------------------------ |
| ID               | S06-UI-COMPLETE / 1                                                                  |
| Date / owner     | 2026-10-03 / Cesar Zea                                                               |
| Status           | Locally verified; owner usability acceptance pending                                 |
| Authority        | Owner instructed completion of the entire interface for the implemented architecture |
| Method           | M06: complete preparation, parallel packages, combined review, testing               |

## Delivery boundary

The owner rejected the preceding partial product adaptation. Earlier passing
checks remain historical evidence, not current completion or usability acceptance.
Complete every existing product destination and its ordinary workflows, including
agent composition. Preserve backend/runtime features, exact source and all guards.
No new graph execution profile, hosted account, credits economy, arbitrary code
installation, evaluation engine, paid call or publication is introduced here.
The reviewed final concept in ../reviews/2026-10-03-s06-fidelity/design-reference.png
governs the workspace hierarchy, with DR12–DR14 and subsequent owner corrections.
The collection has no retained approved screenshot; use the same visual language
and explicit acceptance criteria rather than claim an unverified image match.

## Complete acceptance matrix

- **U01 Collection/access:** compact readable experiment rows with name, available
  description, participant/version counts and truthful template/save state.
  Search and primary Create from template / Import actions share a compact header.
  Exact IDs and missing historical metadata belong in details, not repetitive prose.
  Preserve complete server search/paging, import validation, empty/loading/error
  states, guarded navigation and template/variant actions. Disconnected access is
  a clear entry screen; do not display failed protected-library loads as its default.
- **U02 Shell/navigation:** one experiment-scoped sidebar with Design, Resources,
  Versions, Runs and Experiment settings; All experiments returns to collection.
  Workspace settings/account preview remain separate. Consistent page headings,
  readable current context and save/dirty/validation feedback. Full browser width;
  desktop split graph/inspector and narrow-screen Back to graph. Do not add a
  competing set of horizontal tabs. Keep user edits across every in-experiment page.
- **U03 Design/advanced:** remove both appended technical disclosures from Design.
  A plainly labeled Edit definition action opens a focused dialog for exact JSON
  and import/validation/recovery, sharing the canonical draft. Normal Save validates
  and shows actionable issues; detailed diagnostics remain available. A toolbar
  Graph list view offers keyboard-accessible structural selection. Recorded
  activity is available only in execution context as Run activity, not Design.
  Keep the compact connected-resource strip from the reference; management is in Resources.
- **U04 Graph clarity:** agent type/name/icon and visible entry/output handles,
  faithful routes, readable initial framing, no unrelated line through a card.
  Derive order from actual declared control relationships, not alphabetic source
  enumeration. Wrap long sequences into readable rows rather than shrink to dots.
  Distinguish repeated steps without pretending they are independent components;
  show a discreet step label for reused agents. Respect explicit Arrange and saved
  user geometry during edits/polling. Resource links attach to plain borders.
- **U05 Inspector:** consistent independently collapsible Prompt, Model, Response,
  Components, Connected resources and Advanced sections. Prompt/Model initially
  open, other sections initially closed with truthful summaries/counts. Add/connect
  actions remain discoverable. Prompt expansion stays inside the editor. Preserve
  invalid buffers across collapse and show Needs attention on closed affected groups.
  Ordinary controls avoid redundant IDs, nested boxes and empty schema editors.
  Shared-instance effects, missing capabilities and native-value repair stay explicit.
- **U06 Composition:** the actual bounded-review Reviewer uses RoutedCall with
  LLMCall worker and Redirector children. Show both children, their type/role and
  editable configuration. Router output names and installed routing-function
  reference must be understandable; it deterministically selects accept or revise.
  The parent follows declared slots, not frontend type-name inference. Add compatible
  component and existing resource bindings retain explicit permission controls.
  Demonstrate nested calls through the orchestrator, not merely containment drawing.
  Ordinary LLMCall has no invented component slots; fixed repeated-review remains
  a sequence and is clearly distinguished from conditional review.
- **U07 Resources/components/settings:** Resources has a coherent list/detail
  layout, names/types, actual consumers, add/select/configure paths and empty state.
  Contained children are identifiable as internal, shared bindings as shared.
  Component library describes available reusable types/versions, operations and
  composition points using declared metadata, with technical details progressive.
  Experiment settings groups identity, task inputs and flow. Workspace settings
  groups configured models and real budgets/deadlines with units and scope.
  Preserve server ceilings, explicit grants and honest unsupported states.
- **U08 Versions:** readable immutable history, revision notes, actual dates/lineage,
  selection, comparison and create draft from historical version. Compact identities
  retain exact inspectable value. Never invent chronological sequence or authors.
- **U09 Runs/evidence:** clear experiment Runs heading, new-run setup, session,
  task, budgets, history, selected-run status/result and activity. Place result and
  activity near selected run; inspect calls/content without scrolling through a
  distant technical dump. Raw events/payloads are deliberate details. All histories
  and live graph/evidence use the admitted revision; stop and uncertain recovery
  remain usable independently of authoring. Show unavailable/truncated/error states.
- **U10 Verification/truthfulness:** actual browser journeys cover every destination,
  ordinary edit/save/version/run, child configuration and routing, resource sharing,
  errors and keyboard/narrow layouts. Existing fake operator/account fixtures are
  identified as demonstrations. UI simulation proves UI only. Installed process/MCP
  tests independently prove nested worker/router execution with local test upstream.
  Paid-provider evidence is neither fabricated nor implied. Pass unchanged make verify,
  all strict coverage/static/security rules and configured installed checks.

## Exact contracts and shared decisions

Public module entry points remain unchanged unless the coordinator records an
amendment. App owns canonical EditorModel and maps feature callbacks. Graph uses
GraphViewProps/GraphSelection from graph-view/types.ts; toolbar list/activity can
be module-private state. App opens its source editor with the existing ui Dialog
and DefinitionEditorView; do not mount a second independent EditorModel.
Workspace consumes ControlledWorkspaceProps; source, fields and callback meanings
remain in workspace-frontend-interfaces.md. Never parse exact numeric source
through JSON.parse/stringify. Feature-to-feature imports remain forbidden.

Approved implementation amendment, 2026-10-03: ExecutionPanelProps adds optional
readonly children?: ReactNode as a full-width presentation slot immediately after
the result/setup columns and before history. App passes its admitted-run graph and
inspector composition. No observation state or mounting lifetime is duplicated;
execution does not import other features. Owner A supplies the children; owner C
declares and renders the slot. This groups run result, graph and evidence before
history while retaining the width needed for graph and inspector, without
cross-module CSS or a new public data contract.

Canonical graph contract: schema_version 0.1-draft, GraphRecord.execution_profile
in backend/adapters/catalog/_models.py defaults to sequence when absent. The UI
must apply this exact schema-version default consistently to flow editing, add/
delete placement and mappings, without patching the source or inferring from
type_id. Explicit unsupported/invalid profiles remain unavailable. Graph layout
uses structural control edges and nodes supplied by the validated API.

Representative composition is docs/contracts/examples/bounded-review.graph.json:
review node -> reviewer; reviewer.resources.worker -> review-worker;
reviewer.resources.router -> review-router; both children contained_by reviewer.
Review-worker is ordinary llm-call. Router config.outputs is [accept, revise],
selector is example_grounded_review:choose; parent extracts worker /value.
Review route accept ends, revise returns to propose. Proposer has one next exit.
The exact RoutedCall compatibility profile places both worker and router under
Components; runtime resource roles and explicit operation permissions are unchanged.
The actual source, catalog schemas and component-presentation contract, not example
identifiers, drive controls for arbitrary instances. Coordinator may add JSON Schema
titles/descriptions to descriptors; generic UI should honor those annotations.
Test inputs and observations must distinguish this from fixed repeated-review.

Collection/history wire inputs stay ExperimentSummary, SavedVersion and
DefinitionDifference in api/workspace-history-schemas.ts. Details/ref/notes are
actual data; absent descriptions stay absent. Existing IDs are not rewritten.
New showcase metadata belongs to a new saved draft/revision, never silently to
an old immutable source. Preserve exact unknown extension fields.

## Exclusive packages and phase handoff

| Owner           | Whole assigned modules                                          | Tests when released                                             |
| --------------- | --------------------------------------------------------------- | --------------------------------------------------------------- |
| A Product       | app, ui, definition-editor, experiment-library                  | Their unit tests; all browser journeys/shared harness           |
| B Configuration | features/workspace                                              | workspace unit tests                                            |
| C Observation   | features/graph-view, features/execution, features/inspector     | graph/execution/inspector unit tests                            |
| Coordinator     | API only if needed, backend/descriptors, docs, demo preparation | Backend/contract regressions and unchanged whole-project runner |

A owns app/ui CSS and only outer inspector geometry; B owns workspace-private
content styling; C owns graph/execution/inspector-private styling. Do not edit
another owner's files. Existing code and fixtures remain the baseline. Every
owner reads relevant local specification/todo and exact public dependencies.
Only source implementation and static checks are released initially. Deliver an
acceptance-to-code map and unresolved issues. The coordinator reviews individual
deliveries together and actual whole product, then releases grouped corrections.
Functional test implementation follows combined source review. A owns shared
fixtures and first representative browser composition; only then expand scoped
tests in parallel. No repeated broad runs before coordinated readiness.

## Completion record

Source assignments, combined review, corrections and verification are complete.
The unchanged full runner passes: 2,280 Python tests, 868 frontend tests and
39 browser journeys. All 20 installed-component checks also pass. The actual
demonstration records nested worker/Redirector calls. Desktop and measured
390-pixel evidence is retained in the
[whole-interface review](../reviews/2026-10-03-s06-completion/README.md), with
[verification results](../evidence/s06-ui-completion-verification-20261003.json).
Owner usability acceptance and publication remain separate and pending.
