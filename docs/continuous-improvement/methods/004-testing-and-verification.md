# M04 — Contracts, test preparation and verification

| Document control    | Value                                                                            |
| ------------------- | -------------------------------------------------------------------------------- |
| Method ID           | M04                                                                              |
| Status at recording | Approved for C03; application pending                                            |
| Approval recorded   | 2026-09-29                                                                       |
| Owner               | Cesar Zea                                                                        |
| Extends             | [M03](003-contract-closure.md), retaining contract closure and the phases of M02 |
| Additional decision | [P06](../improvement-register.md)                                                |

## Preparing and running tests

1. Use one way to run tests, shared by implementers and coordinator, with pinned
   versions and correct paths. Commands must propagate test failures even when
   they also save or display logs.
2. During sprint preparation, include success, rejection and boundary scenarios
   in each assignment, with expected results and a reference to the contract that
   supports them. Resolve ambiguities before building affected cases.
3. At the start of the testing phase, validate shared infrastructure first:
   simulated data conforming to schemas, valid configurations, local servers and
   the browser. Run one representative check per infrastructure before building
   and running the remaining suite. This step belongs to testing, after development
   and review.
4. Each implementer delivers their assignment with tests, static checks and
   coverage verified. Plan error and boundary cases in the assignment and use
   coverage to detect omissions. The coordinator verifies interactions and overall
   coverage. Mandatory checks remain in force.
5. Group failures from each run, apply a coherent batch of corrections and repeat
   affected checks. Run complete verification on the code, tests and documentation
   prepared for delivery. Record the cause of each subsequent repeat and group
   changes before publication to avoid CI reruns caused by pending documentation.

Existing assignments and verification commands capture these obligations;
no second collection of test specifications is introduced.

## Additional evaluation in C03

- Failures caused by tests or the environment, distinguished from product defects
  and incorrect expectations caused by ambiguous contracts.
- Rework time, measured when possible and labelled as an estimate when reconstructed
  retrospectively.
- Repeated runs, each run's scope and the reason for repetition.
- Total preparation and delivery time, alongside cumulative parallel activity,
  to assess whether preparation saves more work than it adds.

The clarification and contract-closure metrics from M03 also remain in use.
Apply the shared [measurement definitions](../measurement.md). These changes were
to be evaluated in C03; they are not presented as demonstrated improvements.
