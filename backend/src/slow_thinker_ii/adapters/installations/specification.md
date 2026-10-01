# Component installation catalog: specification

Prepares and verifies isolated component environments from exact hashed production dependencies.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- InstallationCatalog prepares, verifies, describes and resolves installed runtime environments.
- read_lock and installation records validate dependency and registration metadata.
- runtime and interpreter return verified launch artifacts.

## Required behavior

- Install only verified supplied wheels into an immutable environment; do not resolve upgrades during run startup.
- Retain exact dependency resolution and implementation-base identity.
- Verify installed artifacts and effective descriptions before use; ordinary local Python is trusted code, not a security sandbox.

## Dependencies and ownership

Public component registration contracts and explicit uv/Python executables.

## Acceptance criteria

- Corrupt wheels, unexpected installed files and incompatible implementation bases are rejected.
- An existing run resolution is unchanged by preparing another component version.

## Shared contracts

- [component-installation](../../../../../docs/contracts/component-installation.md)
- [0008-component-inheritance-and-versions](../../../../../docs/adr/0008-component-inheritance-and-versions.md)
