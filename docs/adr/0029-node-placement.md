# 0029. Placement of nodes in containers

| Decision control | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Status           | Accepted; delivered locally in S08 and on AWS in S18         |
| Date             | 2026-10-07                                                   |
| Deciders         | Cesar Zea (owner)                                            |
| Requirements     | CR02, CR08, CR22                                             |
| Refines          | [ADR 0023](0023-container-ready-component-boundary.md)       |

## Context and problem

S06 starts one host process per node or embedded component on the local machine, with
no isolation from the platform or from other users. Users' graphs must run isolated,
but isolation has a cost: one container per agent multiplies start-up time and cloud
cost, and one process per component pays an interpreter start for every node. Agents of
one user's graph trust each other; companies and third-party code do not.

## Decision

- **Placement is its own dimension,** apart from the graph. Two presets: all nodes of a
  run in one container, or each node in its own; the user can move any node to another
  container. Placement may later become a variable the optimizer adjusts.
- **Rules the user cannot override:** a container never mixes workspaces, and
  third-party code always runs in its own container.
- **Inside a container,** compatible components run as threads with an in-memory
  transport and incompatible ones as separate processes. Compatibility is checked when
  a run is prepared: same runtime, dependencies that resolve together with one version
  of each library, and no component that declares it needs its own process.
- **Messages always pass through a mediator** that records them while supervised and
  passes them straight through when not; billable calls are metered either way. Events
  reach the platform through a message broker without blocking.
- **Between containers,** MCP over HTTP with mutual TLS and the platform's short-lived
  call grants. SSH is not used.
- **While supervised,** a container's network reaches only the platform, so no call
  bypasses mediation.
- **Where containers run:** Docker locally in S08; ECS Fargate on AWS in S18, whose
  microVMs isolate more strongly than Docker. Other clouds come through the launcher
  interface of ADR 0023.

## Consequences

- Components need Linux images with their locked dependencies.
- One broker serves these events and the ordered queues of S14.
- Docker isolation suffices locally and for the private beta; running anyone's code in
  production requires the stronger isolation of S18.
