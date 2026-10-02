# Workflow runtime preparation

Resolves a start intent into verified component hosts, resource bindings and a frozen workflow.

Definitions are read through the public `library.DefinitionReader` port, allowing
an exact bundled or personal revision to use the same production preparation path.

Use the [public entry point](__init__.py); private implementation files are not an integration API.

See [specification.md](specification.md) for contracts and acceptance criteria.

First-cycle additions are implemented and covered by backend tests.

Provider-neutral preparation adds optional scoped model tariffs, frozen evidence
per resource and runtime identity for managed state. Existing OpenAI callers and
the global tariff snapshot remain supported. Public `model_capabilities` exposes
reviewed settings without credentials; `model-resource` selects the new adapter.

Outgoing MCP clients are added only when an instance has resource bindings or
discoverable outgoing grants. Other host profiles retain their existing clients.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
