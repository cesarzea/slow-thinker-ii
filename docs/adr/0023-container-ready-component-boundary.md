# ADR 0023: Container-ready component boundary

- Status: Accepted on 2026-10-07 with S06; placement of nodes in containers is decided in [ADR 0029](0029-node-placement.md)
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR02, CR17
- Amends: [ADR 0004](0004-component-packaging.md) and [ADR 0007](0007-mcp-profile.md)

## Context and problem statement

Components will later run in isolated containers without losing monitoring. S06
runs trusted local processes, but its protocol must not depend on sharing a machine
with the platform.

## Decision outcome

- Invocations carry a relative time budget in milliseconds, never an absolute
  monotonic clock value.
- Platform endpoints given to components are configurable URLs with bearer
  authentication by invocation grant; nothing assumes loopback.
- Components receive no provider credentials; only platform services hold them.
- Components reach networks, files and services only through the platform.
- Launching a component goes through one launcher interface, so that a container
  launcher can replace the local process launcher.
- Configuration reaches a component through its bootstrap document, not through
  shared files written at runtime.

## Consequences

The S06 local launcher is one implementation of the launcher interface.
Container images per installed component version, network policies and a
container launcher are delivered in sprints S08 and S18 without protocol changes.
