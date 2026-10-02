# Sprint Status Report — S03

| Document control         | Value                                                              |
| ------------------------ | ------------------------------------------------------------------ |
| Report ID                | SPRINT-S03-001                                                     |
| Report version           | **0.0.3.1** — V0.0, Sprint 3, Revision 1                           |
| Owner                    | Cesar Zea                                                          |
| Reporting date           | 2026-10-02, Europe/Lisbon                                          |
| Sprint                   | S03 — Personal experiment definitions                              |
| Delivery status          | Functional scope delivered and verified locally                    |
| Publication status       | Not yet published; owner review and merge decision remain separate |
| Product package versions | Python: `0.1.0.dev1`; frontend: `0.1.0-dev.1`                      |

This report version identifies a development checkpoint, not a product release.
The [central version register](../../CHANGELOG.md) retains prior sprint reports.

## Delivery summary

Users can import or edit graph JSON, configure registered components, save an
immutable revision and create a manual variant with an exact parent. The library
includes bundled and personal experiments and selects their exact revisions.
Runs retain the admitted definition and earlier results when new revisions are saved.

The [delivery specification](../specification/personal-experiments-sprint.md)
defines scope and acceptance. The [usage guide](../personal-experiments.md)
describes authoring, recovery and execution; the
[library contract](../contracts/personal-experiments.md) defines identity and API behavior.

## Delivered scope and evidence

| Outcome                                                                      | Evidence                                                                                                            |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Raw JSON import, editing, validation and immutable Save; numeric fidelity    | HTTP/client/editor tests and the numeric authoring browser journey                                                  |
| Exact revision selection, manual lineage and atomic replay/conflict handling | Library/SQLite/HTTP tests, concurrent saves and signed pagination cases                                             |
| Saved personal configuration admitted through the existing execution path    | Production preparation with real Sequence/LLMCall and explicitly simulated transport; native SDK request inspection |
| Earlier definitions, results and rendered run graphs retained                | Integration preservation cases and browser execution of a new-ID manual variant before saving its next revision     |
| Dirty, pending, stale and uncertain-save recovery                            | App/editor/API tests and recovery browser journeys                                                                  |
| Strict authorization, viewer write absence, bounded bodies and diagnostics   | HTTP boundary cases; no model calls during authoring                                                                |
| Existing database history preserved by SQLite v6                             | Real v5-to-v6 migration, integrity-checked backup and rollback tests                                                |

The implementation uses the existing graph language, component registry, gateway,
mediation, deadlines and budgets. Component configuration remains schema-governed.
Registered schemas and supported execution profiles constrain admissible graphs;
this sprint does not implement arbitrary new control-flow profiles.

## Verification and demonstration

The complete configured `make verify` runner passed on 2026-10-02: **1,724 Python
tests, 259 frontend tests and 15 browser journeys**, including all static/boundary,
build, CodeQL, accounting mutation and independent coverage gates. Python coverage
is 97.21% lines and 91.61% branches; frontend coverage is 99.27% lines and 93.48%
branches. Both CodeQL suites report no errors or warnings; 90 reviewed Python
notes remain. The [verification record](../verification.md#personal-experiment-delivery--2026-10-02)
retains corrections and limits; surviving accounting mutants are not claimed as killed.

The isolated browser demonstration saves `s03-demo · v1`, executes it with
deterministic participants, saves changed instructions as `v2`, and displays the
retained `v1` result and agent canvas. Its accounting values are simulated.
No provider request or actual provider charge was made for S03 verification.

## Review corrections and limitations

Whole-system review corrected browser numeric conversion and the editor baseline
during post-save selection recovery. Testing corrected boolean input-schema
handling, shared import policy and test fixture/collection issues. The
[C05 process evaluation](../continuous-improvement/cycles/005-personal-experiments/report.md)
classifies these separately and preserves their checkpoint chronology.

Hosted checks and explicit owner review remain publication requirements under the
[single-maintainer review policy](../adr/0012-single-maintainer-review.md).
The next proposed scope is [S04](../specification/sprint-roadmap.md): provider-neutral
selection and a second provider. Evaluation, automatic variants and graphical
authoring remain later scopes; this report does not activate them.

## Revision history

| Version | Date       | Change                                                                                                           |
| ------- | ---------- | ---------------------------------------------------------------------------------------------------------------- |
| 0.0.3.1 | 2026-10-02 | Initial S03 report: authoring, immutable revisions, retained execution, verification and publication boundaries. |
