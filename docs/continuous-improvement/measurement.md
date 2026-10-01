# Measurement Policy and Limitations

| Document control        | Value                                                            |
| ----------------------- | ---------------------------------------------------------------- |
| Document ID             | CI-MEAS-001                                                      |
| Status                  | Established measurement policy; historical applications retained |
| Owner                   | Cesar Zea                                                        |
| English project edition | 2026-09-30                                                       |

## Measures

**Active elapsed time** is the recorded time between start and delivery, excluding
inactivity supported by the records. It includes necessary tool and CI waits.
A question does not count as a pause when useful work continues.

**Accumulated participant activity** is the sum of active turns for the coordinator
and implementers. It includes overlapping participants but does not duplicate
background tools within one participant. It is not CPU time, monetary cost or a
prediction of sequential execution time.

**Activity distribution** is a retrospective estimate based on visible events,
tool types, edit destinations and phases. Its uncertainty must remain explicit.

## C01 and C02 attribution rules

Intervals are partitioned without double counting within each participant.
Categories distinguish reading, implementation edits, documents, tests,
diagnosis, operations, coordination and context compaction. Mixed commands use
the predominant activity; foreground activity takes precedence over concurrent tools.

Deliberation intervals with no other observable purpose are classified as analysis.
Their content is neither read nor reproduced. Analysis therefore includes
comprehension and local review during implementation/testing, not only architecture decisions.

Short gaps are attributed to the next observable activity. Long unsupported gaps
remain unattributed. C01 adjusted two turns to the recorded active duration;
its [results](cycles/001-baseline-2026-09-28/results.json) retain those adjustments.
C02 reused the attribution rule with recognition of delegation, CI and relative
test paths. It cannot reliably isolate reanalysis, which is included in
reading/review and technical diagnosis.

Values in seconds support arithmetic reconciliation; they do not establish
second-level semantic accuracy. Rounded presentation preserves the total.
Future attribution changes must be identified before comparing cycles.

## Evidence handling

Reports, tables, results and classified event chronology are retained. The
`evidence` column in interval datasets substitutes a neutral description for
original commands, local paths and potentially private values. Event identities,
categories, interval boundaries and attributions are retained.

The [provenance manifest](provenance.json) records historical source hashes,
observed pre-migration hashes and English-edition hashes. Translation changes
labels and presentation only; it does not recalculate measured values. Original
source snapshots remain locally archived. Temporary reconstruction scripts,
complete conversations and private intermediate files are not project dependencies.

## Comparison requirements

Record the starting point, scope, participant count, controls and verified
functionality delivered. Separate hypotheses from findings. Neither test counts
nor code volume establish productivity. A difference between two dissimilar
sprints cannot, by itself, be attributed to their working methods.

Record exact observations separately from estimates, lower bounds and unknown
values. At the initial C03 checkpoint, sparse clock samples established only a lower-bound interval;
no reconciled whole-cycle or accumulated-effort total was available. Subsequent
input/output work is a separately described follow-up and is excluded from that interval.

## C03 audit addendum — 2026-10-01

The limitations above describe the initial checkpoint record. A later
[initial-handoff audit](cycles/003-contract-closure/time-audit.md) reconstructs
the complete turn and implementer activity through the initial delivered answer.
Its elapsed and accumulated totals now reconcile; task allocation remains an
estimate. Subsequent input/output corrections are still outside that interval.
The sparse original observations and historical measurement statements remain
unchanged as evidence of what was known at that checkpoint.
