# M07 — Validated journeys, tests with code and staged parallelism

| Document control     | Value                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| Method ID            | M07                                                                                                     |
| Status at recording  | Approved; not yet applied                                                                               |
| Approval recorded    | 2026-10-04, Europe/Lisbon                                                                               |
| Owner                | Cesar Zea                                                                                               |
| Supersedes           | [M06](006-delivery-preparation.md) as the current method; retains M05 verification and M06 P08–P10      |
| Decisions            | P14–P18 in the [decision register](../improvement-register.md#approval-of-m07--2026-10-04)              |
| Application          | The new core delivery, planned as the next cycle; approval activates no sprint                          |

M07 responds to the evidence consolidated in the
[2026-10-04 development assessment](../../archive/previous-implementation/reviews/2026-10-04-development-assessment/README.md)
and cycles C06–C11. Five S06 deliveries passed the complete local runner and were
subsequently rejected or reopened by the owner. Derived contracts had encoded an
unsuitable user-facing interpretation, and review and tests mainly checked that
derived behavior. Shared decisions were still missing during implementation in
most M06 cycles, and coverage gaps surfaced only in late verification. The record
contains no reconciled time or token comparison for M06. M07 establishes no
improvement by approval; its effects must be measured.

## Retained obligations

M07 keeps the README engineering standards and every verification gate unchanged,
M05's complete local verification including CodeQL before upload, M06's assignment
preparation (P08), delivery map (P09) and shared test readiness (P10), exclusive
ownership of packages and shared files, and the module documents required by the
repository working rules. Partial verification remains identified as incomplete.

## Phases

0. **Journey validation — P14.** For user-facing scope, the coordinator prepares
   concrete journeys before deriving shared contracts: screen mockups, representative
   definitions such as graph documents, and the results and recorded activity the
   user will see. The owner validates them explicitly. Retain the validated version,
   date and statement. Contracts and acceptance criteria cite the journeys they
   implement; a change to a validated journey requires renewed validation.
1. **Analysis, specification and tasks.** As in M06, with documentation under P17.
   Resolve shared decisions before delegation and walk through a representative case.
2. **Development with tests — P15 and P16.** Implementers write unit and contract
   tests together with their code. A package's scoped gates pass before delivery:
   formatting, linting, types, import boundaries, dead code, source size and unit
   coverage. Shared foundations, such as a new graph model and execution engine,
   are implemented by one implementer until their public contracts are implemented
   and checked against the validated journeys. Independent packages may then run in
   parallel with exclusive ownership. Each delivery includes the P09 map.
3. **Review and corrections.** Review individual deliveries and the combined result
   against the validated journeys as well as the derived contracts, including
   interactions and failure paths. Group corrections into module tickets.
4. **Integration and acceptance.** Apply P10 test readiness, then implement
   integration and end-to-end tests derived from the validated journeys. Pass the
   complete unchanged runner on the final source state. Demonstrate the journeys to
   the owner and record product acceptance separately from technical verification.

Phase 2 does not alternate implementation with end-to-end functional testing; the
tests written with the code verify the implemented units and their contracts.

## Documentation — P17

Architecture follows arc42 with C4 views, and decisions are MADR records, as the
README requires. Contracts are versioned and linked rather than copied. Module
`specification.md` files state the current specification only; dated delivery
receipts and status logs belong in the sprint status report and verification record.
Superseded documents are archived and labelled rather than amended in place.

## Measurement — P18

Record each phase's start and end, pauses, elapsed time and, where the tooling
reports it, token usage per participant. Classify rework as product interpretation,
missing shared decision, implementation defect, or test, fixture or environment
failure. Count complete-runner attempts with their causes. Label estimates. Compare
with earlier cycles only with scope differences explicit; do not infer causal
productivity from elapsed time, code volume, test counts or parallelism.
