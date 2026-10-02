# HTTP boundaries

Exposes operator queries, immutable personal experiment authoring and familiar model calls through authenticated local HTTP routes.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.

Execution-enabled composition installs `definition_router` behind the operator boundary.
Source/draft responses supply canonical domain JSON text for authoring, preserving numeric values.
S03 targeted HTTP/Start tests cover authoring, strict transport, authority, paging,
exact identities and bounded failures. Whole-system verification remains pending.
