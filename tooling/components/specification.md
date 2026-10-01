# Component preparation commands: specification

Builds reproducible component bundles for explicit installation before experiment execution.

## Public boundary

The [public entry point](__main__.py) is authoritative for exported names and signatures.

- python -m tooling.components selects a supported component or all components and a destination.
- Preparation helpers build wheels, record source hashes and write exact installation bundles.

## Required behavior

- Resolve and download dependencies only during explicit preparation, not when starting a graph.
- Produce the registration and exact wheel artifacts consumed by InstallationCatalog.
- Do not embed provider credentials in prepared bundles.

## Dependencies and ownership

Component source packages, pinned packaging tools and public installation contracts.

## Acceptance criteria

- Prepared bundles can be verified and installed from their recorded artifacts.
- Rebuilding another component does not silently replace the dependency identity of a saved run.

## Shared contracts

- [component-installation](../../docs/contracts/component-installation.md)

## Implementation gaps

The first-cycle implementation, integration and repository verification checks pass.

## Sprint additions

- [conditional-routing](../../docs/contracts/conditional-routing.md) defines the planned cross-package contract; implement it without changing existing supported behavior.

`--selector-project` is an optional explicit trusted input for Redirector (or the
Redirector entry in `all`). Its static src-layout Hatchling distribution is built,
source-hashed and added as an exact requirement before normal dependency locking
and offline installation. Without it, Redirector includes the packaged example
selector. New routed-call and bounded-flow recipes use the same installation path.

## October 2026 maintenance: Preparation compatibility

Preparation continues to record the actual pinned uv executable version for new bundles. Production artifact hashes, explicit preparation boundaries and existing resolution identity remain unchanged; the selected development pin is uv 0.12.19.
