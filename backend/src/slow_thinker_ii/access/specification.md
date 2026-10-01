# Invocation authority: specification

Controls which operations a component can discover and invoke during a managed run.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- AccessPolicy publishes permitted aliases and resolves scheduled and nested targets.
- CallAuthority schedules calls, issues invocation leases, resolves grants and closes or revokes authority.
- CallLimits and invocation records carry bounded call context; AccessDenied carries a rejection code.

## Required behavior

- Derive identity and parentage from platform-issued authority, never from request payload assertions.
- Apply permission checks separately to discovery and invocation.
- Inherit deadlines and reject prohibited ancestry or use of expired and revoked grants.

## Dependencies and ownership

Public definition and value contracts; the application layer owns durable recording and dispatch.

## Acceptance criteria

- A hidden or unauthorized operation cannot be invoked by guessing its name.
- Stopping or closing a call revokes the corresponding nested authority.

## Shared contracts

- [call-authority](../../../../docs/contracts/call-authority.md)
