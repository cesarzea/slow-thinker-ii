# Project documentation

**Status: First-cycle specification approved; local implementation available.**

This documentation records the approved first-cycle requirements, architecture and contracts, and keeps later capabilities explicitly deferred. The [delivery sprint](specification/first-cycle-sprint.md) identifies the implemented scope.

## Reading order

1. [Requirements and scope](specification/requirements.md): the purpose, recorded commitments, and delivery boundaries.
2. [Architecture, organized with arc42](architecture/README.md): structure, behavior, constraints, and quality requirements.
3. [Architectural decisions](adr/README.md): accepted principles and proposed implementation choices.
4. [Component and graph contracts](contracts/README.md): versioned formats and bundled examples.
5. [Open questions](specification/open-questions.md): closed first-cycle decisions and unresolved future work.
6. [Engineering process improvement](continuous-improvement/README.md): versioned working methods, cycle evaluations, measurements and approved improvement decisions.

The [verification record](verification.md) identifies the implementation checks, live execution evidence and their limits.

The [central version register](../CHANGELOG.md) records development package versions
and the history of versioned sprint reports.

The [S02 Sprint Status Report](progress/sprint-02-status-report.md), version
`0.0.2.3`, consolidates delivered progress, verification, owner-review corrections
and outstanding items, with links to the sprint specification.

The [sprint roadmap](specification/sprint-roadmap.md) records delivered scopes and
proposes subsequent sprint scopes, delivery order, dependencies and milestones.
Its future sprint scopes remain proposals until approved; planning does not activate
implementation.

The process-improvement record is part of the project documentation. It evaluates
how development is organized; product requirements and architecture retain their
own specifications and decision records. All maintained documents are in English.

## Document states

| State                    | Meaning                                                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| Recorded requirement     | A requirement stated or accepted in the design conversation. Its detailed implementation can still be open.         |
| Accepted ADR             | An architectural principle already agreed with the project owner. This does not mean it has been implemented.       |
| Proposed ADR or contract | A concrete recommendation for review. Examples and schemas do not make it an approved decision.                     |
| Deferred capability      | Part of the intended evolution, excluded from the first functional cycle. Its extension boundary still matters now. |

The project owner is Cesar Zea. Dates record documentation, not a claim that all decisions were made on that date. No proposed decision becomes accepted through omission, elapsed time, or a successful schema check.

## Review and change procedure

- Preserve requirement identifiers. Reference them from decisions and acceptance scenarios.
- Keep requirements, architectural decisions, and implementation evidence distinct.
- Record alternatives and consequences before selecting a new architectural mechanism.
- Update affected diagrams, contracts, examples, and open questions together.
- Keep the [engineering requirements](../README.md#engineering-standards) authoritative; do not paraphrase them into weaker rules.
- Review schemas and examples for both structural validity and semantic constraints.

## Gate for closing the first-cycle specification

The owner must approve the applicable proposed ADRs and contract revisions. All first-cycle blockers in the open-question register must have decisions, measurable acceptance criteria, and a documented verification method. Deferred work must have an explicit boundary. Quality gates must be configured before application code is accepted.

Specification closure and implementation verification are separate gates. Before closure, resolve the design choices, publish reviewable contracts/acceptance cases and investigate feasibility where an unsupported dependency could invalidate the design. Passing the future executor, storage, browser and cancellation tests is not a prerequisite for permission to implement those systems. Their criteria and verification method must be defined first; executable evidence is required before the corresponding functionality or conformance is claimed.

Similarly, Q14 requires agreement on source boundaries and the verification entry point during specification review. Installing and demonstrating the quality gates belongs to the first approved implementation setup, before application code is accepted. A selected technology or passing temporary probe does not authorize skipping owner approval of the specification.

Current state: **the first-cycle specification was approved on 2026-09-28**, with bounded conditional review added on 2026-09-29. Approval does not extend to deferred capabilities; the verification record tracks implementation delivery separately.
