# HTTP boundaries: specification

Exposes operator queries and familiar model calls through authenticated local HTTP routes.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- catalog_router serves graph summaries.
- operator_router exposes workspace, command, run and evidence operations through application ports.
- openai_router exposes the supported model request profile.
- tariff_router reports local catalog refresh state.

## Required behavior

- Validate hosts, origins, credentials, request sizes and request schemas at the boundary.
- Translate application errors without leaking credentials or accepting caller-asserted run identity.
- Keep business rules and monetary admission in application services.

## Dependencies and ownership

FastAPI and public application contracts; storage is accessed through ports.

## Acceptance criteria

- Malformed or unauthorized requests do not dispatch work.
- Operator projections and evidence pages preserve consistent identifiers and bounded cursors.

## Shared contracts

- [operator-api](../../../../../docs/contracts/operator-api.md)
- [call-authority](../../../../../docs/contracts/call-authority.md)

## Verification

Gateway tests cover pinned discovery, authenticated denials, revocation, origin/body limits and durable reports. Existing operator authentication and ETag tests pass; projection tests retain fixed paging boundaries.

## Sprint additions

- [managed-gateway](../../../../../docs/contracts/managed-gateway.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [inspection-projections](../../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

The /mcp endpoint uses a pinned SDK Streamable HTTP transport scoped to each authenticated invocation. Operator routes expose exact graph revisions, saved definitions and bounded execution snapshots. Reports remain platform instrumentation, separate from billable tool calls.
