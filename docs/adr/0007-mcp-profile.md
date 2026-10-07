# ADR 0007: Define a current MCP profile with explicit call directions

- Status: Proposed
- Recorded: 2026-09-27
- Decision-maker: Cesar Zea
- Requirements: R05–R08, R11, R13
- Open questions: Q04, Q06

## Context and problem statement

The requirement is to use current MCP and expose graph-authorized capabilities through the platform. Protocol compliance does not determine every optional capability or guarantee SDK support. Components also need to call back into the platform while serving their own operations.

## Decision drivers

Current protocol semantics, independently authored components, no managed-call bypass, explicit compatibility, and avoidance of nested-call deadlocks.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| stdio to local components; separate loopback HTTP to platform | Natural subprocess management and a shared platform endpoint | Two transports and an explicit identity/launch contract |
| Loopback HTTP in both directions | Uniform transport | Each component needs endpoint startup and lifecycle coordination |
| Treat the existing server stream as an arbitrary reverse-call channel | Appears simpler | Conflicts with current MCP message direction semantics |

## Decision outcome

Recommend the first option for the initial local profile. Use MCP `2026-07-28`, verified as the current revision on the recorded date. This does not approve an SDK version or claim implementation of every extension.

The [profile contract](../archive/previous-implementation/contracts/mcp-profile.md) identifies required base behavior and proposes an initial tool-oriented surface. Optional capabilities and older-protocol compatibility must have explicit support decisions. There is no silent fallback to older behavior.

The profile's [SDK candidate and conformance plan](../archive/previous-implementation/contracts/mcp-profile.md#sdk-candidate-and-conformance-work), recorded 2026-09-28, proposes Python SDK 2.2.0. Subsequent [temporary feasibility probes](../archive/previous-implementation/contracts/sdk-compatibility.md) exercised stdio, loopback HTTP and familiar client shapes. Pinned mode and its cached discovery helper sent no discovery request; readiness must explicitly request and validate the peer's response. This is SDK evidence, not an implemented platform integration.

## Consequences

Components acting as consumers need their own client path to the platform. Native MCP clients use the proposed MCP transport; familiar model clients use compatibility adapters into the same admission and MCP dispatch path. The requirement to support familiar outgoing calls is accepted in [ADR 0004](0004-component-packaging.md); exact transport and SDK mappings remain proposed here. Application work sessions and state cannot be inferred from transport connections. The gateway filters both discovery and invocation, and binds identity outside untrusted payload fields.

The tested `langchain-mcp-adapters` release requires MCP below version 2 and cannot join the candidate environment. A small adapter using standard LangChain tools and the MCP 2 client is proposed instead. Default SDK capability advertisements must also be reviewed and filtered; a tools-only platform profile cannot be inferred from registering only tool handlers.

## Confirmation

Approve transport and scope, verify selected SDKs against the profile, and exercise discovery, denied calls, nested requests, metadata, cancellation and unsupported features. Link evidence to QA03, QA08 and QA14.

## Sources

[Versioning](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning) and [transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports) provide the protocol basis; platform policy is specified separately.
