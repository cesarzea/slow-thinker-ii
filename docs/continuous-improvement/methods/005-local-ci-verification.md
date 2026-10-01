# M05 — Local verification equivalent to CI

| Document control    | Value                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| Method ID           | M05                                                                                                     |
| Status at recording | Approved for C03; application pending                                                                   |
| Approval recorded   | 2026-09-29                                                                                              |
| Owner               | Cesar Zea                                                                                               |
| Extends             | [M04](004-testing-and-verification.md), retaining its phases, contract closure and testing improvements |
| Additional decision | [P07](../improvement-register.md)                                                                       |

## Before uploading changes

1. Use one verification command for reproducible checks both locally and on
   GitHub, with the same versions, configuration, rules and failure criteria.
   Avoid maintaining two independent check lists.
2. Include CodeQL in local verification before publication, alongside existing
   tests, coverage, type checks, lint and architecture checks. Propagate failures
   and retain results; do not weaken checks.
3. Verify the final code, tests and documentation before uploading. If they change
   afterward, apply M04's repetition rules and retain evidence corresponding to
   the changes ultimately published.
4. GitHub repeats verification as an independent check. Explicitly identify checks
   that depend on GitHub and can only be completed there. Incomplete local
   verification does not constitute a passing result.

Dependabot proposals originate on GitHub, so their first check may be remote.
Record these failures separately from locally developed changes.

## Additional evaluation in C03

- Defects detected before uploading and defects discovered only on GitHub,
  identifying the difference that allowed them to escape local verification.
- Corrective uploads and cancelled or repeated runs, with their causes.
- Local and remote verification duration, time until failure detection and total
  delivery time, without counting concurrent intervals twice.

The hypothesis is that this reduces upload-and-correction cycles. It does not
assume that running CodeQL locally is faster or eliminates remote verification
cost. Its effect was to be measured alongside the metrics inherited from M04,
using the shared [measurement definitions](../measurement.md).
