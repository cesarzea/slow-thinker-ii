# M06 — Assignment preparation, review evidence and test readiness

| Document control     | Value                                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| Method ID            | M06                                                                                              |
| Status at recording  | Approved; delivery application pending                                                           |
| Approval recorded    | 2026-10-01, Europe/Lisbon                                                                        |
| Owner                | Cesar Zea                                                                                        |
| Extends              | [M05](005-local-ci-verification.md), retaining all inherited phases and verification obligations |
| Additional decisions | P08–P10 in the [decision register](../improvement-register.md#approval-of-m06--2026-10-01)       |
| Application          | Subsequent authorized delivery work; no new sprint or cycle activated                            |

M06 addresses repeated analysis across assignments and reviews, and avoidable test
infrastructure corrections observed in [C03](../cycles/003-contract-closure/time-audit.md).
It does not establish a measured improvement or change the method applied to C03.

## Assignment preparation — P08

Before delegation, the coordinator makes the assignment implementable from the
existing module `specification.md`, `todo.md`, relevant code and exact public
dependency contracts. Include:

- The owning source and public interface for each consumed dependency; for data,
  identify its origin, relevant field paths and a representative public payload.
- Resolved shared decisions, expected behavior and failure cases. Reference the
  canonical contract rather than copying it into another specification.
- Local implementation choices left to the implementer, exclusive ownership and
  acceptance criteria. Apply this preparation to affected interactions only.

Walk through a representative case from these sources. If implementing it requires
inventing a shared decision or reconstructing dependency internals to understand
the contract, resolve the gap before delegating affected work.

Implementers still study public dependencies and design their module's internals.
Unexpected investigation beyond the supplied contracts must be reported briefly:
what information was missing, the outcome and any repeated work. A blocking shared
decision pauses affected work until the coordinator resolves it. Reading outside
an assigned directory is a signal to classify, not proof of unnecessary analysis.

## Delivery and review — P09

Each delivery includes a brief map from acceptance criteria to changed code and
available evidence, plus material local design choices and unresolved items.
Distinguish implemented behavior from verification still pending; development
delivery does not claim completion of the later testing phase.

The coordinator uses this map to review the implementation, public contracts,
interactions and failure paths without reconstructing decisions already explained.
The map supports review; it does not replace code inspection, engineering checks
or whole-system review. Group corrections in the existing module tickets.

## Shared test preparation — P10

At the start of the testing phase, before parallel test implementation and runs:

1. Establish the shared fixtures, mocks and configured environment needed for the
   affected contracts. Include composed renderer mocks where applicable.
2. Run one representative composition or browser case for each affected shared
   infrastructure before expanding dependent tests. This remains after development
   and review; it does not introduce functional testing into each coding step.
3. Resume failed verification blocks through the same configured entry point,
   preserving pinned versions, paths, cache settings and failure propagation.
   Classify failures and group corrections before repeating affected checks.

Use existing test tickets and verification commands. Do not introduce a second
documentation set, weaken gates or rerun unrelated broad checks without cause.
M05's local verification including CodeQL before upload remains mandatory; partial
verification must be identified as incomplete.

## Evaluation

Retain M05's metrics and the [measurement policy](../measurement.md). In delivery
records and review, distinguish necessary dependency comprehension, local design
and repeated reconstruction of shared decisions, including work without questions.
Record missing information, reopened decisions, causes and associated effort when
observable; label estimates. Do not require a separate diary for every file read.

Measure added coordinator preparation, implementer investigation, review and
corrections alongside total elapsed delivery time and accumulated parallel work.
Separate product, fixture, expectation and environment failures, and record rerun
causes. Check acceptance outcomes and escaped defects as well as time: fewer
questions, file reads or verification runs alone do not demonstrate improvement.
