# Findings — UX-S06-001

Read the [review scope and priorities](README.md) before interpreting these findings.
Locations refer to baseline `a844514`; user consequences are assessments unless
explicitly described as observed. Proposed corrections are not approved changes.

## Selection, layout and editing

### UX01 — Canvas selection and editing selection disagree · P1

**Observed:** selecting Reviewer displays `node: review` and raw component/input/
operation JSON. The Agent selector remains `proposer`. Graph clicks therefore do
not select the agent being edited. The inspector also shows “No activations in the
visible snapshot” while designing an experiment, where runtime activity is irrelevant.

**Consequence:** a user can reasonably believe a change affects Reviewer while
editing Proposer. Technical step IDs replace the name used on the graph.
**Correction:** share selection across canvas, inspector and forms; show the agent
name and step context, with raw configuration behind an explicit advanced action.
Show activation information only in a run context.

**Source:** [graph selection](../../../../../frontend/src/app/graph-workspace.tsx#L29),
[raw object summary](../../../../../frontend/src/app/object-summary.tsx#L12),
[separate agent selection](../../../../../frontend/src/features/workspace/agents/editor.tsx#L18).

### UX02 — Essential editing is far below the graph · P2

**Observed:** at a 1,367 × 1,815 CSS-pixel viewport, the selected Reviewer page was
5,681 pixels tall. The graph section started at y=780, the JSON summary at y=1,527,
and the Agents section at y=2,209; that section alone occupied about 3,408 pixels.
These are one recorded layout, not responsive benchmarks. The screenshot and
[evidence record](evidence.json) retain the observation.

The prominent revision-creation form, graph, resources, raw selection and editor
are stacked. The user cannot readily keep the selected agent and its settings in
view. **Correction:** prioritize the graph plus nearby selected-object editor,
use short purposeful sections, and keep save/status context visible. Put revision
creation in the editing journey rather than permanently ahead of the graph.

**Source:** [authoring composition](../../../../../frontend/src/app/authoring-workspace.tsx#L43),
[agent editor composition](../../../../../frontend/src/features/workspace/agents/editor.tsx#L18).

### UX03 — Visible field edits are missing from pending-change status · P1

**Source-confirmed:** scalar inputs hold local text until “Apply …”; the global
dirty flag compares source and baseline. A changed visible prompt can therefore
coexist with “No unsaved changes”. Validation consumes the applied draft source.
Execution readiness checks its dirty state; execution uses the selected saved
revision. Neither includes unapplied field buffers. This failure path was not
exercised by changing live data.

**Consequence:** Save/Run can appear to include a visible change that has not been
applied. Different controls also commit differently: some selectors/checkboxes
patch immediately while scalar fields require Apply. **Correction:** track all
pending edits, including invalid/incomplete text, in one model; clearly associate
errors and pending state with the selected object. A single save action must include
valid pending changes or explain why it cannot. Preserve exact source patching.

**Source:** [scalar buffer](../../../../../frontend/src/ui/schema-values/scalar.tsx#L10),
[dirty calculation](../../../../../frontend/src/features/definition-editor/use-editor.ts#L22),
[run readiness](../../../../../frontend/src/app/use-readiness.ts#L20).

### UX04 — Navigation can discard work without warning · P1

**Source-confirmed:** changing experiment/revision remounts the authoring session.
Changing Agent or Node remounts keyed local editors. Pending field values can be
lost on agent/node changes; an applied draft can be lost on experiment changes.
Discard and import replace source without a dirty-work review. Primary section
navigation does preserve mounted state; the problem is not every navigation action.

**Correction:** retain drafts by identity, or intercept transitions that discard
work with concrete Keep editing/Discard choices. Import should preview replacement.
Discard must reset field buffers as well as source. Treat an uncertain save
separately: its server-side outcome may already exist.

**Source:** [experiment selection](../../../../../frontend/src/app/experiment-panel.tsx#L18),
[keyed session](../../../../../frontend/src/features/definition-editor/definition-session.tsx#L12),
[agent key](../../../../../frontend/src/features/workspace/agents/editor.tsx#L27),
[node key](../../../../../frontend/src/features/workspace/node-editor.tsx#L24),
[discard/import](../../../../../frontend/src/features/definition-editor/edit-actions.ts#L28).

### UX05 — Natural select → edit → save can lead to an identity conflict · P1

**Source-confirmed:** saved definitions expose enabled editing fields. Applying a
change makes the draft dirty and disables “New revision or variant”. The identity
remains the existing immutable revision; saving changed content under it conflicts.
The resulting “definition conflict” does not explain how to preserve the work.

**Correction:** make saved versus draft mode explicit and offer “Edit as new revision”
before editing, or support a non-destructive Save as new revision flow after editing.
Keep immutable storage. Use a readable proposed revision name; show technical IDs
secondarily. This is an interaction correction, not permission to overwrite history.

**Source:** [editing lock](../../../../../frontend/src/features/definition-editor/draft.ts#L27),
[revision form disabled by dirty](../../../../../frontend/src/features/definition-editor/revision-draft.tsx#L18),
[immutable conflict](../../../../../backend/src/slow_thinker_ii/application/library/_service.py#L59),
[error text](../../../../../frontend/src/api/definition-errors.ts#L13).

### UX06 — Controls do not respect the execution profile · P1

**Observed:** the sequence example offers Output port, Optional feedback in mapping
forms, and Final result with `review /value`. **Source-confirmed:** sequence nodes
reject output selectors and bindings containing `activation` or `missing`.
Nevertheless, editing a completed-response binding adds `activation: latest_completed`
without checking the execution profile. Applying ordinary mapping/final-result
controls can therefore introduce invalid data.

A sequence-style final-result binding can be accepted by definition validation,
but sequence compilation does not carry it into execution. Sequence execution
returns all node outputs. The observed draft/review aggregate is consistent with
that implementation; the displayed final-result choice is misleading. Conditional
execution uses ports, optional feedback and a final-result binding legitimately.

**Correction:** expose only applicable controls, preserving existing inactive or
extension source deliberately. For sequence show “Returns all node results”; edit
backward mappings without conditional metadata. For conditional execution expose
ports, first-pass feedback and explicit result selection. Do not silently change
the runtime contract to make a generic form appear correct.

**Source:** [automatic activation metadata](../../../../../frontend/src/features/workspace/connections/binding-state.ts#L48),
[unconditional final-result form](../../../../../frontend/src/features/workspace/graph-editor.tsx#L18),
[validation](../../../../../backend/src/slow_thinker_ii/adapters/catalog/_validation/_nodes.py#L45),
[sequence metadata constraints](../../../../../backend/src/slow_thinker_ii/adapters/catalog/_validation/_nodes.py#L67),
[final-result validation](../../../../../backend/src/slow_thinker_ii/adapters/catalog/_validation/_nodes.py#L111),
[sequence compiler](../../../../../backend/src/slow_thinker_ii/adapters/catalog/_sequence_compiler.py#L59),
[aggregate result](../../../../../backend/src/slow_thinker_ii/application/_sequence_program.py#L26),
[conditional result](../../../../../backend/src/slow_thinker_ii/application/_conditional_program.py#L100).

### UX07 — The prominent graph previews saved source, not edited source · P2

**Source-confirmed:** the canvas receives saved graph detail while forms receive the
draft source. A changed component or route need not be reflected in that canvas.
Connection handles are visible, but drag-to-connect is disabled; control edges
have no editing selection. This can suggest capabilities the view does not provide.

**Correction:** identify saved versus draft preview explicitly and show divergence.
Synchronize selection and provide ordinary connection-edit actions without implying
full graphical authoring has been implemented. Preserve independent historical run
identity; editing a draft must never alter the displayed historical definition.

**Source:** [saved detail and draft source](../../../../../frontend/src/app/authoring-workspace.tsx#L50),
[disabled connections](../../../../../frontend/src/features/graph-view/graph-canvas.tsx#L25),
[edge selection](../../../../../frontend/src/features/graph-view/control-routes.ts#L30).

## Agents, models, resources and extensibility

### UX08 — Model changes can strand incompatible parameters · P1

**Source-confirmed:** model selection patches the profile/model, retaining existing
parameters. Temperature is then disabled when the profile or selected reasoning
cannot accept it. A retained incompatible value has no ordinary remove-override
action; the provider rejects such combinations. Blank optional values and unsupported
values are not clearly distinguished from effective defaults.

**Correction:** before applying model/effort changes show affected overrides and
their compatibility. Offer explicit removal or “Use model default”, without silently
discarding unknown settings. Explain disabled fields at their location. When the
model resource is shared, identify every affected user-facing agent, not only workers.

**Source:** [model patches](../../../../../frontend/src/features/workspace/agents/model-selection.tsx#L10),
[parameter availability](../../../../../frontend/src/features/workspace/agents/generation-options.ts#L24),
[scalar actions](../../../../../frontend/src/ui/schema-values/scalar.tsx#L33),
[provider validation](../../../../../components/model-provider/src/slow_thinker_model_provider/_requests.py#L40).

### UX09 — Resource choices include incompatible resource types · P2

**Observed:** Calculator and Memory selectors offer model resources as well as the
calculator and memory instance. **Source-confirmed:** filtering uses roles and
declared operations, but shipped ContextualCall resource slots declare only the
resource role. Its runtime requires specific calculate/get/put operations.

**Correction:** declare required capabilities in canonical descriptors and filter
ordinary choices accordingly. Keep an existing incompatible selection visible with
an explanation. A model should not look like a valid replacement for memory merely
because both implement the resource role. Do not automatically grant permissions.

**Source:** [filter](../../../../../frontend/src/features/workspace/agents/resource-bindings.ts#L29),
[shipped slots](../../../../../components/contextual-call/contextual-call.component.json#L85),
[runtime operations](../../../../../components/contextual-call/src/slow_thinker_contextual_call/_component.py#L27).

### UX10 — Ordinary memory retention still requires JSON · P2

**Observed:** Configure shared-memory shows “Advanced JSON: Retention”. The shipped
schema uses a valid enum without an explicit type; the form's type inference sends
it to the JSON fallback. This is an ordinary first-party setting, not an unknown
extension construct.

**Correction:** present “This run” and “Across runs” as ordinary choices. Explain
which agents share the instance, where keys live and what survives a new run.
Expose namespace and capacity limits progressively, using meaningful units.

**Source:** [memory enum](../../../../../components/key-value-memory/key-value-memory.component.json#L192),
[type inference](../../../../../frontend/src/ui/schema-values/values.ts#L9),
[fallback](../../../../../frontend/src/ui/schema-field.tsx#L11).

### UX11 — Fields expose names without enough meaning or effective values · P2

**Observed/source-confirmed:** instructions, token limits, effort, namespace and
memory key are available, but generic configuration does not consistently display
schema descriptions, required/default metadata or constraints. “Choose a value”
and an empty field do not explain whether a backend default is active. Some
constraints are checked only when applying/validating the larger definition.

**Correction:** show the purpose, effective value, allowed range, default provenance
and effect of an override. Make help contextual and short. Use schema titles and
descriptions where trustworthy, and maintain fallbacks for extensions. A form label
should answer what changes, not merely convert snake_case to spaced text.

**Source:** [schema form](../../../../../frontend/src/features/workspace/schema-form.tsx#L15),
[scalar inputs](../../../../../frontend/src/ui/schema-values/scalar-input.tsx#L29),
[memory default](../../../../../components/contextual-call/src/slow_thinker_contextual_call/_config.py#L83).

### UX12 — Tools and permissions require users to reconstruct an internal call chain · P2

The distinction between selecting a resource and authorizing access is correct.
However, the ordinary page asks users to connect “Read memory” to separate
caller/target/operation grants, including managed workers. The permissions section
competes with instructions and model selection instead of explaining their readiness.

**Correction:** show capability-level status beside each tool: for example,
“Proposer can read shared memory” or “Read permission missing”, with an explicit
grant action. Keep granular grants and internal call chains available to experts.
Display an impact warning when a shared resource configuration changes; do not
silently broaden authority or treat hiding controls as a security mechanism.

**Source:** [binding help](../../../../../frontend/src/features/workspace/binding-fields.tsx#L15),
[grant editor](../../../../../frontend/src/features/workspace/agents/permission-grant.tsx#L51),
[agent resources](../../../../../frontend/src/features/workspace/agents/resources.tsx).

### UX13 — Component discovery and adding an agent are disconnected · P2

**Observed:** Components lists type/version, role, installation state and operation
names, with no purpose-oriented selection journey. Resources is read-only and shows
irrelevant “Retention: Not configured” and “Namespace: Not configured” on model and
calculator cards. **Source-confirmed:** adding an instance is hidden under Advanced,
creates empty configuration/resources, and is separate from adding an agent node.

**Correction:** describe each type's purpose and requirements, distinguish installed
types from experiment instances, and provide a guided Add agent journey using
registered capabilities. Resource cards should show only applicable metadata and
link to the relevant configuration. Keep independent instance creation for experts.

**Source:** [inventory](../../../../../frontend/src/features/workspace/inventory.tsx#L30),
[new instance](../../../../../frontend/src/features/workspace/new-instance.tsx#L53),
[new node](../../../../../frontend/src/features/workspace/connections/node-targets.tsx#L43),
[irrelevant resource metadata](../../../../../frontend/src/features/workspace/resource-inventory.tsx#L79).

### UX14 — Data mapping assumes knowledge of internal response paths · P2

Users choose a target input, source kind, source node and field path. Helpful mapping
summaries exist, but “Response field path” also labels task input paths; target
fields lack operation-schema suggestions. `/value/value/findings` exposes wrapper
composition rather than the user concept “Reviewer's findings”. “Completed agent
response” does not explain which invocation supplies repeated feedback.

**Correction:** show a readable mapping sentence with source, destination and value
example, using declared schemas. Explain latest-completed selection and first-pass
omission. Keep exact paths accessible and editable for extensions. Distinguish data
availability from control flow: referencing a response does not itself schedule its agent.

**Source:** [target input](../../../../../frontend/src/features/workspace/input-binding.tsx#L21),
[source controls](../../../../../frontend/src/features/workspace/connections/binding-controls.tsx#L41),
[path help](../../../../../frontend/src/features/workspace/connections/path-control.tsx#L28).

### UX15 — Branch selection, routing, Finish and result selection need separate explanations · P2

**Observed:** Output port, selected route destination, Final result and Router appear
in separate places. The router's “Selector” field contains a Python callable
reference (`example_grounded_review:choose`), not a script editor. Maximum activations
does not explain how it differs from calls or review rounds. Outputs are declared
in both the composed agent and router, without a visible consistency guide.

**Correction:** for the reviewed RoutedCall composition, explain the chain:
response → routing function → named branch → destination. Other supported conditional
nodes can select a constant branch or read one from a response field without a
separate routing function. “Finish” ends control routing; a separate rule chooses returned content.
Name and document the routing function reference, its input/output contract and
declared exits. Do not imply inline script execution exists. Show consistent exit
names, an explicit bound meaning and a worked review-loop example. Permit custom
declared ports for extensions alongside suggestions.

**Source:** [port form](../../../../../frontend/src/features/workspace/connections/output-port.tsx#L73),
[route form](../../../../../frontend/src/features/workspace/connections/route-form.tsx#L53),
[routes](../../../../../frontend/src/features/workspace/connections/routes.tsx#L70),
[flow settings](../../../../../frontend/src/features/workspace/connections/flow-selection.tsx#L38).

### UX16 — Schema editing exposes schema language and inconsistent apply behavior · P2

The recursive builder supports useful nested fields, arrays and constraints. Labels
such as `exclusiveMaximum`, `additionalProperties` and “Schema type for …” nevertheless
require implementation knowledge. Type changes retain old constraints; some become
hidden. Required checkboxes patch immediately while adjacent type/value edits need Apply.
Removing a node/field can also leave references requiring repair elsewhere.

**Correction:** use purpose-oriented labels, examples and previews. Explain retained
constraints and show references affected by removal. Link validation messages to
the relevant editor, preserving exact paths in technical details. Retain unsupported
schema constructs instead of silently flattening them.

**Source:** [constraint labels](../../../../../frontend/src/ui/schema-definition/constraints.tsx#L7),
[required behavior](../../../../../frontend/src/ui/schema-definition/property-row.tsx#L39),
[type patch](../../../../../frontend/src/ui/schema-definition/header.tsx#L24),
[validation rendering](../../../../../frontend/src/features/definition-editor/editor-feedback.tsx#L10).

## Execution, results and recovery

### UX17 — Run-input forms do not carry the authoring schema's guidance · P2

**Observed:** required empty task fields immediately show messages such as
`/expression: must NOT have fewer than 1 characters`. **Source-confirmed:** ordinary
run controls retain little schema metadata; descriptions, examples, defaults, enums
and bounds are not incorporated consistently. One nested property can switch the
whole task to a JSON textarea. Numeric fields use textareas rather than task-specific inputs.

**Correction:** reuse supported structured value controls, display field guidance
and link plain-language errors to fields. Delay avoidable empty-field errors until
interaction/submission. Keep advanced JSON available, but do not require it for
ordinary nested structures already supported by the authoring UI.

**Source:** [field extraction](../../../../../frontend/src/features/execution/input-fields.tsx#L10),
[JSON fallback](../../../../../frontend/src/features/execution/run-input.tsx#L10).

### UX18 — Execution safeguards are not fully explained where users act · P2

**Source-confirmed:** disabled Start may reflect missing session, storage readiness,
admission policy, pending commands or stale state; the API's admission reason is not
displayed. Stop is inside the collapsible New run setup. A stop-request flag can
retain waiting text after polling confirms a terminal state.

**Correction:** show the current blocking reason and next action beside Start. Put
Stop beside active status, independent of form expansion. Derive stopping text from
current state. Preserve exact-command recovery and never retry by silently creating
a second execution. Distinguish execution completion from cleanup and cost settlement.

**Source:** [admission gate](../../../../../frontend/src/features/execution/state.ts#L102),
[API reason](../../../../../frontend/src/api/operator-schemas.ts#L15),
[control messages](../../../../../frontend/src/features/execution/start-controls.tsx#L80),
[stop receipt](../../../../../frontend/src/features/execution/receipts.ts#L17),
[polling state](../../../../../frontend/src/features/execution/polling.ts#L44).

### UX19 — Readable text does not yet explain the collaboration outcome · P2

**Observed:** Final result shows separate `draft` and `review` headings containing
the same workshop text. The UI does not map these IDs to Proposer/Reviewer or explain
whether review accepted, changed or simply returned the content. A failed run shows
`Reason: startup_failure` and offers technical inspection, without a next-step explanation.
**Source-confirmed:** result-load failure has no direct Retry; only completed runs
receive the result panel, so retained partial work is not surfaced there.

**Correction:** label responses by agent and invocation, explain aggregate versus
selected final result, show captured review reports when available, and explicitly
say when no verdict was recorded. Provide actionable failure summaries and access
to retained partial outputs. Add retry for result retrieval. Completion alone must
never be labeled as successful evaluation or proof of influence; deeper evaluation
remains a later feature.

**Source:** [result panel](../../../../../frontend/src/features/execution/result-view.tsx#L14),
[result content](../../../../../frontend/src/features/execution/results/content.tsx),
[run status](../../../../../frontend/src/features/execution/run-view.tsx#L19).

### UX20 — “Original response” can be normalized and numerically altered · P1

**Source-confirmed:** the result client obtains content through `response.json()`
and then `JSON.stringify`. The disclosure therefore does not preserve original JSON
bytes and may already have rounded large/high-precision JSON numeric literals.
The source-preserving renderer cannot restore information lost upstream. This
review did not identify corruption in the inspected workshop run.

**Correction:** preserve bounded source end to end where exact evidence is promised.
Clearly distinguish rendered content, normalized JSON and original captured evidence.
Validate through the complete API-to-display path, including values outside JavaScript's
exact integer range. Do not substitute a reassuring label for that guarantee.

**Source:** [result serialization](../../../../../frontend/src/api/operator.ts#L72),
[JSON parsing](../../../../../frontend/src/api/transport.ts#L23),
[original label](../../../../../frontend/src/features/execution/result-view.tsx#L50).

### UX21 — History entries are difficult to distinguish · P2

**Observed:** buttons show graph ID, status and eight ID characters, with no visible
selected state, date or task description. The exact revision is visible only after
selection. **Source-confirmed:** More runs replaces a page rather than accumulating
entries, and Previous navigation is absent.

**Correction:** show available revision/selection immediately and use honest paging
labels. Add date/task summaries only with corresponding API data; do not infer them
from IDs. Separate the current editable experiment from the selected historical run
with equally visible context, preserving their independent identities.

**Source:** [history labels](../../../../../frontend/src/features/execution/history-view.tsx#L38),
[paging](../../../../../frontend/src/features/execution/page-controls.tsx#L24).

### UX22 — Cost and limit figures omit essential scope explanations · P2

The precise recorded/pending/limit values are useful, but users must infer available
allowance, the meaning of pending reservations, the current month and which session
is charged. Current workspace month spending appears while inspecting historical
runs. Deadlines, maximum calls, call depth and payload size lack examples and scope.

**Correction:** distinguish current allowance from historical run accounting; show
period/timezone and explain reservations. Keep sub-cent precision without pretending
small charges are zero. Explain whether each setting governs one model call, all
mediated calls, a run, a session or the month, and when changed limits take effect.
Use readable duration/size units with exact technical values available.

**Source:** [budget presentation](../../../../../frontend/src/features/execution/run-view.tsx#L34),
[current month](../../../../../frontend/src/features/execution/execution-panel.tsx#L101),
[limit labels](../../../../../frontend/src/features/workspace/limits-model.ts#L9),
[accounting contract](../../contracts/accounting-policy.md#L7).

### UX23 — Settings recovery and errors do not describe their actual effect · P2

**Source-confirmed:** “Use latest server limits” resets from the existing client
catalog; it does not fetch current server values. It can restore stale values after
a concurrent change. Errors such as `invalid_limits` do not point to the offending
field or explain coupled restrictions. The agent's model selector includes a terse
tariff status, while fuller capability and expiry information resides in Settings;
the selector does not explain what that status establishes.

**Correction:** separate Discard edits from Reload server values, preserve clear
conflict recovery and provide field-specific constraints. Show model availability
and its meaning at selection. “Ready” must distinguish installation, tariff readiness
and verified access; none alone promises a successful model response.

**Source:** [reset label](../../../../../frontend/src/features/workspace/settings.tsx#L95),
[reset implementation](../../../../../frontend/src/features/workspace/use-limits.ts#L70),
[error projection](../../../../../frontend/src/api/configuration.ts#L15).

### UX24 — Access, loading and empty states can contradict reality · P2

**Observed:** with local services stopped, the page simultaneously showed a catalog
load error and “No saved experiments are available”. After key submission it could
show “Operator connected” despite failed discovery. During definition loading it
briefly advised using advanced JSON to correct unreadable source.
**Source-confirmed:** connected means a credential is held locally, not that the
server verified it. Disconnect clears local work without explaining the loss or
whether server execution continues.

**Correction:** distinguish Connecting, Access verified, Access rejected, Service
unavailable, Loading and genuinely Empty. Give key-acquisition guidance. Explain
disconnect consequences and guard unsaved work. Do not show source-repair advice
while merely awaiting a response.

**Source:** [optimistic access](../../../../../frontend/src/app/access-panel.tsx#L38),
[credential-based composition](../../../../../frontend/src/app/app.tsx#L24),
[generic discovery error](../../../../../frontend/src/features/workspace/use-discovery.ts#L47),
[unreadable-source fallback](../../../../../frontend/src/features/workspace/index.tsx).

### UX25 — Evidence inspection is technical first and has an incomplete focus lifecycle · P2

**Observed:** Inspect run opens a large event table starting with `run.created` and
multiple `host.state_changed` entries before agent activity. Escape did not close
the panel. **Source-confirmed:** the fixed complementary panel has Close and focused
headings but no complete Escape/return-focus lifecycle. Its responsive overlay can
cover content while background controls remain keyboard-accessible.

**Correction:** lead ordinary inspection with agent/invocation input, output and
recorded activity; preserve full technical events as an expert view. Give evidence
links meaningful names, keep missing/redacted data explicit and avoid presenting
reported reasoning as complete internal thought. Choose modal or nonmodal behavior
deliberately; implement its keyboard, focus and background-visibility semantics.
Verify with keyboard and assistive technology before any conformance claim.

**Source:** [inspector composition](../../../../../frontend/src/app/execution-workspace.tsx#L70),
[fixed panel](../../../../../frontend/src/app/workspace.css#L92),
[event view](../../../../../frontend/src/features/inspector/event-view.tsx),
[focus handling](../../../../../frontend/src/features/inspector/focus-heading.tsx#L10).

### UX26 — Extension forms infer capabilities from field names · P2

**Source-confirmed risk, not an observed third-party failure:** a component whose
discovered configuration schema declares `instructions` receives specialized
model/response treatment, and fields named
`parameters` or `output` can be excluded from the ordinary schema form. Names ending
in `_schema` are treated as schema editors. Unrelated custom components can use these
names with different meanings.

**Correction:** let explicit capability/presentation metadata select specialized
editors. Retain generic schema-driven forms and intact advanced source. Every
component should be able to declare display name, purpose, help, defaults, constraints,
capability slots and compatibility without exposing all implementation details to
ordinary users. This is a proposed contract refinement requiring design review.

**Source:** [instructions heuristic](../../../../../frontend/src/features/workspace/model-fields.tsx#L21),
[schema suffix heuristic](../../../../../frontend/src/features/workspace/schema-form.tsx#L49),
[schema-form special cases](../../../../../frontend/src/features/workspace/schema-form.tsx#L59).

## Foundations worth preserving

Keep source-preserving leaf patches, immutable revisions, explicit authority,
bounded imports and schema traversal, shared-consumer information, historical run
identity, safe text rendering, missing/redacted evidence states and identical-command
recovery. Native labels, fieldsets, focus styling, responsive wrapping and the
keyboard-accessible evidence list are useful foundations. None of the proposed
simplifications should weaken these guarantees.
