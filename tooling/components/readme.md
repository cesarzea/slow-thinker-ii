# Component preparation commands

Builds reproducible component bundles for explicit installation before experiment execution.

Use the [public entry point](__main__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle implementation and local acceptance checks are complete.

`--component all` includes `redirector`, `routed-call` and `bounded-flow` alongside
the existing four components. Their distribution and component versions are
`0.1.0`; the shared host dependency remains exactly `0.1.0.dev1`.

The default Redirector recipe includes the example selector distribution. To use
another authored selector, pass `--selector-project /absolute/project` with
`--component redirector` or `all`. This is an explicit trusted preparation input,
not a graph or invocation argument. The selected project must be a static-version,
src-layout Hatchling package. Its built wheel, source digest and exact package
requirement enter the same hashed production closure and offline installation
workflow. Graph configuration names an installed public `module:callable` only.
No package installation or source loading happens at invocation time.


S04–S06 adds built-in recipes `model-provider`, `calculator`, `key-value-memory`
and `contextual-call`, all component/distribution version `0.1.0`. `all` retains
every existing recipe. Each new package owns its canonical descriptor and registration.

External authored components use explicit `--external-project`, `--registration`,
`--descriptor` and repeatable `--dependency-project` inputs. Sources must have static
metadata, the controlled Hatchling backend/build requirement and a src layout.
Validated distribution/type identities, exact dependency projects, source/wheel
hashes and canonical descriptor/registration hashes enter the preparation evidence.
The prepared external bundle copies both declarations beside its JSON manifest,
with a `descriptors` map from component name to absolute copied descriptor path.
Built-in bundle manifests retain their existing three fields. See the independent
[resource-agent preparation guide](../../examples/resource-agent/readme.md).
Targeted recipe, external validation, offline installation and managed MCP
execution checks pass. Shared whole-system verification remains pending.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
