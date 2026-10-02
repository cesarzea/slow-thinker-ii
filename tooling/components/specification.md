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

## S04–S06 active delivery

Owner B implements the complete tooling/components package. Follow
[tools and memory](../../docs/contracts/tools-memory.md) and the
[delivery block](../../docs/specification/s04-s06-delivery.md).
Add built-in recipes for model-provider, calculator, key-value-memory and
contextual-call (distribution/component version 0.1.0). Preserve existing recipes.
Add explicit external Hatchling src-layout preparation with --external-project PATH,
--registration FILE, --descriptor FILE and repeatable --dependency-project PATH.
Validate identity agreement and exact offline dependency closure before publishing
a bundle. External source paths are trusted preparation inputs, never graph fields.
A owns model-provider implementation; B owns its recipe. The coordinator owns root
package/quality configuration and shared example graph definitions.

## External bundle contract

External preparation retains built-in bundle fields `schema_version`, `catalog_root`
and `resolutions`, adding `descriptors: {component_name: absolute_descriptor_path}`.
The copied descriptor and registration live in `bundles/<bundle_id>/<component_name>/`;
the manifest lives beside that owned directory. The descriptor filename agrees with
registration. Trusted startup consumes the explicit copied descriptor path; graph
configuration cannot select source, registration or build inputs. Built-in manifests
omit `descriptors` and retain their established format.

Inner descriptor schemas use the trusted canonical contract registry. Preparation
checks static distribution/registration/descriptor identity and source layout before
building; the existing installation catalog verifies installed public exports,
ancestry, exact hash closure and interpreter/SDK compatibility before publication.
Canonical declaration hashes accompany source and built-wheel hashes in provenance.
Targeted tests cover all eleven recipes and the independent external component's
build, offline installation and managed MCP execution. Shared mandatory
whole-system verification remains pending.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
