# Architectural decision records

These records follow [MADR](https://adr.github.io/madr/). Each contains context, drivers, options, an outcome or proposal, consequences, and a confirmation method. The project owner decides acceptance.

Accepted records capture principles already agreed in the conversation. Proposed records are recommendations only. Alternatives documented now do not imply that the owner previously selected between those exact alternatives. Acceptance alone does not establish implementation or verification; dated confirmation sections identify observed evidence.

| ADR | Decision | Status |
| --- | --- | --- |
| [0001](0001-engineering-baseline.md) | Architecture documentation and engineering gates from the first implementation | Accepted |
| [0002](0002-platform-mediation.md) | Platform-mediated managed communication | Accepted |
| [0003](0003-local-application-stack.md) | Local Python backend and TypeScript browser application | Accepted |
| [0004](0004-component-packaging.md) | Independent component packages and local processes from the first cycle | Accepted |
| [0005](0005-versioned-contracts.md) | Versioned component and graph contracts with JSON Schema review examples | Proposed |
| [0006](0006-execution-and-accounting.md) | Separate execution lifecycle, reservations and evidence | Proposed |
| [0007](0007-mcp-profile.md) | Current MCP revision and explicit two-direction transport profile | Proposed |
| [0008](0008-component-inheritance-and-versions.md) | Optional implementation inheritance, compatible version ranges and exact dependency resolutions | Proposed |
| [0009](0009-standalone-python-export.md) | Future standalone Python export with explicit portability and verified optimization | Proposed |
| [0010](0010-llm-output-validation.md) | Text/JSON validation with retained invalid output and no implicit repair call | Accepted |
| [0011](0011-local-persistence.md) | Local SQLite storage, transactional dispatch and explicit crash recovery | Detailed profile proposed; SQLite and backend storage boundary selected |
| [0012](0012-single-maintainer-review.md) | Single-maintainer owner review with mandatory PRs and checks; no external approval count | Accepted; remote setting verified |

## Change procedure

Proposed records may be revised during review. Once accepted, substantive changes require a new or superseding decision; the original rationale remains available. A change to an engineering obligation requires explicit review, not merely editing a table.

Decisions must link to requirements and an observable confirmation method. Cross-cutting changes must update affected contracts, diagrams, examples, and the [question register](../specification/open-questions.md).
