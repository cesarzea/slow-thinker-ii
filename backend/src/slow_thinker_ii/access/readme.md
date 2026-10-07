# Access

Invocation grants for [derived authorization](../../../../docs/adr/0018-derived-authorization.md):
one bearer token per call of one activation, stored only as a SHA-256 digest.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for the interface, behaviour and acceptance criteria.
