# Bootstrap

Reads the server configuration and the environment's secrets and composes the application:
SQLite stores, the catalog, grants, providers, component hosts, use cases and the HTTP app,
with a lifespan that owns the database, recovers interrupted runs and stops active runs on
shutdown. Nothing imports it; uvicorn starts `configured_app` as a factory.

Use the [public entry point](__init__.py); private implementation files are not an
integration API. See [specification.md](specification.md) for the configuration, the
composition and the acceptance criteria.
