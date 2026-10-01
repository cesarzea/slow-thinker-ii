# M02 — Complete sprint in distinct phases

| Document control  | Value                                                |
| ----------------- | ---------------------------------------------------- |
| Method ID         | M02                                                  |
| Status            | Agreed with the user and applied in C02              |
| Approval recorded | 2026-09-29, before work resumed at 03:53 Lisbon time |
| Owner             | Cesar Zea                                            |
| Applied cycle     | C02                                                  |

This record does not treat later retrospective proposals as accepted changes.

## Agreed procedure

1. The coordinator defines the complete sprint through delivery, keeping final
   objectives in view without extending the scope. The coordinator completes
   necessary research and decisions, and defines responsibilities, dependencies,
   contracts and acceptance criteria.
2. For each affected module, prepare its brief README first, then
   `specification.md`, and finally `todo.md` when work remains. Review new public
   interface skeletons before implementation.
3. Assign complete components or packages to independent implementers, with
   exclusive ownership, shared rules, specifications and the minimum relevant
   context. Development runs in parallel. Static checks are allowed; functional
   testing belongs to the later phase.
4. Review individual deliveries and the complete result. Group corrections into
   module tickets and repeat necessary corrections until the whole sprint appears
   ready for testing. A local uncertainty does not reopen the entire design.
5. Prepare concrete test assignments from the planned acceptance criteria.
   Implement module tests in parallel, verify the whole result, and group
   diagnosis, tickets and corrections until all mandatory checks pass.
6. Maintain documentation and tickets: remove completed work from `todo.md` and
   delete the file when no work remains. Keep the process history in this archive,
   outside implementation tickets.

Separate ownership prevents editing conflicts. Interaction checks and integration
tests are still required. Checks are not weakened to reduce elapsed time.

## Observed application in C02

Backend, components and packaging, and frontend were assigned to three
implementers. The coordinator retained shared contracts, configuration, review
and delivery. Individual review partly overlapped development; whole-system review
preceded functional testing. Local clarifications and corrections occurred,
without a general replacement of the architecture.

- [C02 report](../cycles/002-sprint-2026-09-29/report.md).
- [English edition of the archived operating rules](002-rules-snapshot.md).
- [Later proposed improvements](../improvement-register.md).
