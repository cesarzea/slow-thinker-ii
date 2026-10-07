# Sprint Status Report — S06

| Document control   | Value                                                           |
| ------------------ | --------------------------------------------------------------- |
| Report ID          | SPRINT-S06-002                                                  |
| Report version     | **0.0.6.2** — V0.0, Sprint 6, Revision 2                        |
| Owner              | Cesar Zea                                                       |
| Reporting date     | 2026-10-02, Europe/Lisbon                                       |
| Scope              | Completion of the product configuration and execution workspace |
| Delivery status    | Locally verified; ready for owner review                        |
| Publication status | Local delivery checkpoint; remote publication pending           |

This development checkpoint follows the owner's review of
[Revision 1](sprint-06-status-report-0.0.6.1.md). It is not a stable product release
or a record of owner acceptance. Report and package versions remain separate in
the [central register](../../../../CHANGELOG.md).

**Subsequent review:** the owner rejected this checkpoint's usability. The
[dated addendum](#usability-review-addendum--2026-10-02) records that outcome and
the resulting audit; the original checkpoint and verification evidence below are
preserved.

## Delivered outcome

Ordinary configuration is organized into **Agents**, **Connections** and
**Task inputs**. Selecting an agent exposes its worker instructions, model,
reasoning, response settings, resources and explicit permissions. Supported graphs
use controls for input mappings, fixed values, optional feedback, sequence order,
conditional routes, Finish destinations, activation limits and final output.
Nested values and schemas have field builders. Advanced JSON remains available
for unsupported extension constructs and import.

The workspace has consistent navigation and responsive forms. Draft changes,
immutable saving and historical run identity retain their existing safeguards.
Results are readable, named node outputs are distinct, and original evidence is
available on request. Terminal results precede collapsed new-run setup.

## Acceptance and verification

The [completion contract](../specification/s06-product-completion.md) defines
U01–U08 within the existing [S06 scope](../specification/s04-s06-delivery.md).
The [usage guide](../workspace.md) describes the delivered controls.

| Acceptance         | Evidence                                                                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| U01, U03, U05, U07 | Form-only browser journey derives a revision, edits instructions/model/reasoning, creates a task schema, retains navigation state at 390 px, saves and executes it. |
| U02                | Composed-agent and resource-option tests cover worker/resource bindings, shared consumers, declared operation compatibility and explicit grants.                    |
| U04                | Conditional-flow browser journey edits feedback, route destinations, activation limits and final output, saves and executes an accepted result.                     |
| U05–U07            | Schema/result unit tests, existing recovery/identity/browser journeys and direct inspection of the live product.                                                    |
| U08                | Mandatory shared verification and the existing paid-run inspection; final evidence is recorded in the verification register.                                        |

Browser inference is deterministic. Separately, the previously completed actual
OpenAI/DeepSeek execution `1a6a889893f54851842a912da1c02554` was opened in the live
application using its original operator credential. Its separate node outputs,
90-minute agenda, USD 96 calculation and USD 0.0002215 recorded cost are visible.
No new provider call or credential change was made for this correction.

The complete shared runner passed **2,204 Python tests, 439 frontend tests and
22 browser journeys**, including CodeQL and all existing mandatory gates.
Frontend coverage is **99.56% lines, 93.86% branches, 99.44% functions and 98.74%
statements**. The [verification record](../verification.md#s06-product-workspace-completion--2026-10-02)
and [sanitized summary](../evidence/s06-product-completion-verification-20261002.json)
retain the evidence and its limits.

## Scope boundaries

Forms support the current finite-sequence and bounded-conditional profiles.
Unsupported extension schemas remain editable as exact JSON. Full graphical
creation, additional execution profiles and evaluation/comparison keep their
existing later sprint assignments. S07 is not activated by this delivery.

## Revision history

| Version | Date       | Change                                                                                                                                           |
| ------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0.0.6.2 | 2026-10-02 | Owner-requested completion: ordinary forms, coherent presentation and readable results; direct live inspection and expanded acceptance evidence. |
| 0.0.6.1 | 2026-10-02 | Initial structured workspace checkpoint; subsequently found insufficient by owner interface review. Preserved as a separate snapshot.            |

## Usability review addendum — 2026-10-02

The owner found the raw node JSON, distant agent editor and configuration language
unsuitable for ordinary use and requested a deep review. S06 is **not accepted as
a usable product workspace**. No package version or historical verification count
is changed by this assessment.

[UX-S06-001](../reviews/2026-10-02-ui-usability/README.md) records live observations,
source-confirmed failure paths, 26 prioritized findings, a control inventory and
12 proposed acceptance scenarios. It identifies disconnected graph/editor selection,
untracked local field edits, unguarded draft loss, a revision-saving dead end,
profile-incompatible controls, model-parameter recovery gaps and misleading
original-result labeling, as well as presentation and comprehension problems.

The earlier delivered-outcome statements need this qualification: safeguards cover
the tested state transitions, not all pending field buffers or experiment changes;
the form surface does not consistently enforce profile applicability; and the
original-response disclosure reconstructs parsed JSON rather than guaranteeing
original source fidelity. Existing passing checks remain evidence for their cases,
not evidence against these findings or proof of user acceptance.

The review made no application changes, started no runs and incurred no new model
cost. Corrections and revised acceptance journeys remain proposals for owner
approval. The next delivery decision should address these gaps before S06 closure;
it does not activate S07 or expand into full graphical authoring.

## Workspace redesign preparation addendum — 2026-10-02

Following the usability rejection, the owner authorized analysis/documentation of
the revised interface. The [S06-UX specification](../specification/s06-workspace-redesign.md)
records full delivery scope, module assignments, public contracts and acceptance.
Graph-version history is functional scope; account/credit visuals remain explicit
demonstrations. This addendum records preparation only. It does not close S06,
change package versions or claim new implementation/test evidence.

## Workspace redesign implementation addendum — 2026-10-02

The owner subsequently activated the goal to complete the redesign. Implementation
is in progress under M06 with exclusive package ownership. The backend and graph,
execution and inspection packages have delivered source for combined review;
authoring and application composition are completing their deliveries. Shared
interface clarifications are recorded in the frontend and history contracts.

Scoped development checks are not delivery verification. The redesigned source
has not yet passed the complete mandatory runner or W01–W14 browser acceptance.
No new paid execution, commit or publication is recorded for this phase. S06
remains open. [C08](../../../continuous-improvement/cycles/008-workspace-redesign/report.md)
records the process separately from product acceptance.
