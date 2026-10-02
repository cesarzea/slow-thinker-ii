# Local application composition

Builds the backend from explicit configuration and manages its local runtime lifetime.

Configured operator applications compose the definition library and its routes.
Preparation reads through an equivalent library against the same database and
bundled files. Viewer and legacy graph routes continue using the bundled catalog.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.
