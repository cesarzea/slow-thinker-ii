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
