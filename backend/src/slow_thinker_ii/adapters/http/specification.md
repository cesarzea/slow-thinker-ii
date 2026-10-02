# HTTP boundaries: specification

Exposes operator queries and familiar model calls through authenticated local HTTP routes.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- catalog_router serves graph summaries.
- operator_router exposes workspace, command, run and evidence operations through application ports.
- openai_router exposes the supported model request profile.
- tariff_router reports local catalog refresh state.
- definition_router exposes personal definition pages, exact detail/source, unsaved drafts, validation and immutable saves.

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

S03 targeted tests in `backend/tests/integration/definition_http` and the Start
boundary suite use the shared real SQLite library. They cover the shared authoring,
transport, authorization, identity, paging and diagnostic-bound scenarios, including
lossless numeric text and exact replay after an injected post-insertion failure.
Complete mandatory and whole-system verification remain coordinator-owned.

## Sprint additions

- [managed-gateway](../../../../../docs/contracts/managed-gateway.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [inspection-projections](../../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

The /mcp endpoint uses a pinned SDK Streamable HTTP transport scoped to each authenticated invocation. Operator routes expose exact graph revisions, saved definitions and bounded execution snapshots. Reports remain platform instrumentation, separate from billable tool calls.

## S03 personal experiment library

Follow the [shared contract](../../../../../docs/contracts/personal-experiments.md) for wire values, data origins,
public interfaces, validation scope, errors, immutable identity, paging and failure
handling. Implementation owner: B.

`definition_router(library.ExperimentLibrary, max_payload_bytes)` implements the
six specified routes. Composition supplies operator authentication; each route
uses `no-store`. Raw UTF-8 POST text is strictly decoded without changing the source
passed to the library. GET fields are exact and reject unknown/duplicate options.
Complete success representations use the configured byte bound. Fixed error
envelopes have a separate 4096-byte bound and omit trailing issues to fit.
Library paging/signatures and save semantics remain application responsibilities.
Start accepts canonical graph-ID syntax without a length maximum and arbitrary
nonempty graph revisions. Existing command/session/configuration identities and
legacy graph routes retain their contracts.

Source reads apply the detail query rules and serialize public raw library
definitions with `decode_json`/`encode_json`, preserving Python numeric values.
Draft requests contain only strict source/target identity objects and delegate
variant construction/validation to `ExperimentLibrary.draft`. Both return bounded
canonical domain JSON text without a projection envelope or `view_token`.

Acceptance follows the shared S03 scenarios. Development delivery does not claim
testing is complete. Keep module-private choices within these public contracts.

## S04–S06 active delivery

Follow [the shared contract](../../../../../docs/contracts/product-workspace.md). Implementation owner: Coordinator.

Add authenticated bounded configuration/catalog, configuration/limits and definitions/patch endpoints exactly as specified. Preserve existing APIs, origin/credential checks, no-store and error semantics. Return canonical source text without inserting or invoking a component.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
