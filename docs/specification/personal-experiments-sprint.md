# S03 — Personal experiment definitions

| Document control | Value                                                                   |
| ---------------- | ----------------------------------------------------------------------- |
| Sprint           | S03                                                                     |
| Owner            | Cesar Zea                                                               |
| Updated          | 2026-10-02, Europe/Lisbon                                               |
| Status           | Functionally closed; closure publication and owner merge pending        |
| Method           | M06                                                                     |
| Prerequisite     | S01/S02 published; dependency maintenance closed                        |

## Delivery objective

Create, configure and run personal experiments without changing application code.
Import or edit the existing graph JSON, save an immutable revision, create a
manual variant and inspect its execution through the existing agent canvas and
retained evidence. This sprint implements the S03 scope in the
[roadmap](sprint-roadmap.md), not later provider, evaluation or graphical-authoring
sprints.

## Scope and invariants

- Import a local JSON file or edit JSON text. Agent/component configuration remains
  governed by the existing graph and component schemas; no second graph language.
- Preserve `graph_id`/`revision` as exact immutable identity. A changed experiment
  uses a new revision; a manual variant records `derived_from` explicitly.
- Store personal definitions in backend-owned SQLite. Bundled examples remain
  available and previous definitions or saved executions cannot be overwritten.
- Reuse the existing Sequence and bounded conditional profiles, registered
  component types, model gateway, policy references and mediated execution.
- Graphs reference approved provider/resource profiles; credentials and arbitrary
  executable paths do not enter the definition. Model selection stays within the
  current OpenAI profile; S04 adds provider-neutral selection and another provider.
- Validate before saving and repeat runtime preflight before execution. Definition
  validation must describe its scope rather than promise future inputs or provider
  availability. Saving/validating must not make paid model calls.
- The browser selects an exact revision, including when two revisions share one
  graph ID. Unsaved edits cannot silently become a run's admitted definition.
- Keep the canvas agent-focused and all authored text in English. No drag-and-drop
  graph authoring, prompt authoring, scoring or automatic variants in this sprint.

## Existing public dependencies

The [graph contract](../contracts/graphs.md),
[canonical graph schema](../contracts/schemas/graph.schema.json),
[installation contract](../contracts/component-installation.md) and
[operator API](../contracts/operator-api.md) remain authoritative.

`GraphDetail.definition` contains parsed domain JSON for the canvas; authoring
must load raw text through the source endpoint to avoid JavaScript numeric loss.
`structure` and
saved-run `execution` are projections and must not be exported as graph fields.
`InstalledGraphCompiler.compile` remains the effective runtime schema check.
`InstalledWorkflowPreparer` currently reads `BundledDefinitionStore` directly;
replace that concrete dependency with a public raw-definition reader shared by
catalog selection and admission. Keep exact installation/runtime snapshots.

A representative variant copies `single-agent`, changes its revision and
`components.proposer.config`, and records its source in `derived_from`. The graph's
node/controller/resource/permission relationships still use the original schema.
Saving it must leave the parent selectable and any prior run unchanged.

## Preparation closure

The [shared personal experiment contract](../contracts/personal-experiments.md)
resolves canonical equality, bundled/personal collisions, lineage, pagination,
raw JSON handling, transport errors, runtime validation boundaries and editor states.
Public skeletons and each affected module's specification/ticket are prepared.

The representative case copies the raw `single-agent` definition, changes proposer
instructions and revision to `personal-1`, and adds its exact `derived_from`.
The editor sends original text; the validator returns the canonical record; the
service verifies identity/parent and SQLite inserts one immutable row. Listing and
detail return that exact revision; Start resolves it through the same library reader.
Installed preflight freezes changed instructions into the run. A second save with
identical canonical content replays; different content conflicts. Neither changes
the bundled parent or a previous run. This path requires no unresolved shared choice.

Development questions exposed further boundary details: transport rejection codes,
the editor's explicit byte cap, diagnostic-envelope bounds, uncertain post-insertion
responses and selecting a saved identity beyond the first library page. These were
closed in the shared contract before dependent implementation continued. They are
recorded as preparation gaps and clarifications for the M06 cycle evaluation.

## Whole-system review corrections

| ID  | Finding                                                                                                                                                               | Closed correction and owners                                                                                                                                                                                                                       |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R01 | Browser JSON parse/stringify can round large integers or change `1.0` to `1`, violating canonical replay and variant fidelity.                                        | A adds lossless backend draft creation; B adds bounded raw source/draft routes and text-returning client methods; C loads/derives authoring text through those methods.                                                                            |
| R02 | Save installs a new editor baseline before the selected library identity changes; listing failures leave the displayed source associated with the previous selection. | C restores the selected source/baseline after confirmation and retains the saved identity separately until selection changes. Existing `selectedSource` already protects the derivation parent; verification must cover the complete failure path. |

R01 is a preparation gap. R02 is a cross-state review correction. Neither is
functional acceptance evidence. Review the complete correction round before testing.

The coordinator reviewed the complete corrected source/service/client/editor path.
The whole frontend dependency check passed after removing an API type-import cycle.
Testing now establishes shared production-library/browser fixtures before expanding
dependent assignments; passing static checks alone does not close any runtime claim.

Testing correction T01 addresses partial static input checking: JSON Schema true
subschemas remain valid, while false schemas reached directly, through local
references or allOf reject an input that must be present. This includes declared
properties with runtime bindings. Preserve literal/dictionary checks and bounded
diagnostics; do not add general satisfiability inference for unknown runtime values.
The existing JSON Schema contract and execution preflight remain authoritative.

Testing correction T02 registers the already agreed `application.library` public
entry point in the shared dependency policy. Exact public-target exceptions for
adapters/bootstrap retain application descendant protection; a separate library
contract also protects its internals from sibling application modules. Real
negative import probes must confirm that no private path becomes accessible.

Testing correction T07 replaces the coordinator-owned browser fixture's unrelated
`worker.run` activation with the selected saved graph's compiled plan. Sequence
and conditional fixtures must resolve the exact saved identity, schedule declared
nodes and operations, and retain valid node IDs in execution evidence. Use real
programs/controllers with deterministic participant results; retain simulated
charges and existing wait/cancellation modes. Do not change production response
schemas or generic coordinator fixtures. C strengthens historical browser checks
to require a rendered agent canvas without loading errors, including a run of a
manual variant with a new graph ID and preservation after another revision is saved.
This corrects a shared-fixture omission and insufficient browser assertions.

Other verification corrections were T03 (unused test helper exports), T04
(an ambiguous brace-prefix expression in a JSON test fixture), T05 (duplicate
Python test-module names during complete collection) and T06 (an existing drag
test used coordinates below the viewport after the authoring panel was added).
These affected fixtures, test integration or gate policy. No quality threshold,
production schema, accounting control or security suppression was relaxed.

## Testing assignments

| Owner       | Exclusive tests and acceptance responsibilities                                                                                                                                                                                                                                                                                                                            |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Coordinator | Shared `support/personal_library.py`, browser execution/snapshot and OperatorServer composition; first production HTTP save/source/draft/replay case and representative browser case; complete verification and failure classification.                                                                                                                                    |
| A           | Library, catalog validator, SQLite v6 and preparation tests; canonical/concurrent replay and conflicts, fixed signed pages, every supported profile, lineage and exact unusual revisions. Execute a saved definition's production prepared program/policy with real Sequence/LLMCall and simulated transport; retain earlier admitted snapshot/result after new revisions. |
| B           | HTTP definition/Start boundary and frontend API tests; strict bodies/queries/auth/viewer absence, full response and 4096-byte diagnostic bounds, numeric source/draft fidelity, exact reply identities, cancellation/timeouts and uncertain-save classification.                                                                                                           |
| C           | App/editor component and browser journeys; raw load/import/edit/validate/save/select/reload/Start, revision disambiguation, lineage, dirty/pending/stale/uncertain states, saved selection pagination/recovery and historical inspection. Update affected public selector expectations in existing journeys.                                                               |

Use existing real SQLite and component support contracts. Preparation fixtures have
synthetic description installations, not executable LLM implementations: explicitly
substitute a simulated runtime environment for the prepared program/policy rather
than claim those packages launch inference. Record native SDK requests from the real
LLMCall. Browser journeys use production HTTP/storage with deterministic operations;
they do not establish provider behavior. No paid provider calls are required.

| Owner       | Exclusive development assignment                                                                                                         |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| A           | Application library and exports; catalog validator; SQLite v6/repository; preparation reader; bootstrap composition.                     |
| B           | HTTP definition routes and compatible Start identities; frontend API client/schemas/exports.                                             |
| C           | Frontend app/catalog selection; definition-editor feature; execution dirty-state gating.                                                 |
| Coordinator | Shared contracts and source-location policy; interface/whole-system review; shared acceptance composition; progress and process records. |

Testing ownership follows those same packages after development and whole-system
review. Shared integration fixtures and policy files have one coordinator owner.
Implementers may split private helpers/files within their declared responsibility;
they must report a missing cross-package decision before changing the contract.

## Expected package assignments and verification

Prepare exclusive assignments around the backend definition/persistence/composition
packages, HTTP/client boundaries, and browser application/editor feature. Existing
[boundary rules](../architecture/module-boundaries.md) prohibit sibling-feature
imports; the application composes editor, canvas and execution through public APIs.
Shared root schemas, source-location policy and test fixtures have one owner.

Plan acceptance for import/edit/save/reload, two revisions with the same graph ID,
manual lineage, exact prior-run preservation, invalid configuration/references,
identity conflicts, unauthorized or oversized writes, uncertain-response recovery,
and execution of a saved personal graph with the existing simulated provider.
Prepare one representative composition before expanding tests. All mandatory
`make verify` gates, independent coverage thresholds, browser journeys, CodeQL and
accounting checks remain required. A paid demonstration is unnecessary for S03.

## Delivery acceptance register

| ID     | Required outcome and authoritative evidence                                                                                                             |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S03-01 | Import/edit/save/reload a canonical graph and preserve changed agent configuration: browser journey plus persisted exact detail.                        |
| S03-02 | Execute the saved personal revision through production preparation and simulated provider: integration run and recorded changed prompt/input.           |
| S03-03 | Select two revisions sharing a graph ID and preserve their independent definitions: API and browser tests.                                              |
| S03-04 | Canonical replay, concurrent saves and occupied identity conflicts are atomic: application/SQLite/HTTP tests.                                           |
| S03-05 | Manual variants retain a known exact parent; missing/self parents fail: stored lineage and rejection tests.                                             |
| S03-06 | Bounded signed pages retain the original insertion window across new saves: paging, invalid-cursor and refresh tests.                                   |
| S03-07 | Strict JSON, schema/configuration/reference/profile validation and safe diagnostics reject invalid definitions without calls: validator and HTTP tests. |
| S03-08 | Authorization, viewer write absence and request/response limits remain effective: HTTP boundary tests.                                                  |
| S03-09 | Schema-valid unusual revisions survive save/detail/Start unchanged: public-boundary tests.                                                              |
| S03-10 | New revisions cannot alter old admitted definitions/results: saved-run preservation integration evidence.                                               |
| S03-11 | Dirty drafts cannot start a run; stale replies and uncertain saves have safe UI recovery: component/browser tests.                                      |
| S03-12 | SQLite v5 to v6 retains old data and verified backup: migration tests.                                                                                  |
| S03-13 | Complete mandatory local verification passes; hosted checks pass before merge: make verify log and PR check state.                                      |
| S03-14 | English usage instructions, version/changelog, formal sprint report and separate M06 cycle evaluation match delivered behavior: reviewed documents.     |

Completion requires every outcome, a working demonstration and the mandated
verification. A development receipt or interface skeleton does not satisfy delivery.

## Local delivery checkpoint — 2026-10-02

All functional acceptance cases and the complete configured `make verify` runner
passed. The browser demonstration retains the rendered `v1` run after saving `v2`.
The [S03 report](../progress/sprint-03-status-report.md) and
[verification record](../verification.md#personal-experiment-delivery--2026-10-02)
record evidence and limitations. Hosted checks must pass before merge; explicit
owner review and merge authorization remain separate from local verification.

## Functional closure — 2026-10-02

Following the owner's requested real execution and review, the S03 functional
scope is closed. The [live validation](../progress/sprint-03-live-validation.md)
adds actual OpenAI request/response, feedback provenance, history, outcome and cost
evidence to the original simulated acceptance. All required implementation checks
on [PR #11](https://github.com/cesarzea/slow-thinker-ii/pull/11) passed for `b806140`.
The [closure report](../progress/sprint-03-status-report.md), version `0.0.3.2`,
separates this completed scope from the still-pending publication of the supplement
and owner-authorized merge. No later sprint is activated by this closure.
