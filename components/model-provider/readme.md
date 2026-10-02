# Provider-neutral model resource

`slow_thinker_model_provider` hosts one managed native Chat Completions attempt for
reviewed OpenAI or DeepSeek profiles. Import `ModelProviderHost`, `parse_config`,
`normalized_request`, `effective_operation`, `ProviderEndpoint` and
`ProviderTransport` from the public package entry point.

Graphs select a provider profile and model alias. Trusted preparation supplies the
actual model, supported reasoning modes, output bounds, endpoint and launch-only
credential. The component preserves native response/error bodies, headers and UTC
transport timing; it performs no accounting or provider retries.

The canonical descriptor is [model-provider.component.json](model-provider.component.json)
and [registration.json](registration.json) identifies distribution
`slow-thinker-model-provider` version `0.1.0`. B owns its installation recipe.
See [specification.md](specification.md) and the
[shared model contract](../../docs/contracts/model-resources.md).
Scoped acceptance tests pass with recorded prices and simulated native transports;
coordinator review and full verification remain pending.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
