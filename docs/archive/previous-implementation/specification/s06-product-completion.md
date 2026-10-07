# S06 product workspace completion

> **S06-UX target update — 2026-10-02.**
> The later [S06-UX delivery specification](s06-workspace-redesign.md) records the
> owner-reviewed interface requirements and the prepared complete correction scope.
> It supersedes conflicting navigation, field Apply and save-lifecycle requirements
> below. Earlier implementation/checkpoint statements remain historical evidence,
> not usability acceptance or implementation of the new design.

| Document control | Value |
| --- | --- |
| Scope | Completion of S06, following owner interface review |
| Authorized | 2026-10-02, Europe/Lisbon |
| Status | Locally verified; ready for owner review |
| Baseline | [S04–S06](s04-s06-delivery.md), A15–A22 |
| Method | [M06](../../../continuous-improvement/methods/006-delivery-preparation.md) |

## Outcome and review finding

The first delivery established functional configuration APIs and controls, but
ordinary configuration still exposed JSON fields and internal component inventories.
The owner authorized completing S06 before S07. Functional test counts did not
establish that the product interaction objective had been achieved. Retain the
previous checkpoint as evidence; it is not acceptance of the product experience.

## Screen and interaction contract

The workspace uses a restrained, consistent visual hierarchy: persistent primary
navigation, an experiment/revision context header, a main content area and clear
primary actions. Use readable widths, grouped cards, visible focus, responsive
stacking and sufficient text contrast. All authored content is English.

Experiments shows the agent canvas, a compact revision/save toolbar and configuration
sections **Agents**, **Connections** and **Task inputs**. Ordinary configuration is
visible in one selected section rather than a long list of unrelated forms. Keep
the selected section and unapplied values across primary navigation. Clearly state
that Apply updates the draft and Save persists a new immutable revision.

Agents shows the graph's agent instances first. Selecting Proposer in the resource
collaboration example exposes its instructions, reasoning, output limits, bound
model and resource/worker settings together. Resolve the configured worker through
`components[id].resources.worker`; follow bounded, cycle-safe child references.
Edit each underlying component at its own source path. List other instances under
an advanced component editor, preserving external component support. Controller
configuration is presented as flow settings in Connections, not an agent.

Known configuration values use text, exact numeric, boolean, enum, object and
array controls. Object and array editors preserve unrelated raw values. Input and
output schemas use a field builder for object properties, types, required fields,
nested objects/arrays and common constraints. Existing unsupported schema constructs
remain intact and are available in explicitly expanded advanced JSON controls.
Do not rebuild a complete graph with browser JSON.parse/stringify.

Resource and managed-worker bindings use selectors derived from declared slots,
registered operations and existing instances. Missing resources maps can be created
by the same patch transaction. Permissions remain explicit: render readable grants
and add/remove actions with caller, target and operation selectors. Binding a
resource never silently grants access. Display the model profile within the agent
configuration; explain when its resource is shared with another consumer.

Connections provides node/component/operation selectors, readable existing input
mappings, add/edit/remove mappings, sequence reordering, conditional source/port/
destination selectors and an explicit Finish destination. Show entry and activation
limit controls. Output selection supports constant ports and response-field paths;
the final result supports selecting a node and a response field. Offer known field
paths where possible and retain a plain path input for extension payloads. Preserve
`missing`, activation and other binding fields when changing one mapping property.
Profile/controller changes remain explicit and validated; a draft cannot imply
that an incompatible controller is executable.

Runs displays clear state and costs, readable result content and each named node
result when the server returns an aggregate. Render runtime text safely, never as
HTML. Structured results use readable key/value or nested presentation, with the
original raw response in a collapsed advanced disclosure. Preserve exact run
identity, stale/unknown states, cancellation and historical configuration.

Advanced JSON remains available for opaque extension configuration and expert use.
Full graphical authoring, new execution profiles and new runtime capabilities stay
in their existing later sprints.

## Public interfaces and assignment ownership

All code consumes existing public `api/index.ts`, `ui/index.ts`, feature entry
points and the source-preserving patch API. `SourceValue` retains `raw`, `entries`
and `items`. `PatchOperation` sends an exact `value_json` string to an individual
path; the server owns validation and immutable persistence.

| Owner | Exclusive complete modules | Required dependency contract |
| --- | --- | --- |
| Form primitives | `frontend/src/ui` | Preserve `SchemaField` props; export `SchemaDefinitionField` with `label`, `path`, `source: SourceValue \| undefined`, `disabled`, `patch`. It edits a schema document using field controls and exact patches. No API calls or feature imports. |
| Configuration | `frontend/src/features/workspace` | Preserve `StructuredWorkspace` and `SourceWorkspaceProps`; consume `SchemaDefinitionField` from `ui/index.ts`. Resolve descriptors through existing public catalog types. |
| Presentation | `frontend/src/app`, `frontend/src/features/definition-editor`, `frontend/src/features/execution` | Preserve authoring and execution public contracts; style the shell and common controls, compact revision controls and readable results. |
| Coordinator | Shared documentation, quality configuration and verification coordination | Resolve cross-module decisions; review complete journeys and source-preservation/failure behavior. |

Common presentation classes may include `configuration-tabs`, `agent-list`,
`agent-card`, `agent-settings`, `field-grid`, `advanced-options`, `result-content`
and `page-heading`. Public signatures above are fixed; local decomposition is left
to each implementer. New subdirectories group cohesive private implementation.

Representative source: the registered `resource-collaboration` example has
`proposer.resources.worker = proposer-worker`,
`proposer-worker.config.instructions`, `config.parameters.reasoning_effort`,
`proposer-worker.resources.model = openai-model`, and
`openai-model.config.provider_profile`. Its private/shared memory is bound through
`proposer.resources.memory = shared-memory`. The bounded-review example supplies
conditional routes, nested output schemas and optional missing-input mappings.

## Acceptance and verification

| ID | Required outcome |
| --- | --- |
| U01 | Create an immutable variant, change an agent's prompt, model and effort through forms, validate and save without typing JSON. |
| U02 | Configure a composed agent's worker, calculator and memory from the selected agent; inspect shared consumers and grant permissions explicitly. |
| U03 | Add/edit/remove object fields and array item schemas using controls; preserve existing unsupported constraints and exact unrelated numeric literals. |
| U04 | Edit input mappings, sequence order, conditional routes, entry/activation limits and final output using controls, including Finish and optional feedback inputs. |
| U05 | Ordinary configuration hides raw JSON and technical internals by default; expert controls remain available and never discard opaque extension fields. |
| U06 | Completed real-run content is legible, named node results are distinguishable, and original evidence stays inspectable with exact identities. |
| U07 | Keyboard and narrow-screen journeys retain visible actions, labels, focus and readable layout. Field validation, pending patches, dirty drafts and immutable saving retain existing guards. |
| U08 | Required local quality, security, coverage and browser checks pass; inspect the actual application and an existing paid run without incurring a new model charge. |

Complete development and individual/whole-system review before test implementation.
Then establish fixtures and a representative browser journey; assign tests by
module, group corrections and run the unchanged configured verification entry point.
Review the rendered experience against U01–U07, not only automated assertions.


## Verification checkpoint

U01–U08 have local evidence in [report 0.0.6.2](../progress/sprint-06-status-report.md)
and the [shared verification record](../verification.md#s06-product-workspace-completion--2026-10-02).
The original paid run was inspected without another model call. This checkpoint
establishes implementation verification; owner acceptance and publication remain
separate. No later sprint is activated.
