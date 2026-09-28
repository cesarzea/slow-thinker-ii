# ADR 0001: Apply architecture and engineering standards from the outset

- Status: Accepted
- Recorded: 2026-09-27
- Decision-maker: César Zea
- Requirements: R22

## Context and problem statement

The project must demonstrate disciplined architecture and implementation. The owner explicitly requires the reference engineering rules from the first implementation, including documentation, modularity, encapsulation, and verification.

## Decision drivers

Preserve exact obligations, make violations detectable, avoid architectural drift, and distinguish mandatory policy from evidence of enforcement.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Mandatory baseline from initial setup | Consistent standards across all functional cycles | Initial setup and verification work |
| Add controls after a prototype | Earlier ungoverned prototype | Retrofitting and weaker assurance; conflicts with the requirement |
| Documentation without automatic checks | Low setup effort | Cannot establish that violations block delivery |

## Decision outcome

Apply the [README engineering baseline](../../README.md#engineering-standards) from the first implementation. Use arc42, C4 and MADR for architecture. Configure and demonstrate applicable gates before accepting application code. Preserve the seven reference TypeScript requirements verbatim; add Python-specific controls separately.

The owner has approved this policy. Individual configurations and implementation evidence remain to be produced. Controls tied to a release or deployment apply to the first such event, not an unspecified later maturity phase.

## Consequences

Small functional cycles still need strict checks. Directory and dependency rules must be explicit. Exceptions require a reviewed rationale and architecture decision; weakening a gate to pass a change is prohibited.

The [module-boundary proposal](../architecture/module-boundaries.md) now makes directory placement, public APIs and dependency direction concrete for Q14 review. Its particular package layout is proposed; this accepted baseline does not silently approve it or claim enforcement.

## Confirmation

Verify each introduced gate fails on a deliberate violation. Confirm local/CI parity, mandatory review and repository protections. Trace requirements to test evidence and retain the distinction between required, configured, and verified.
