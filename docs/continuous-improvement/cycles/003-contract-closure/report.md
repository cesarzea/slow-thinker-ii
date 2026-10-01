# C03 — Agent canvas and English presentation

Local delivery verified on 2026-09-30. Owner: Cesar Zea.
The [original plan](plan.md) and [structured observations](observations.json)
are retained as process records within this project documentation section.

| Document control | Value                                                         |
| ---------------- | ------------------------------------------------------------- |
| Document ID      | C03                                                           |
| Status           | Local delivery verified; publication pending                  |
| Record owner     | Cesar Zea                                                     |
| Recorded date    | 2026-09-30                                                    |
| Method           | M05, partially applied                                        |
| Product sprint   | [Agent canvas](../../../specification/agent-canvas-sprint.md) |

## Scope and method

The owner approved an agent-focused canvas, optional inline model configuration,
optional orchestration markers, resources below the graph, and English throughout
the product. Existing execution, evidence and budget behavior had to remain intact.

The coordinator prepared shared contracts, ownership and acceptance cases before
two parallel implementation assignments. Individual and combined review preceded
test assignments. Two implementers owned graph tests and remaining browser tests;
the coordinator owned shared fixtures, whole-system checks and visual verification.
No unresolved cross-module design question was raised by an implementer. Review
still identified a metadata-selection correction and small presentation issues.

## Results

- One agent card for the single-agent graph; reviewer loops and exact evidence
  navigation preserved; actual saved model and effort metadata verified visually.
- 1,266 Python tests, 139 frontend tests and nine browser journeys pass.
- Required coverage, static, dependency, formatting, dead-code and build gates pass.
- No paid provider calls, commits, pushes or remote CI. Local CodeQL was not run.
  M05's publication/remote-defect hypothesis therefore remains unevaluated.
- The original unrelated IDE, ignore-file and component lock changes were preserved.

## Rework and process findings

Shared fixture roles and terminal routes needed repair. A runtime import inside a
mocked-module fixture caused a loading deadlock; another composition test needed
its renderer mock updated. A browser assertion omitted the router resource. These
were test infrastructure/expectation issues, not observed execution regressions.

The coordinator also omitted formatting one translated Python fixture and omitted
Makefile cache variables when continuing verification outside make. The latter
prevented browser startup until corrected. Dead-code checking found an unnecessary
helper export. All corrections and rerun reasons are in the observation record.

Whole verification did not pass uninterrupted on its first invocation. Completed
checks were retained; relevant failed/remaining blocks were resumed. Eight browser
journeys passed together; the corrected file's two journeys then passed. Neither
this record nor the product record describes that as a clean first-pass CI run.

## Measurement limits and comparison

The measured interval from the first retained clock sample (15:37:54 UTC) to
completed checks (16:09:15 UTC) is **31 min 21 s**. Analysis had already started at
the first sample; closing documentation followed the second. This interval is a
lower bound, not the complete elapsed time or accumulated parallel effort.
No waiting for user answers occurred. Per-activity totals require a later timestamp
audit; do not invent a reconciled breakdown from these sparse samples.

C03 is a smaller presentation change on an existing implementation, unlike C02's
runtime delivery. Its elapsed time cannot establish a causal productivity gain.
Closed shared contracts avoided implementer design questions, but test preparation
and preserving the exact verification environment still need improvement.

## Proposed follow-up, not an approved method revision

Freeze shared renderer mocks as well as shared data fixtures before parallel test
runs. Validate one representative composed browser test against those fixtures.
When continuing a failed verification block, preserve the entry command's complete
environment automatically; avoid rebuilding it by hand. Evaluate these proposals
with the owner before recording a new approved method version.

## Owner-review follow-up — 2026-09-30

The owner's subsequent review identified hidden agent input/output connectors and
an absent incoming graph-entry arrow. The earlier acceptance suite checked card
and outgoing-route presence, but did not verify connector visibility or an exterior
entry. The approved correction now has a real-browser regression for both visible
connectors and horizontal boundary arrows after expansion, dragging and reset.
Entry resolution also covers cyclic graphs, saved configuration and invalid data.

The coordinator specified this correction before assigning the cohesive graph
module. Production delivery and review preceded test implementation. The initial
ten browser journeys passed, but their logs exposed an initialization warning
during the new drag case. A module correction retained measured geometry through
controlled-node updates; all four affected journeys passed again without that
warning. The regression now rejects its recurrence. All 154 frontend tests and
frontend static/coverage/build gates passed. No backend checks, paid calls, commit
or publication were needed for this correction.

The dead-code checker initially failed because its browser configuration allocated
loopback ports inside the restricted environment; the authorized rerun passed.
A focused test command also passed its filter through the root npm wrapper
incorrectly, selecting two files rather than all four cases; the remaining geometry
file's two cases were then run explicitly. These are verification-command handling
issues, retained here rather than attributed to product defects.

This is additional acceptance/rework evidence for C03, not a new approved method
version or a measured productivity comparison. No complete timestamp audit was
performed for this follow-up.

## Initial-handoff time audit — 2026-10-01

The [timestamp audit](time-audit.md) now records the complete initial application
through the delivered final answer: approximately 36 minutes elapsed and
1 hour 3 minutes 50 seconds of accumulated activity across three participants.
It includes the preparation and closing documentation excluded from the earlier
31 min 21 s checkpoint observation. Those original figures are preserved above.
Subsequent owner-review work remains outside this audited interval. Activity
attribution is estimated, and the new totals do not establish a productivity gain.

## Improvement proposals after review — 2026-10-01

[Pending proposals P08–P10](../../improvement-register.md#proposals-following-c03--2026-10-01)
address dependency-contract handoffs, review supported by delivery evidence and
shared test infrastructure. P08 includes repeated external design reconstruction
that can occur without an implementer asking a question. Reading outside an owned
module is a signal to classify, not proof of avoidable work. These are hypotheses
for owner review; no new method or subsequent cycle is activated.

## Follow-up decision — 2026-10-01

The owner subsequently approved P08–P10 as
[M06](../../methods/006-delivery-preparation.md). The
[decision record](../../improvement-register.md#approval-of-m06--2026-10-01)
preserves their original proposed status and defines future evaluation. C03 remains
a record of partial M05 application; M06 approval does not activate another cycle
or retrospectively change this cycle's outcomes.

## Publication verification follow-up — 2026-10-01

This checkpoint follows the audited C03 handoff and owner-review corrections; it
is outside all recorded C03 duration and participant-activity totals. The shared
CodeQL publication prerequisite is now integrated and locally verified under the
current [M06 working method](../../methods/006-delivery-preparation.md). Contracts
and public interface skeletons preceded a package implementation assignment;
coordinator review preceded the separate public-contract test assignment.

The [verification record](../../../verification.md#shared-codeql-verification-and-commit-readiness--2026-10-01)
records 155 gate tests, a successful real rejection probe and the complete local
runner. Preparation corrections comprised document formatting, replacing an
ineffective negative fixture with the documented subprocess example, and raising
CodeQL RAM after an observed JavaScript heap failure. The resource correction was
assigned separately to the implementation and test owners, then checked before the
final complete run. These are verification preparation/resource issues, not new
agent-runtime defects. No query or mandatory gate was bypassed.

M06 application is observed for this follow-up; elapsed and accumulated activity
have not been audited, so no productivity gain or comparative timing is claimed.
The original C03 method assessment and measurements remain unchanged. Updated
remote CI has not been run; this checkpoint establishes local commit readiness.

## Browser CI regression follow-up — 2026-10-01

After publication, the polling journey failed in GitHub CI despite the preceding
local pass. The [diagnosis and correction](../../../verification.md#browser-polling-regression-and-publication-follow-up--2026-10-01)
identify a test-fixture and assertion defect: the attempted drag was outside the
viewport, and whole-style comparison could pass on visibility changes. Four
passing diagnostic repetitions showed no movement; a readiness assertion then
reproduced the failure four times. This qualifies the earlier browser evidence
without changing its recorded counts or any C03 timing.

Under M06, the coordinator resolved the diagnosis and module contract before
assigning the complete browser-journey package to one implementer. Delivery and
whole-change review preceded the separate testing assignment. One representative
case, ten focused repetitions and the unchanged full shared runner passed. No
production change, retry, delay or verification relaxation was needed.

The local pass did not prevent this escaped defect. The correction strengthens
evidence of the intended behavior rather than adding more broad test repetitions.
Remote checks for the correction remain pending at this checkpoint. This follow-up
has no complete timing audit and establishes no comparative productivity gain;
the original cycle measurements and method attribution remain unchanged.
