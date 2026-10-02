# Managed component processes: specification

Starts independent local component hosts and translates their MCP operations into application operation ports.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- ComponentProcess owns connection lifetime and process outcome.
- ComponentConnection prepares schema-checked arguments and invokes named operations.
- ProcessOperation implements OperationPort with optional pricing policy.
- InstalledGraphEnvironment, ProcessFleet and launch/host records manage verified runtime resources.

## Required behavior

- Pin the accepted MCP profile and verify real discovery and effective operation schemas before readiness.
- Pass trusted invocation grants and deadlines separately from business arguments.
- Bound startup, response capture and termination; preserve transport and accounting uncertainty.
- Process cleanup is independent of whether a run already has a terminal outcome.

## Dependencies and ownership

MCP SDK, subprocess facilities and public installation/application contracts; domain modules do not import this adapter.

## Acceptance criteria

- A mismatched host cannot become ready.
- Timeout or cancellation closes authority and initiates bounded cleanup without assuming billing has stopped.

## Shared contracts

- [component-lifecycle](../../../../../docs/contracts/component-lifecycle.md)
- [mcp-profile](../../../../../docs/contracts/mcp-profile.md)

## Verification

Process tests verify retained launch intentions, PID and fingerprint mismatches, real owned-child termination and forced kill, cleanup admission blocking and bounded diagnostics. An installed nonterminating Redirector selector is reaped after its deadline without retaining credential-bearing stderr.

## Sprint additions

- [managed-gateway](../../../../../docs/contracts/managed-gateway.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

Every production launch persists an intention before spawning, then records PID, creation instant, executable, command, workspace, process group/session and private ownership marker. Recovery signals only a completely matching identity; uncertain ownership remains unconfirmed. Process stderr contributes bounded diagnostic metadata, with raw text unavailable because it can contain unknown invocation credentials.

## October 2026 maintenance: Generator typing compatibility

The `@asynccontextmanager` implementations use `AsyncGenerator[YieldedType]`
for Pyright 1.1.414. `ComponentProcess.connect` and `InstalledProcess.connect`
yield `ComponentConnection`; `ProcessFleet.open` and `InstalledGraphEnvironment.open`
yield `Mapping[OperationAddress, OperationPort]`; `transport` and `channels` yield
the existing `Streams` tuple. Preserve all yielded values, cleanup and runtime
behavior; leave ordinary iterator contracts unchanged.

## S04–S06 active delivery

Follow [the shared contract](../../../../../docs/contracts/tools-memory.md). Implementation owner: Coordinator.

Keep independently installed host invocation/capture/ownership behavior. Trusted storage/provider client bootstrap is supplied by adapters; no graph-driven external command or unscoped environment secret.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.
