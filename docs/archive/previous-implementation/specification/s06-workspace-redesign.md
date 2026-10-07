# S06 — Usable experiment workspace

| Document control | Value                                                                                                                                                       |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ID / revision    | S06-UX / 1                                                                                                                                                  |
| Date / owner     | 2026-10-02 / Cesar Zea                                                                                                                                      |
| Status           | Fidelity correction locally verified; owner usability acceptance pending                                                                                       |
| Method           | [M06](../../../continuous-improvement/methods/006-delivery-preparation.md)                                                                                        |
| Evidence         | [Usability review](../reviews/2026-10-02-ui-usability/README.md), [owner requirements DR01–DR14](../reviews/2026-10-02-ui-usability/design-review-notes.md) |

## Objective and authority

Complete S06 by letting the owner configure, version, run and understand supported
agent collaborations without editing JSON for ordinary tasks. This is a correction
and completion of S06, not a replacement for S07 evaluation. Earlier technical
verification remains historical evidence; it does not accept this delivery.

The owner initially authorized analysis and documentation after reviewing the
interface concept, then explicitly activated the goal to complete S06. This
specification governs that implementation and its verification. Preparation
records describe their original checkpoint; they are not current delivery evidence.
Paid runs and publication retain their separate authorization and budget limits.

## Complete delivery scope

- Experiment collection: search the complete collection, create from an available
  template, import, open and derive a variant; one row per experiment, not revision.
- Contextual Design, Resources, Versions, Runs and Experiment settings navigation;
  separate global Component library and Workspace settings.
- Full-width graph and adjacent selected-object inspector. Forms configure the
  existing sequence and bounded-conditional profiles. The toolbar launches guided
  Add agent, Add resource and Delete dialogs; it is not a drag-to-connect editor.
- One controlled draft for all forms and advanced source. Save creates an immutable
  revision; unsaved fields participate in dirty, navigation and execution guards.
- Declared component composition, compatible private/shared resource bindings and
  explicit permissions, including generic forms for external installed types.
- Version history, historical viewing, definition comparison and a new draft from
  an earlier revision. Runs remain attached to their admitted revision.
- Task inputs, sessions, effective limits, Start/Stop/recovery, experiment-wide
  run history, final/intermediate results and optional exact evidence inspection.
- English product copy, keyboard access, responsive layout and truthful states.
- An explicitly illustrative account/credit footer: horizontal consumption bar,
  small figures below, no real account actions or credit transactions.

Exclude credit economics, account management, installations from the browser,
provider-secret editing, graph nesting, new execution profiles, automatic influence
or quality evaluation, paid validation and direct graphical connection editing.
Keep real USD accounting and its existing limits visible in execution/settings.
Do not add undocumented defaults or new spending allowances.

## Governing contracts

| Contract                                                             | Decisions owned                                                                      |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [Interaction](../contracts/workspace-interaction.md)                 | Navigation, selection, save lifecycle, graph commands and user states                |
| [Read APIs and history](../contracts/workspace-history-api.md)       | Collection, revisions, comparison, preview, run filters, migration and wire examples |
| [Component presentation](../contracts/component-presentation.md)     | Optional metadata, generic fallback, composition and exact-version compatibility     |
| [Frontend interfaces](../contracts/workspace-frontend-interfaces.md) | Public interface sketches, state ownership and cross-feature handoffs                |
| [ADR 0013](../../../adr/0013-workspace-authoring-state.md)                 | Draft, saved revision and execution separation; consequences and alternatives        |

These documents supersede conflicting presentation, per-field Apply and editor
save-baseline clauses in the earlier S06 specifications. Existing runtime,
accounting, source fidelity, authorization and uncertain-command contracts remain.
No consumer should infer new execution capabilities from presentation metadata.

## Exclusive implementation assignments

Assignment IDs describe responsibility, not running agents. During development,
launch independent assignments in parallel only after reviewing public interfaces.

| Owner             | Whole module/package ownership                                                                                                                                | Dependencies                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| A — Backend       | `backend/src/slow_thinker_ii/application` (including library/workspace); `adapters/http`, `adapters/sqlite`, `adapters/workspace`; `bootstrap`; backend tests | Existing domain and catalog public APIs; history and presentation contracts     |
| B — Authoring     | `frontend/src/features/definition-editor`, `features/workspace`, new `features/experiment-library`; their feature tests                                       | Reviewed API and UI interfaces; fixtures can precede actual HTTP implementation |
| C — Product shell | `frontend/src/app`, `api`, `ui`; their tests and shared browser harness                                                                                       | Backend wire contracts and feature public interfaces                            |
| D — Observation   | `frontend/src/features/graph-view`, `execution`, `inspector`; their tests                                                                                     | API contracts, controlled graph selection and UI primitives                     |
| Coordinator       | Shared contracts, architecture, roadmap, location/boundary configuration, `docs/workspace.md`, delivery review and shared verification orchestration          | Receipts from A–D                                                               |

Application subpackages remain encapsulated despite common ownership. No assignment
edits another's directory or the shared configuration files. Product-shell styles
belong to C; existing feature styles stay with the owning feature. Agree classes
and public props here, not by importing a sibling feature's internals.

### Ownership handoff — 2026-10-03

During source review, A took the complete definition-editor and experiment-library
packages from B; B retained workspace forms and commands. The transfer used an
explicit cutoff with no concurrent writers. Source delivery is now under final
combined review. For verification, A owns backend source, test fixtures and tests;
B owns workspace source and feature tests; C owns app/API/UI source, their tests,
shared browser fixtures and every browser journey. The coordinator owns the
definition-editor and experiment-library packages and their tests, including
`tests/support/editor-model.ts`, `editor-view.tsx`, `editor-session.tsx` and
`experiment-library-view.tsx`. D owns graph-view, execution
and inspector source and tests when its verification assignment is released.
Shared fixture changes remain with C, except those editor/library helpers. This
allocation supersedes the original development ownership without rewriting it.

Implementers may choose private file names, algorithms and local helpers within
the contracted bounds. New generic frameworks, public dependencies, source
boundaries or runtime behavior are not local choices. Respect existing file-size,
complexity, strict typing and public-entry-point gates. Subdirectories group real
responsibilities; do not create catch-all helpers to evade limits.

## Acceptance matrix

| ID  | Observable acceptance                                                                                                                                                                 | Owner / audit trace                      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| W01 | Collection search covers every page; open one experiment, navigate sections and return without confusing global and experiment scope.                                                 | C/B/A; UX02, UX07                        |
| W02 | Click Reviewer; its inspector, prompt, selection and preview all refer to Reviewer. Reused instances show all affected steps before editing.                                          | B/C/D; UX01                              |
| W03 | Type in an ordinary field without Apply, navigate away and back, and save exactly that value. Invalid text survives; late responses do not discard edits.                             | B/C; UX03–UX05                           |
| W04 | Edit an existing revision and save a new one without an identity conflict. Lost save replies recover by the same frozen source; old runs are unchanged.                               | A/B/C; UX05, UX24                        |
| W05 | Expand a long prompt, edit, collapse and save the same value; keyboard focus returns to the expansion icon.                                                                           | B/C; DR06, DR08                          |
| W06 | Add/configure an agent, internal component or compatible resource through forms; unsupported slots are explained. Bindings and grants remain separate.                                | A/B; UX09–UX13, UX26                     |
| W07 | Configure sequence order/mappings and bounded-review feedback/Finish without offering invalid profile-specific choices. Delete reports every affected reference.                      | B; UX06, UX14–UX16                       |
| W08 | Resource layer shows a shared instance once and only configured consumers; dashed lines meet plain card borders. Toolbar toggles, arrows and polling geometry remain correct.         | D/C; DR04, DR07, DR11                    |
| W09 | Versions shows complete saved history; compare two revisions including large numbers and prompt changes; derive from an older revision without modifying it.                          | A/B/C; DR14                              |
| W10 | Configure task fields, select/create a session, understand blocking limits, run, stop and recover using authoritative command state.                                                  | B/C/D; UX17–UX19, UX24                   |
| W11 | Runs lists all sessions for the experiment; selecting an old run displays its admitted graph and exact result, not the current draft. Evidence opens next to the selected activation. | A/C/D; UX19–UX25                         |
| W12 | Generic external components remain configurable without client type-name branches; malformed presentation metadata falls back safely.                                                 | A/B/D; UX10–UX12, UX26                   |
| W13 | Account/credit preview is visibly illustrative; no balance changes, account API calls or attribution to a fake user occur.                                                            | C; DR09–DR13                             |
| W14 | Core journeys work by keyboard and at 1440×900 and 390×844; no document overflow or hidden selected editor; English authored copy throughout.                                         | C and all owners; UX02, UX07, UX18, UX23 |

## Development, review and testing phases

1. Review the interface sketches and representative handoff cases, then implement
   A–D with exclusive ownership. Each receipt maps W IDs to changed code, important
   local choices and pending verification. Development delivery is not acceptance.
2. Review individual deliveries and the complete journeys, including failures.
   Write grouped correction tasks in the affected module's `todo.md`; repeat until
   the whole delivery appears coherent. Do not reopen unaffected architecture.
3. Finalize test tickets from W01–W14. C owns shared typed fixtures, renderer mocks
   and browser harness; A owns HTTP/SQLite fixtures. Verify one draft/save composition
   and one migrated revision-history case before parallel test expansion.
4. B tests field buffering, composition and version UI; D tests geometry, retained
   evidence and recovery; C tests navigation, accessibility and owner-facing browser
   journeys; A tests real application/HTTP/storage boundaries and migrations.
5. Run affected tests, classify product/fixture/expectation/environment failures,
   group corrections, and resume via the same configured entry points. Finish with
   `make verify`, including existing CodeQL, coverage, boundary and dead-code gates.
   Do not weaken thresholds or use uncontrolled provider calls to satisfy tests.
6. Demonstrate W01–W14 in the local browser with existing saved evidence or simulated
   providers. Update the workspace guide, verification and sprint report with actual
   results. Owner review remains distinct from passing technical gates.

Fixtures must include legacy missing dates, branched/cross-experiment lineage,
multiple history pages, concurrent saves, lost responses, malformed presentation,
unknown fields, exact large numbers, missing permissions and multiple activations.
No completion dates or effort savings are claimed from this preparation. Evaluate
M06 after delivery using observed preparation, rework, review and test evidence.

## Delivery checkpoint — 2026-10-03

The [Revision 3 sprint report](../progress/sprint-06-status-report.md) maps W01–W14
to mandatory verification and local demonstration evidence. Technical delivery is
complete; owner acceptance and publication remain separate decisions.

## Owner review follow-up — 2026-10-03

The owner rejected the local S06 redesign. Its technical evidence remains historical;
S06 stays active under the [bounded fidelity correction](../reviews/2026-10-03-s06-fidelity/README.md).
No later sprint or publication is activated.

## Fidelity delivery follow-up — 2026-10-03

[Report 0.0.6.4](../progress/sprint-06-status-report.md) records the completed
bounded correction, actual desktop/narrow demonstrations and unchanged complete
mandatory verification. Earlier rejection and technical checkpoints remain
preserved. Owner usability acceptance and publication are still pending.
