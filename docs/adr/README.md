# Architectural decision records

These records follow [MADR](https://adr.github.io/madr/). Each contains context, drivers, options, an outcome or proposal, consequences, and a confirmation method. The project owner decides acceptance.

Accepted records capture principles already agreed in the conversation. Proposed records are recommendations only. Alternatives documented now do not imply that the owner previously selected between those exact alternatives. Acceptance alone does not establish implementation or verification; dated confirmation sections identify observed evidence.

| ADR                                                | Decision                                                                                        | Status                                                                  |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [0001](0001-engineering-baseline.md)               | Architecture documentation and engineering gates from the first implementation                  | Accepted                                                                |
| [0002](0002-platform-mediation.md)                 | Platform-mediated managed communication                                                         | Accepted                                                                |
| [0003](0003-local-application-stack.md)            | Local Python backend and TypeScript browser application                                         | Accepted                                                                |
| [0004](0004-component-packaging.md)                | Independent component packages and local processes from the first cycle                         | Accepted                                                                |
| [0005](0005-versioned-contracts.md)                | Versioned component and graph contracts with JSON Schema review examples                        | Proposed                                                                |
| [0006](0006-execution-and-accounting.md)           | Separate execution lifecycle, reservations and evidence                                         | Proposed                                                                |
| [0007](0007-mcp-profile.md)                        | Current MCP revision and explicit two-direction transport profile                               | Proposed                                                                |
| [0008](0008-component-inheritance-and-versions.md) | Optional implementation inheritance, compatible version ranges and exact dependency resolutions | Proposed                                                                |
| [0009](0009-standalone-python-export.md)           | Future standalone Python export with explicit portability and verified optimization             | Proposed                                                                |
| [0010](0010-llm-output-validation.md)              | Text/JSON validation with retained invalid output and no implicit repair call                   | Accepted                                                                |
| [0011](0011-local-persistence.md)                  | Local SQLite storage, transactional dispatch and explicit crash recovery                        | Detailed profile proposed; SQLite and backend storage boundary selected |
| [0012](0012-single-maintainer-review.md)           | Single-maintainer owner review with mandatory PRs and checks; no external approval count        | Accepted; remote setting verified                                       |
| [0013](0013-workspace-authoring-state.md)          | Separate authoring, immutable versions and execution views with exact-source patching           | Superseded by 0016                                                      |
| [0014](0014-component-owned-dialogs-and-composition.md) | Component-owned dialogs and generic composition through a composer component                 | Superseded by 0016 and 0020                                             |
| [0015](0015-new-execution-core.md)                 | New execution core reusing verified subsystems                                                  | Accepted                                                                |
| [0016](0016-graph-document-model.md)               | Graph documents of nodes, ports, connections and embedded components                            | Accepted; amends 0005                                                   |
| [0017](0017-message-driven-execution.md)           | Message-driven asynchronous execution                                                           | Accepted; activation-failure policy proposed                            |
| [0018](0018-derived-authorization.md)              | Authorization derived from connections and declared uses                                        | Accepted; refines 0002                                                  |
| [0019](0019-platform-llm-service.md)               | Platform LLM service with provider-declared parameters                                          | Accepted                                                                |
| [0020](0020-declared-component-configuration.md)   | Component-declared configuration rendered by the platform                                       | Accepted                                                                |
| [0021](0021-supervision-and-recording.md)          | Supervision and recording by default                                                            | Accepted                                                                |
| [0022](0022-budgets-and-request-reservations.md)   | Run, daily and monthly budgets with request-size reservations                                   | Proposed; amends 0006                                                   |
| [0023](0023-container-ready-component-boundary.md) | Container-ready component boundary                                                              | Proposed; amends 0004 and 0007                                          |
| [0024](0024-working-copy-and-activated-versions.md) | Working copy with change history and activated versions | Accepted; amended by 0025 |
| [0025](0025-runs-of-changes-and-run-mode.md) | Runs of changes, run mode and observation points | Accepted; amends 0024 |
| [0026](0026-memory-position.md) | Memory as an embedded component position | Accepted; amends 0004, 0007 and 0023 |
| [0027](0027-functional-source-license.md) | Functional Source License | Accepted; replaces Apache 2.0 |

## Change procedure

Proposed records may be revised during review. Once accepted, substantive changes require a new or superseding decision; the original rationale remains available. A change to an engineering obligation requires explicit review, not merely editing a table.

Decisions must link to requirements and an observable confirmation method. Cross-cutting changes must update affected contracts, diagrams and examples. Records 0001–0014 reference the requirements (R01–R31) and documents of the previous implementation, now [archived](../archive/previous-implementation/README.md); records from 0015 onward reference the [current requirements](../specification/requirements.md) (CR01–CR18).

## New core — 2026-10-04

Records 0015–0023 define the new execution core approved by the owner after the
[development assessment](../archive/previous-implementation/reviews/2026-10-04-development-assessment/README.md).
Accepted records capture decisions stated or confirmed by the owner on that date;
proposed records are technical decisions taken within the validated step 1 scope
and await the owner's review.

## S06 workspace authoring state

[ADR 0013](0013-workspace-authoring-state.md) separates controlled authoring,
immutable-version and execution views. The owner-authorized implementation is
locally verified; its [delivery report](../archive/previous-implementation/progress/sprint-06-status-report.md)
retains evidence. Owner usability acceptance and publication remain separate.

## S06 composition and component-owned configuration

[ADR 0014](0014-component-owned-dialogs-and-composition.md) records the authorized
generic composition protocol and component-owned dialog definitions. The related
S06 correction is in source development; implementation and verification evidence
will be recorded separately from the accepted decision.
