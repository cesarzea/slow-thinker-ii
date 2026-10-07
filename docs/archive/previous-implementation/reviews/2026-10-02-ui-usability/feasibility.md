# Interface concept: implementation feasibility

| Document control | Value |
| --- | --- |
| Assessment ID | UX-S06-001-F01 |
| Date and timezone | 2026-10-02, Europe/Lisbon |
| Baseline | `a844514` — S06 configuration and results |
| Status | Assessment completed; implementation not authorized |
| Scope | Latest interface concept and owner requirements DR01–DR14 |

## Conclusion

The proposed interface is technically feasible on the existing React/TypeScript
frontend and Python backend. It fits S06's purpose: make experiment configuration,
execution and inspection usable without requiring ordinary users to edit JSON.
The layout does not require replacing the orchestration engine, component process
model or immutable experiment revisions.

It is not yet a complete implementation contract. The concept depicts the design
screen, while several required workflows and some displayed information need
additional interaction or API definitions. The existing selection, draft and
revision defects must be corrected as part of the delivery, not concealed by a
new layout. A static concept image is not usability acceptance evidence.

## Reuse and required changes

| Area | Existing foundation | Required work |
| --- | --- | --- |
| Navigation and layout | Separate application, graph, editing and execution modules. | Contextual experiment navigation, persistent global footer, full-width layout and adjacent inspector. Distinguish experiment settings from workspace defaults and limits. |
| Agent selection and editing | Graph selection and schema-driven forms exist. | One selection identity and draft shared by canvas, inspector and save action; preserve edits across navigation. Identify both graph step and component instance when instances are reused. |
| Instructions | Existing prompt fields and definition patches. | Compact and expanded editors of the same pending value, with expansion inside the textarea. Preserve unknown extension fields and immutable revision semantics. |
| Graph and resources | Custom graph nodes, edges, layout and resource bindings. | Draft-aware projection, optional resource layer, distinct attachment geometry, configured-consumer highlighting and graph toolbar. Do not depict a binding as an observed call. |
| Add and delete actions | Instance, node, binding and connection editors. | Guided commands that coordinate required definition changes and validate references. Deletion must account for routes, mappings, containment and permissions. Full drag-to-connect authoring remains outside this correction. |
| Configurable composition | Versioned component descriptors, configuration schemas and resource slots. | Present compatible declared slots and configured instances. Extend discovery metadata where necessary for meaningful labels, composition controls and presentation; avoid hardcoded universal tools, memory or routing sections. |
| Experiment collection | Paginated definition summaries and immutable revisions. | Define experiment grouping and readable metadata. Descriptions, update dates and latest-run information illustrated in concepts are not all supplied by the current listing API. |
| Graph versions | Immutable identities, source retrieval, source-revision references and draft derivation. | Experiment-scoped revision history, reliable ordering and metadata, readable comparison and creating a new draft from a historical revision. Preserve historical runs; distinguish definition comparison from evaluation of results. |
| Experiment runs | Saved runs, results, accounting and evidence. | Provide experiment-scoped history across sessions. Current history is session-scoped; filtering one loaded page would not provide a complete experiment history. Preserve the executed revision separately from the editable draft. |
| Credits and user footer | Monetary budget ledger and local operator access. | Under DR13, display an explicitly illustrative user/credit preview only. Real accounts and credit accounting are deferred; existing operator access and real monetary limits remain in force. |

The current [workspace contract](../../contracts/product-workspace.md) and
[S06 completion contract](../../specification/s06-product-completion.md) describe
an earlier navigation and editing interaction. Their affected sections need an
agreed update before implementation; this assessment does not silently supersede
them.

## Component extensibility

An **Add component** action must offer capabilities supported by the selected
component's declared extension points. Catalog presence, a resource binding and
permission to call an operation are distinct facts. Adding or authorizing a memory
resource does not make agent code use it automatically.

Existing resource slots and schemas support a substantial starting point. They do
not yet constitute a complete contract for arbitrary nested editors, composition
presentation or compatible runtime behavior. Metadata should travel through the
descriptor, discovery API and UI with a defined compatibility policy. Unknown
extensions must retain an explicit advanced editing path without data loss.

An embedded component and a reference to a shared resource must remain distinct.
Private/shared memory behavior belongs to the existing component and resource
contracts. Reusable graphs implemented as agents remain a future capability.
See [components](../../contracts/components.md),
[graphs](../../contracts/graphs.md) and [tools and memory](../../contracts/tools-memory.md).

## Credit presentation and accounting

**Owner clarification, 2026-10-02 (DR13):** users and credits are illustrative
placeholders for this delivery. Their real semantics remain deferred. This removes
credit valuation and account behavior as prerequisites for the current UI scope.

Retain DR12's horizontal consumption bar above small, readable credit figures.
Identify the area as a preview with English copy such as **Demo credits** and
**Account preview**. Example balances must not be sourced from or affect the real
ledger, simulate actual paid deductions, or imply an implemented account service.
The existing operator-access controls and real monetary limits remain functional
and distinct from these placeholders. Account actions remain explicitly unavailable.

Before future credit implementation, define the unit, valuation, allocation,
deduction, reservation and replenishment rules. The earlier suggestion of a
versioned conversion from monetary accounting remains only an option, not an
approved model. Preserve exact provider cost evidence and the
[accounting policy](../../contracts/accounting-policy.md). Workspace settings must
continue to distinguish supported controls from explicitly deferred capabilities.

## Required workflows beyond the image

1. Create or import an experiment, select a revision, edit a draft and save a new
   revision without losing changes or overwriting the evidence of an earlier run.
   Browse saved versions, inspect their changes and derive a new draft from a
   historical revision; never overwrite that revision as a restoration action.
2. Configure collaboration: entry, connections, data mappings, conditional exits,
   feedback and completion according to the chosen execution profile.
3. Define task inputs and intended outputs, with understandable field labels and
   validation. Agent instructions are only one part of the complete model request.
4. Connect compatible resources, explain missing permissions and obtain explicit
   configuration changes. Never grant additional authority silently.
5. Select a session, supply task data, inspect effective limits, run, stop and
   recover from failures or uncertain outcomes with clear status.
6. Inspect the final result and individual activations, including exchanged data,
   duration and cost. Keep exact evidence accessible; do not infer influence or
   quality from successful completion alone.

All journeys require keyboard access, visible focus, readable states and an
appropriate narrow-screen layout. Test them on a working interface; the concept
does not establish their accessibility or ease of use.

## Fit with the project and delivery boundary

The workspace is a necessary authoring and observation surface for a collaboration
evaluation platform. It is not the complete evaluation product. Comparative
evaluation, deep influence analysis, dynamic or nested graphs and full graphical
authoring retain their separate scopes in the [roadmap](../../specification/sprint-roadmap.md).

Prepare one bounded implementation scope covering the complete configuration,
execution and inspection journeys above. Close only the missing contracts needed
for that scope, assign coherent module ownership, implement, review the combined
result and verify the [audit acceptance scenarios](README.md#acceptance-scenarios-for-a-correction).
Acceptance requires those journeys to work, not merely visual similarity to the
concept. This assessment authorizes neither implementation nor roadmap changes.

## Implementation evidence

Source review supports feasibility; no application changes or paid runs were made
for this assessment. Key implementation references:

- [Workspace composition](../../../../../frontend/src/app/authoring-workspace.tsx),
  [graph canvas](../../../../../frontend/src/features/graph-view/graph-canvas.tsx) and
  [editor state](../../../../../frontend/src/features/definition-editor/use-editor.ts).
- [Resource compatibility](../../../../../frontend/src/features/workspace/agents/resource-bindings.ts),
  [model controls](../../../../../frontend/src/features/workspace/model-fields.tsx) and
  [discovery schemas](../../../../../frontend/src/api/configuration-schemas.ts).
- [Definition library](../../../../../frontend/src/api/definition-library.ts),
  [budget and runtime schemas](../../../../../frontend/src/api/operator-schemas.ts),
  [history](../../../../../frontend/src/features/execution/history-view.tsx) and
  [operator access](../../../../../frontend/src/app/access-panel.tsx).
