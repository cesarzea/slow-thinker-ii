# External authored resource-aware agent

This independent Hatchling package, `example-resource-agent` version `0.1.0`,
exports `ResourceAgent` as a public `LLMCall` subclass. It adds explicit guidance
for supplied resource context while retaining configurable instructions, input
schema, generation parameters and text/JSON output. It uses the ordinary managed
model client and contains no backend imports, credentials, provider endpoint or
installation code.

Prepare it explicitly from the repository root with the controlled development
toolchain active:

```sh
python -m tooling.components \
  --external-project examples/resource-agent \
  --registration examples/resource-agent/registration.json \
  --descriptor examples/resource-agent/resource-agent.component.json \
  --dependency-project components/host \
  --dependency-project components/llm-call \
  --destination .local/components
```

Preparation validates the [registration](registration.json), canonical
[descriptor](resource-agent.component.json), static distribution identity and exact
source dependency projects. It builds/hashes wheels, resolves the production
closure, installs offline and verifies the public entry point and actual LLMCall
ancestry. The CLI reports the type and resolution IDs, bundle and copied descriptor
path; the bundle's `descriptors` map records that trusted absolute path.

In trusted startup settings, add the copied descriptor to `descriptors` and an
installation with `type_id="example.resource-agent"`, `type_version="0.1.0"`,
the reported `resolution_id` and `host_adapter="openai-client"`. Preserve the
prepared `installation_catalog` directory. Bind the graph agent's `model` slot
to a declared model resource and grant its `complete` operation. The graph never
contains package paths or Python import strings.

For resource composition, bind ContextualCall's `worker` slot to this agent's
`generate` operation. Configure matching input/output schemas, optional memory
get/put flags and calculator settings, and grant only the enabled nested operations.
The agent receives explicit `memory`/`calculation` input fields. All model and
resource calls remain mediated; the authored agent never calls a peer directly.
[specification.md](specification.md) links the approved contract. Targeted build,
offline installation and managed MCP execution checks pass using bounded provider
fixtures. Shared whole-system verification remains pending.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
