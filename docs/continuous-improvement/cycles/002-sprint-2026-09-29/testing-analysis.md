# C02 — Subsequent analysis of testing activity

| Document control | Value                                                                              |
| ---------------- | ---------------------------------------------------------------------------------- |
| Cycle            | C02 — Sprint through delivery                                                      |
| Parent record    | [C02 report](report.md)                                                            |
| Record owner     | Cesar Zea                                                                          |
| Recorded date    | 2026-09-29                                                                         |
| Record type      | Subsequent analysis; supplements the original report without replacing its figures |

This note does not amend the method approved for [C03](../003-contract-closure/plan.md)
or initiate implementation work.

## Breakdown of the 45 minutes

Intervals originally classified as Testing and verification total 2,684.570
seconds, or 44.74 accumulated minutes across four participants. Their identifiers
were checked against the recorded actions to subdivide them approximately:

| Predominant activity                                              | Approximate minutes |
| ----------------------------------------------------------------- | ------------------: |
| Preparing and correcting tests, fixtures and acceptance scripts   |                  27 |
| Running local checks and acceptance checks, and visual inspection |                  13 |
| Checking and waiting for remote CI checks                         |                   5 |
| **Rounded total**                                                 |              **45** |

Some commands wrote and ran tests in the same step; the two activities cannot be
separated exactly. These values attribute active time, rather than the complete
duration of each process. Background execution overlapped other activities.
Test-related analysis and corrections to production code remain in their original
categories.

## Planned work

Tests were added for conditional flow, selectors, MCP composition, permissions,
reports, budgets and process recovery. HTTP, model and graph fixtures, common
clients, independent-installation tests and browser journeys were prepared. There
were two demonstrations with a real provider.

Existing tests also needed adaptation to the expanded catalog and SQLite v5.
Acceptance checks confirmed feedback, limits, costs and cleanup.

## Sources of corrections and repeated execution

- **Environment:** some executions inherited incorrect Node or uv versions; others lacked access to the local server or installed browsers. One backend execution reported 48 failures and 47 errors; the group of 95 cases passed after using the environment with the pinned version. This count does not represent 95 product defects.
- **Fixtures and tests:** simulated MCP responses lacked required fields; catalog and migration expectations were outdated; limit profiles were modified without recording the corresponding revision. The application correctly rejected some of these test configurations.
- **Insufficiently specified contract:** handling of string-valued root inputs was tested, then the interface and tests were adjusted to the requirement to send a JSON object. This work is related to contract improvement P05.
- **Actual interface defects:** loaded content displaced the focused evidence, the complete graph was not framed when its definition arrived, and return paths could overlap labels. These defects were corrected and verified.
- **Coverage:** one verification reached 89.19% branch coverage against the required 90%; 18 additional tests covered 25 branches. The threshold was not lowered.
- **Remote review:** CodeQL detected cleanup inside assertions and ambiguous protocol declarations. These were corrected and verified again.
- **Publication:** a subsequent documentation commit triggered CI again. That additional execution could have been avoided by grouping documentation with corrections.

## Complete verification and reliability of monitoring

There were four local launches of `make verify`: one stopped after four seconds at
a static check; one ended because of insufficient coverage; the third passed; and
the fourth passed after CodeQL corrections. Their processes lasted approximately
nine minutes in total, overlapping other activities. They were not four complete,
identical executions, and those nine minutes are not added to the 45 minutes.

Some partial checks used `pytest ...; tail ...`. The command's final exit status
belonged to `tail`, so it could be zero even when pytest had failed. Failures were
observed in the log and corrected; the final complete verification passed. The
way these partial checks were launched made their monitoring less reliable and
must be distinguished from an actual passing test result.

## Interpretation

The largest attributed block was building and adjusting tests and their
infrastructure. Tests found actual defects and provided evidence about the
contracts. Rework also resulted from inconsistent environments, invalid fixtures,
contract decisions clarified late and the publication sequence. There is no basis
for quantifying the complete fraction of the 45 minutes that would have been
avoidable.

Sources: [original intervals](intervals.csv), [activities by participant](activities.csv)
and the corresponding tool events. Tests were not rerun for this analysis.
