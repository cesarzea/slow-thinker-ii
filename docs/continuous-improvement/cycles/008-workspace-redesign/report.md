# C08 — S06 workspace redesign

| Document control           | Value                                                                      |
| -------------------------- | -------------------------------------------------------------------------- |
| Document ID                | C08                                                                        |
| Status                     | Locally verified; owner usability review pending                           |
| Record owner               | Cesar Zea                                                                  |
| Recorded date and timezone | 2026-10-03, Europe/Lisbon                                                  |
| Method                     | [M06](../../methods/006-delivery-preparation.md)                           |
| Product scope              | [S06 workspace redesign](../../../archive/previous-implementation/specification/s06-workspace-redesign.md) |

## Context and hypothesis

The owner rejected C07's workspace usability. The authorized redesign retains
S06 and its runtime/accounting invariants. Preparation defines complete contextual
navigation, controlled draft state, declarative component presentation, version
history and exact retained evidence. The hypothesis is that explicit state ownership
and whole ordinary journeys will reduce the previous integration defects. M06 is
unchanged; no efficiency improvement is assumed.

## Measurement basis

[Observations](observations.json) record direct UTC clock samples, not a reconstructed
activity audit. The first sample below occurred during development and excludes
initial analysis, document preparation and interface handoffs. Participant activity
overlaps; it cannot be summed as elapsed delivery time. Full-chat goal usage is
not a reliable category-level activity measurement. No completion duration, pause
adjustment or causal time saving is reported while delivery remains active.

## Delivery and process results

Three implementers own backend, authoring and product-shell packages exclusively.
The coordinator implements the observation packages while reviewing shared
interfaces. Public skeletons were reviewed before private functional code; new
operations initially failed explicitly rather than pretending to work. Functional
verification remains reserved for the combined-review/testing phase.

Shared handoffs needed further closure: preview's wire envelope, presentation
warnings and null semantics, comparison response ceilings, import source initialization,
post-flush source reads, and explicit URL run selection. These are preparation gaps;
they are recorded rather than attributed to implementer speed. A model-field gap
was identified against the actual model-provider schema: both provider profile and
model name are required. A declarative model pointer closes that handoff without
client type-name inference. The contract revision preserves existing descriptor bytes.
Further handoffs resolved structural command preparation, opaque route selection,
field representation switching and credential-lease invalidation. These are
additional preparation gaps, not evidence of local implementer shortcomings.

After the backend source delivery, its slot was reassigned to an independent
review of the coordinator's observation implementation. That review corrected
resource visibility, historical metadata precedence, retained execution lifetime,
focus behavior and geometry. Combined review also identified a voluntary disconnect
that bypassed the draft guard and an unknown-save recovery reference that could
disappear during navigation. Corrections are required before testing; they are
product/composition defects found by source review. A type-only history dependency
cycle was corrected without changing its behavior or weakening boundary rules.

The authoring assignment was rebalanced at an explicit ownership cutoff: backend
delivery's implementer took the complete definition-editor and experiment-library
packages for independent review and corrections, while the original authoring
implementer retained workspace forms/commands. No simultaneous writers were
authorized for those packages. Review identified obsolete immediate-preview
publication and derivation from an unpromoted saved reference; these are product
lifecycle defects to correct before functional testing.
Combined composition review subsequently found confirmed saves remounting the
authoring session, loss of buffered agent selection, and selected-run URLs not
following an admitted new start. Stable working-context keys, separate preview
selection and receipt-origin navigation address these existing requirements. The
observation assignment independently reviews the coordinator's final corrections
before testing. Their effectiveness remains unverified at this checkpoint.

Scoped TypeScript/Python/lint checks validate declarations and implementation form;
they do not establish functional delivery. The supported bundled Node 24 runtime
was located; default system Node 23 must not supply the final verification gate.
No provider calls, publication or commits occurred during this recorded stage.

### Testing checkpoints — 2026-10-03

Combined source review closed before testing was released at 23:24:06 UTC on
2026-10-02 (00:24:06 Europe/Lisbon on 2026-10-03). The production SQLite/HTTP
draft-save and legacy-history representatives passed first. The production-catalog
browser case then edited an ordinary prompt and saved a distinct immutable
revision while proving the template remained unchanged. These are scoped
composition checks; mandatory verification and W01–W14 remain pending.

Initial failures include distinct categories. Environment corrections supplied
repository-local cache paths and the existing matching Chromium installation;
no browser-version downgrade or verification rule change was required. Fixture
corrections addressed migration versions, namespaced extension keys, row equality,
template inventory and helper typing. Expectation corrections replaced obsolete
Apply/save selectors, updated promoted-save behavior and waited for asynchronous
state transitions. Product corrections blocked editing/actions received during
initial source loading and repaired declarative generation controls whose native
schema was unconstrained, absent nested parent initialization and duplicate
configuration controls for composed resources. Regression verification is in
progress. Subsequent browser cases found two composition defects: Save-and-continue
was waiting for a stale rendered dirty state after a confirmed save, and Start
received an unavailable reason even when its explicit blocking flag was false.
The fixes use the save receipt to finish the guarded action and supply a reason
only for blocked execution. Focused browser regressions pass. Direct demonstration
then found a mounted history list that did not refresh its scope after a confirmed
save, despite comparison already using the promoted reference. The library scope
now includes that reference revision; its regression passes. A development
StrictMode replay also left the import controller aborted; its lifetime correction
and scoped browser regression subsequently passed.

Two bounded usability corrections remove misleading empty residual-group messages
and replace an unavailable reasoning textarea with a compact disabled selector.
Selection of an activation exposed a fifty-row event table preceding its selected
evidence in the adjacent pane; selected evidence now precedes that table and its
focused regression passes. Further browser testing found that navigation unmounted
global settings and lost the frozen uncertain command. Retaining that module within
the credential lifetime corrected the defect; its browser recovery regression passes.
These are concrete delivery defects, not new runtime capabilities. Two remaining
browser failures were interaction expectations: a native select needed actual focus
before blur, and a buffered checkbox needed asynchronous confirmation. Both scoped
corrections pass; the complete runner remains authoritative for the final count.

The backend implementer handed off a running full-suite process at completion;
the coordinator could not resume that process and its log stopped advancing.
That partial log is not a passing receipt. The first coordinator-owned mandatory
runner passed Python static checks and frontend typing, then stopped at six
browser-test lint errors. These are test-authoring errors, not waived checks;
they were corrected before resuming through `make verify`. The next run stopped
at unused exports/types: genuinely private symbols became local and public contracts
received typed consumers in actual fixtures. No exclusion or suppression was added.
A further run stopped at formatting in three updated tickets, which was corrected.
The coordinator owns the final shared runner through completion. This is a runner handoff limitation, not a
reported product defect. Participant overlap remains unsuitable for summed effort
totals.

## Evaluation checkpoint before final verification

Delivery, whole-system review and W01–W14 verification remain pending. It is too early
to assess the method or compare C08 with C07's checkpoint. Record later review and
test corrections by product, fixture, expectation, command or environment category.

## Next-cycle decision

No new method or process proposal is approved here. Continue M06 through review,
corrections and mandatory local verification before evaluating the outcome.

### Coverage correction checkpoint — 2026-10-03

The complete Python run passed 2,280 tests in 338.20 seconds. The following
frontend run found a comparison test waiting for a mounted region rather than
its asynchronous numeric content. The correction retains exact-number assertions.
A subsequent scoped source assertion initially matched two identical fixture
snapshots; its plural assertion now verifies both. The coordinator prematurely
restarted the mandatory runner before inspecting that scoped result, then stopped
the known process. This is a coordinator sequencing error, not a product defect
or a passing verification receipt.

The corrected complete frontend suite passes 574 tests, but its coverage is
88.92% statements and 81.89% branches, below the existing 90% requirement.
Browser journeys do not supply Vitest unit coverage. In particular, creation,
navigation guards and generic configuration edge paths need unit/composition
coverage. This is incomplete test delivery and a planning/verification gap;
passing scoped tests did not establish the required shared threshold. Grouped
module tickets now assign meaningful supported-behavior and failure-path tests
with exclusive ownership. No threshold, exclusion or instrumentation is weakened.
The stopped runner's Python and CodeQL outcomes are retained as checkpoint
evidence, while the final complete runner remains required.

### Coverage correction delivery — 2026-10-03

Exclusive assignments added contract-level unit/composition coverage for template
creation, opaque routes, selection, Save/Discard/Cancel, command lifetimes, exact
import limits, reasoning repair, private configuration, mappings/deletion and
execution receipts. Production source did not change in this test-expansion phase.
The combined frontend preflight passes 747 tests with 96.04% statement, 90.70%
branch, 97.02% function and 97.26% line coverage. All original thresholds apply.
Individual diagnostic branch gains support selecting focused cases but do not
replace this authoritative combined report. The final mandatory runner remains
pending at this checkpoint.

## Final technical delivery — 2026-10-03

The coordinator-owned unchanged `make verify` completed with exit code 0 at the
01:08:40 UTC observation: 2,280 Python tests, 747 frontend tests and 33 browser
journeys pass. Frontend coverage independently meets all four original thresholds;
Python line and branch coverage independently exceed 90%. CodeQL records no errors
or warnings, with 100 Python informational notes. Accounting mutation results are
141 killed, 58 surviving and one timed out; success of the existing runner does
not establish complete mutation effectiveness. The [sanitized evidence](../../../archive/previous-implementation/evidence/s06-workspace-redesign-verification-20261003.json)
and [S06 report](../../../archive/previous-implementation/progress/sprint-06-status-report.md) preserve scope and limits.

An isolated production HTTP/SQLite composition demonstrated an ordinary prompt
edit and immutable save, refreshed version history/comparison, guided resource
configuration and a four-activation simulated proposer/reviewer feedback run.
Manual desktop inspection measured 1440×900 CSS pixels and keyboard focus
restoration; automated browser coverage includes 390×844. Actual new provider
cost was zero. Owner usability acceptance and publication remain pending.

## Final evaluation and measurement limits

Exclusive package assignments and ownership cutoffs prevented simultaneous edits.
Representative application/storage and production-catalog browser cases established
composition before dependent test expansion. Combined review and browser verification
found real lifecycle defects that scoped declarations could not establish. These
are observed benefits of the controls, not evidence that delivery became faster.

Preparation still omitted shared state transitions, exact dependency payloads and
lifetime behavior that required coordinator decisions during development. Source
review and browser testing then required repeated corrections. Test handoff also
failed to establish complete frontend coverage before the expensive shared runner;
its first passing functional suite remained below the mandatory branch threshold.
Grouped behavior tests corrected that gap without changing production source,
coverage exclusions or thresholds. Lint, unused-symbol, formatting and asynchronous
expectation errors caused further avoidable restarts. The coordinator's premature
restart before inspecting a scoped result is separately retained above.

The observed checkpoint span from 22:09:23 UTC to 01:08:40 UTC is **2 h 59 min
17 s**. It excludes initial analysis, preparation and handoffs and is not an
activity-duration audit or a complete sprint duration. Pauses are not reconciled;
parallel participant activity cannot be summed into this span. No category-level
effort, causal productivity improvement or valid comparison with C07 is established.
The final observations identify the evidence that is available rather than filling
measurement gaps with estimates.

## Decision at technical closure

M06 remains unchanged. No new method, future sprint or publication is activated.
The next evaluation should retain preparation omissions, product/fixture/expectation
failures, expensive corrective restarts, verified usability and complete elapsed
measurement. In particular, scoped passing tests must not be mistaken for complete
coverage or full delivery. The owner reviews product acceptance separately.

## Owner usability rejection — 2026-10-03

The owner explicitly rejected the delivered redesign and instructed continued S06
work. The final technical results and measured checkpoint span above are preserved.
They do not establish visual fidelity or owner acceptance. The comparison against
the actual last concept exposes excessive canvas/inspector whitespace, absent model
presentation for historical metadata and weak action/navigation hierarchy. These
are delivery/preparation defects, not evidence that the implementers lacked speed.
The [C09 correction](../009-s06-fidelity/report.md) applies M06 without changing it.
