# Browser API client

Provides typed, validated HTTP access to catalog, personal definitions, operator commands and execution evidence.

Use the [public entry point](index.ts); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

The API preserves validated wire values and provides English client error messages. Saved graph details also expose their execution metadata.

Use `DefinitionClient` with an operator credential for the personal library and raw
JSON validate/save requests. Every operation accepts an abort signal; uncertain saves
report a fixed recovery message. Viewer reads retain `loadGraphs` and `OperatorClient.graph`.
`source` and `draft` return the server's original JSON text for lossless authoring;
identity checks never replace it with a browser serialization.

## S04–S06 development

ConfigurationClient reads validated trusted discovery and submits exact frozen limit
command bodies. DefinitionClient.patch returns raw object text for incomplete
drafts. Definition replies use a streaming 1 MiB bound. Review and functional
verification remain pending in [verification record](../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02).

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
