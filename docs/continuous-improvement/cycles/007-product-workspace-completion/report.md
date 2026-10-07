# C07 — S06 product workspace completion

| Document control | Value |
| --- | --- |
| Document ID | C07 |
| Status | Locally verified; owner review pending |
| Record owner | Cesar Zea |
| Recorded date and timezone | 2026-10-02, Europe/Lisbon |
| Method | [M06](../../methods/006-delivery-preparation.md) |
| Product scope | [S06 completion](../../../archive/previous-implementation/specification/s06-product-completion.md) |

**Subsequent outcome:** the owner rejected this checkpoint's usability. See the
[dated follow-up](#owner-usability-review-follow-up--2026-10-02). Original timing,
verification and delivery statements remain preserved as checkpoint evidence.

## Context and hypothesis

The owner found the original S06 workspace too technical for ordinary agent and
graph configuration. C06's tests established functional behavior but did not
establish product usability. The owner authorized completing the existing scope.
This cycle records that rework; it is not a new sprint or additional capability.
The [C06 follow-up](../006-provider-resource-workspace/report.md#owner-interface-review-follow-up--2026-10-02)
preserves the original finding and measurements.

M06 remained the approved method. Preparation explicitly added screen hierarchy,
ordinary journeys, advanced disclosures and rendered acceptance criteria. The
working hypothesis was that these details would reduce further implementation
ambiguity and prevent another premature product handoff.

## Measurement basis

[Structured observations](observations.json) retain preparation, implementation
handoff and test-readiness timestamps. The first saved activity observation was
11:18:13.798711 UTC; it is not the beginning of the complete user turn. Earlier
reading/preparation is outside that observation window. Implementation assignments
were launched at 11:23:21.117395 UTC; whole-source review and test preparation were
recorded at 11:42:16 UTC.

The final shared-verification confirmation was recorded at 12:09:58 UTC. The
observed span is **51 min 44 s**, excluding earlier preparation and later closing
documentation/delivery. These are checkpoint boundaries, not a reconciled activity audit. Development and
review overlap across participants. No owner-response pause was required; tool
execution, verification waits and documentation remain inside the recorded span.
Accumulated participant activity and exclusive analysis/coding/testing durations
were not measured. No such totals or causal time-saving claim are inferred.

## Delivery and process results

The coordinator specified U01–U08 and public dependency/data paths, then assigned
three exclusive module groups. Implementers delivered form primitives,
configuration, and presentation separately. Source review preceded functional
testing. One representative production HTTP/storage authoring journey and the
source parser fixture suite passed before dependent test work expanded.

Source review corrected exact integer-exponent validation, recognized result
wrappers that could discard sibling fields, source-conversion metadata and
composed-agent presentation. These were reviewed within the agreed contracts.
The completed product exposes agent configuration, task schemas, mappings and
routes through forms while retaining exact JSON as an advanced path.

| Classification | Finding and correction |
| --- | --- |
| Product accessibility | Response-field help text changed its accessible name; an associated label and separate description corrected it. |
| Product integration | A configuration CSS class collided with graph node styling; separate names now isolate both. |
| Product suggestions | Contextual and routed worker outputs have different nesting; declared operation schemas now guide suggested paths. |
| Product usability | Profiles with identical provider/model labels could not be distinguished; identifiers now disambiguate them. |
| Static gate | A formerly consumed public type became unused; it was made internal without changing runtime APIs. |
| Existing test expectations | New disclosures and configuration sections required visible-section selection; jsdom cannot prove closed-details visibility. Browser assertions retain that responsibility. |
| New test preparation | The coordinator's new browser test initially confused adapter/profile IDs, assumed an existing optional task schema, and used unscoped labels. Correct fixture data, explicit schema creation and accessible-role queries resolved these. |
| New test timing/representation | Required-field changes are server-confirmed; the test now waits for confirmed state. Saved key ordering and result casing were corrected in expectations. |
| Environment | A stale development import was cleared by reload. A browser viewport command timed out; automated 390 px journeys supply narrow-layout evidence. |

The form-only and conditional-flow browser cases execute saved immutable revisions
through real local HTTP/storage with deterministic inference. The previously paid
OpenAI/DeepSeek run was separately inspected in the live product using the original
credential, with no new provider spending. Readable results and original evidence
were both retained.

The final [shared verification](../../../archive/previous-implementation/evidence/s06-product-completion-verification-20261002.json)
passed 2,204 Python tests, 439 frontend tests and 22 browser journeys, together
with the unchanged static, security, coverage, build and mutation gates.

## Evaluation and limitations

The source review found and corrected defects before testing, but test preparation
was still incomplete. The first shared journey covered existing authoring, not the
new schema-creation and profile-selection interactions; avoidable coordinator
fixture and locator corrections followed. Passing isolated module tests also did
not prevent the CSS namespace collision. These findings limit any claim that M06
has eliminated rework.

This correction changes an already implemented frontend and preserves backend
contracts, so its scope cannot be compared directly with C06's provider/resource
implementation. Test counts, elapsed checkpoints and parallelism do not establish
an efficiency gain. The useful evidence is the verified user journeys, classified
rework and direct product inspection.

## Next-cycle decision

M06 remains unchanged. For this delivery, visible acceptance was checked alongside
contract tests under existing whole-system review obligations. Earlier P11–P13
remain proposals; no new method is approved here. A future preparation improvement
would use one representative case for each materially different form path,
including creation of missing schemas and asynchronous field confirmation, before
expanding dependent browser tests. This is a recommendation for owner review,
not an adopted process rule.

## Owner usability review follow-up — 2026-10-02

The owner rejected the delivered interaction: selecting an agent exposed raw node
JSON, its editor appeared far below, and the configuration was difficult to
understand. The subsequent [formal review](../../../archive/previous-implementation/reviews/2026-10-02-ui-usability/README.md)
examined the live workspace and relevant source without modifying product data.
Its 26 findings distinguish direct observations from source-confirmed paths and
inferred user consequences. S06 usability acceptance remains unmet.

This contradicts the hypothesis that the added screen hierarchy and journey
specification had prevented another premature handoff. Visible controls and passing
scripted journeys did not establish a coherent user workflow. Whole-system review
missed selection disagreement, separate unapplied field state, unsafe navigation,
revision-order dependence and execution-profile mismatches. Original-result
fidelity was checked too locally: a source-preserving renderer cannot recover
precision already lost while fetching data.

These findings concern preparation, review and acceptance coverage, not merely
styling or implementer speed. They provide no new timing measurement and do not
show that parallel development caused the defects. The 51 min 44 s checkpoint
span remains unchanged; audit and further correction effort lie outside it.

Proposed improvement: review complete ordinary journeys before handoff, including
select → edit → navigate → save → execute → inspect, and their interruption and
recovery paths. Check every materially different execution profile and component
composition. Assess whether a user can explain a control's effect, shared impact
and saved state, instead of treating field presence or a passing script as sufficient.
The review's 12 scenarios make this proposal concrete; they supplement rather than
replace existing technical gates.

M06 remains the approved method. This follow-up approves no new method, runtime
change or later sprint. Earlier P11–P13 remain proposals. The formal review and its
control inventory are the detailed evidence for an owner decision about corrections.
