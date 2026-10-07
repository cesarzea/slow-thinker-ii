> **Archived documentation — superseded on 2026-10-04.** These documents describe the
> previous implementation (sprints S01–S06) and are retained as historical evidence.
> The owner then approved a new execution core; its current documentation starts at
> the [documentation index](../../README.md). Links into source code refer to the
> previous implementation, preserved in the local archive branch
> `archive/s06-c11-wip`, and may not resolve in the current tree.

# Project documentation

**Status as of 2026-10-04: S06 remains incomplete. Development is paused by the
owner while component responsibilities and configuration usability are reviewed.
Complete current verification and owner acceptance remain outstanding.**

The [Development Status and Architecture Review](reviews/2026-10-04-development-assessment/README.md)
consolidates implemented capabilities, component inventory, detected problems,
verification failures, clarified decisions and remaining work. It is the current
assessment; earlier technical checkpoints retain their original scope and dates.

**Decision of 2026-10-04:** the owner decided to build a new execution and
orchestration core that reuses selected verified subsystems, under the
[M07 working method](../../continuous-improvement/methods/007-validated-journeys.md).
The documents below describe the previous implementation. They will be archived
and labelled as superseded when the new core's documentation is approved; until
then they remain the historical record, not the specification of the new core.

This documentation records the approved first-cycle requirements, architecture and contracts, and keeps later capabilities explicitly deferred. The [delivery sprint](specification/first-cycle-sprint.md) identifies the implemented scope.

## Reading order

1. [Requirements and scope](specification/requirements.md): the purpose, recorded commitments, and delivery boundaries.
2. [Architecture, organized with arc42](architecture/README.md): structure, behavior, constraints, and quality requirements.
3. [Architectural decisions](../../adr/README.md): accepted principles and proposed implementation choices.
4. [Component and graph contracts](contracts/README.md): versioned formats and bundled examples.
5. [Open questions](specification/open-questions.md): closed first-cycle decisions and unresolved future work.
6. [Engineering process improvement](../../continuous-improvement/README.md): versioned working methods, cycle evaluations, measurements and approved improvement decisions.

The [verification record](verification.md) identifies the implementation checks, live execution evidence and their limits.

The [S06 usability and comprehension review](reviews/2026-10-02-ui-usability/README.md)
records the owner's subsequent interface rejection, 26 prioritized findings, a
control-by-control inventory and proposed acceptance journeys. Passing technical
checks does not close the identified usability and editing-safety gaps. The review
did not authorize its proposed implementation changes. The subsequent owner-activated
[S06 redesign](specification/s06-workspace-redesign.md) defines the delivered
correction; its report separates technical verification from owner acceptance.
The earlier [whole-interface completion](specification/s06-ui-completion.md)
covers every implemented destination and actual internal Redirector composition.
Its [review evidence](reviews/2026-10-03-s06-completion/README.md) and
[C10 process record](../../continuous-improvement/cycles/010-s06-interface-completion/report.md)
retain observed results, corrections and verification limits.
The owner subsequently identified a composition/configuration gap. The
[correction scope](specification/s06-composition-and-dialogs.md) and
[C11 process record](../../continuous-improvement/cycles/011-s06-composition-and-dialogs/report.md)
define the current delivery and retain its failures and pending checks.

For development, start with the [contributing guide](../../../CONTRIBUTING.md).
The [local development guide](development.md) covers running the application,
preparing components and enabling model execution. Full verification requires
the pinned [CodeQL bundle](../../../tooling/quality/codeql/readme.md#installation).

The [personal experiment guide](personal-experiments.md) describes S03 JSON
authoring, immutable revisions, recovery and saved-definition execution. The
[S03 delivery specification](specification/personal-experiments-sprint.md) tracks
acceptance verification separately from these usage instructions.

The [workspace guide](workspace.md) covers structured component and graph editing,
model/resource discovery, execution history, configurable limits and recovery.
The [S04–S06 delivery block](specification/s04-s06-delivery.md) defines the current
end-to-end acceptance scope.

The [central version register](../../../CHANGELOG.md) records development package versions
and the history of versioned sprint reports.

The [S02 Sprint Status Report](progress/sprint-02-status-report.md), version
`0.0.2.5`, consolidates delivered progress, verification, owner-review corrections
and outstanding items, with links to the sprint specification.

The [S03 Sprint Status Report](progress/sprint-03-status-report.md), version
`0.0.3.2`, records personal authoring, retained execution and functional closure
after real collaboration validation, with publication and owner review identified
separately.

The S04 [model report](progress/sprint-04-status-report.md), S05
[resource report](progress/sprint-05-status-report.md) and S06
[workspace report](progress/sprint-06-status-report.md) record the latest verified
delivery. The [live validation](progress/s04-s06-live-validation.md) retains actual
two-provider collaboration, shared persistent memory and independently audited cost.

The [sprint roadmap](specification/sprint-roadmap.md), revision 9, records delivered
scopes, future delivery order, dependencies and milestones. The owner-requested
replan adds the product configuration/execution workspace as S06, followed by
evaluation as S07. The [previous plan](specification/sprint-roadmap-20261002-r1.md)
retains its original scope numbering and forecast. Future delivery specifications
still require approval; planning does not activate implementation.

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
- Keep the [engineering requirements](../../../README.md#engineering-standards) authoritative; do not paraphrase them into weaker rules.
- Review schemas and examples for both structural validity and semantic constraints.

## Gate for closing the first-cycle specification

The owner must approve the applicable proposed ADRs and contract revisions. All first-cycle blockers in the open-question register must have decisions, measurable acceptance criteria, and a documented verification method. Deferred work must have an explicit boundary. Quality gates must be configured before application code is accepted.

Specification closure and implementation verification are separate gates. Before closure, resolve the design choices, publish reviewable contracts/acceptance cases and investigate feasibility where an unsupported dependency could invalidate the design. Passing the future executor, storage, browser and cancellation tests is not a prerequisite for permission to implement those systems. Their criteria and verification method must be defined first; executable evidence is required before the corresponding functionality or conformance is claimed.

Similarly, Q14 requires agreement on source boundaries and the verification entry point during specification review. Installing and demonstrating the quality gates belongs to the first approved implementation setup, before application code is accepted. A selected technology or passing temporary probe does not authorize skipping owner approval of the specification.

Current state: **the first-cycle specification was approved on 2026-09-28**, with bounded conditional review added on 2026-09-29. Approval does not extend to deferred capabilities; the verification record tracks implementation delivery separately.

## S06 workspace redesign

The [S06-UX delivery specification](specification/s06-workspace-redesign.md) closes
the authorized correction scope, ownership and acceptance criteria. It links the
interaction, history/API, presentation and frontend-interface contracts and
[ADR 0013](../../adr/0013-workspace-authoring-state.md). Module-local specifications retain delivery receipts; completed implementation
tickets have been removed. Implementation, the unchanged mandatory runner and the local demonstration
have completed. The versioned sprint report records the latest checkpoint;
passing tests does not constitute owner acceptance.
