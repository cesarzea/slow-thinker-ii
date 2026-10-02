# Workflow runtime preparation

Resolves a start intent into verified component hosts, resource bindings and a frozen workflow.

Definitions are read through the public `library.DefinitionReader` port, allowing
an exact bundled or personal revision to use the same production preparation path.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.
