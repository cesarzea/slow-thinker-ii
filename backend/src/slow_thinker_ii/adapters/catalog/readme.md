# Graph catalog and compilation

Loads bundled experiment definitions and compiles them against installed component contracts.

`GraphDefinitionValidator` checks editable definitions using only local schemas and
registered descriptors. It does not describe installations or contact providers.
Its successful result covers definition validation; admission still performs the
installed-contract, resource, input and policy preflight checks.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.
