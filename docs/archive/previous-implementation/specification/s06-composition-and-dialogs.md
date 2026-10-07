# S06 — Configurable composition and component-owned dialogs

| Document control | Value |
| --- | --- |
| ID | S06-COMPOSITION / 1 |
| Owner / date | Cesar Zea / 2026-10-03 |
| Status | Parallel verification and grouped corrections active; full verification pending |
| Method | M06: complete preparation, exclusive parallel packages, combined review, testing |

## Authority and delivery boundary

The owner reopened S06 after finding that Add component only expanded existing
bindings, LLMCall could not accept a Redirector, ordinary configuration required
JSON, and platform-owned presentation restricted independent components. Earlier
verification remains valid for its tested behavior; it does not establish this
scope's delivery or usability acceptance. The owner approved the correction list
and its dependencies, and explicitly authorized completing this sprint.

Complete configurable composition and component-owned presentation across the
existing local workspace. Retain graph schema 0.1-draft, finite sequence and bounded
conditional profiles, exact-source drafts, immutable history, mediated processes,
permissions, deadlines and accounting. No paid calls, publication, real accounts,
credits economy, internal graph editor, simultaneous output emission or new graph
profile is introduced. Trusted component preparation remains independent of UI
configuration; an installed callable reference is not an arbitrary script runner.

## Closed architecture decisions

1. A component supplies versioned declarative dialogs and summaries. The platform
   interprets a common contract; it does not choose dialogs by type name.
2. New declarative attachments express before/after-worker calls, input mapping,
   result selection and optional routing. A separately packaged generic composer
   executes them through the existing managed MCP boundary. Legacy RoutedCall and
   ContextualCall remain supported, but new attachment behavior requires no new
   special agent type or platform branch for the attached component.
3. Attaching preserves the graph agent ID/name and node IDs. Its former functional
   component becomes a managed worker with the same configuration and bindings.
   Outgoing grants transfer to that worker; grants for the new composition are
   explicit in the preview. Downstream result pointers retain their original
   meaning through a coherently added envelope. Removal restores the current
   worker settings, not an old configuration snapshot.
4. Configuration edits occur in local dialog drafts. Apply stages one coherent
   source patch; Cancel/Escape/Close discard the local changes. Save revision is
   separate. A pending or invalid dialog cannot silently contaminate the shared
   draft. Concurrent context/source changes invalidate a pending structural plan.
5. Bundled components provide complete ordinary forms. Expert source access remains
   optional. Unknown external constructs preserve source and offer an explicitly
   generic configuration dialog. No semantic value is inferred from an example ID.

## Acceptance matrix

| ID | Required outcome |
| --- | --- |
| C01 | Select an ordinary Proposer, add a compatible Redirector, retain its identity/prompt/model/settings, save and execute the composition. |
| C02 | Attachment phase, input source, result behavior and ports come from the component contract; incompatible/missing contracts produce understandable explanations. |
| C03 | Replace/remove internal components without losing current worker edits; list affected connections and require resolution of incompatible ports/shared references. |
| C04 | Sequential graphs may explicitly become bounded conditional while preserving order and requiring a positive activation limit. Existing conditional destinations are retained only where their port meaning remains unchanged. |
| C05 | Private/shared resources and actual consumers remain visible; required functional connections and grants are configured deliberately, with no automatic memory/context injection. |
| C06 | Adjacent inspector is read-only: readable summary cards with Edit actions; no textboxes, selects, JSON, slots or telemetry controls in ordinary summary content. |
| C07 | Separate component-declared concept dialogs, large Prompt editor, component breadcrumb, no stacked modal windows, coherent Apply/Cancel and accessible keyboard/focus behavior. |
| C08 | Every bundled type's supported ordinary configuration is available through fields, including input/response schemas, native options, routing outputs and installed selector choice. JSON is an optional expert action. |
| C09 | Component metadata is shipped in its package/descriptor and consumed generically. An external authored component supplies its own fields/summary and attachment behavior without a platform type-specific adapter. |
| C10 | Add component opens selection and creation, not an existing-section disclosure. Existing children have Configure/Replace/Remove actions with clear scope. |
| C11 | Agent cards remain agent-focused; platform wrappers, slot keys and instrumentation are hidden from ordinary configuration. Recorded child calls/results remain accessible during execution. |
| C12 | Existing collection/navigation/resources/history/run functionality and original draft remain intact; earlier admitted runs retain their definitions and evidence. |
| C13 | Real installed process/MCP demonstration with local deterministic upstream, plus external-component demonstration. Label illustrative model/usage explicitly and preserve failures. |
| C14 | Complete unchanged quality/security/coverage runner passes, alongside new installed acceptance. Owner usability acceptance is recorded separately. |

## Dependency order and owners

Close integration/compatibility/routing/resource contracts and the presentation
contract before source assignments. Parallel development then has three owners:

| Owner | Exclusive packages and files |
| --- | --- |
| A Execution and discovery | New generic composer and external response-marker packages; bundled metadata; backend application/workspace, adapters/workspace/catalog/http, bootstrap workspace composition; tooling/components; their module documents. |
| B Presentation primitives | frontend/api and frontend/ui, including metadata validation, reusable field/schema controls and dialog draft primitives; their module documents. |
| C Product composition | frontend/features/workspace and frontend/app, including read-only inspectors, component-defined dialogs, actual add/replace/remove workflows, source guards and resource configuration; their module documents. |
| Coordinator | Shared contracts and schemas, ADR/process/sprint records, root packaging and quality manifests, graph-view fidelity integration and demonstration setup. |

Only implementation and static checks are released initially. Each owner reports
an acceptance-to-source map and unresolved choices. Coordinator reviews individual
deliveries and their interaction, groups correction tickets, then releases test
assignments. B owns shared API/catalog fixture definitions; C owns browser journeys
and the browser operator server. A owns backend/component/packaging tests. Root owns
whole-run evidence and installed/demo integration. No shared-file concurrent edits.

## Representative public contracts

See [component-owned dialogs](../contracts/component-dialogs.md) and
[configurable composition](../contracts/configurable-composition.md). Consumers use
public API/UI exports only. SourceWorkspaceProps gains optional planComposition
callback supplied by app; other canonical source/field/patch meanings remain.

Representative ordinary input is the existing bounded-review Proposer. Its worker
operation is generate; the response includes status/format/value. A Redirector may
receive the worker's /value through a declared binding. The generic composer
returns status=succeeded, port=<declared>, value=<selected complete result>.
Downstream references to the original /value become /value/value in one plan.
The Redirector determines port; the finite controller determines its destination.
The external marker receives the complete worker reply, changes its text value
according to its own configuration and returns the same envelope shape.

## Verification preparation

Preserve all previously maintained tests; update expectations only for intentionally
changed UI interactions, with equivalent or stronger behavior assertions. Inventory
all affected tests, including names without module prefixes. Before parallel test
expansion, establish metadata fixtures and prove one attach/apply/cancel browser
journey and one installed composition. Check no provider call occurs during describe
or preview. Include request bounds, permission rejection, invalid pointer/port,
child failure, shutdown/cancellation, stale plans, shared-instance effects, removal
after worker edits, exact large integers, keyboard and narrow layouts. Full make
verify and configured installed checks are mandatory without weakened thresholds.
