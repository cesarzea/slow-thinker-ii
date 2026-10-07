"""Shared in-memory fakes of the engine and application ports, and contract example loaders.

Import from the submodules (``backend/tests`` is on the test path):

- ``support.clock.FakeClock``: engine and application ``Clock``.
- ``support.log.RecordingLog``: engine ``RunLog``.
- ``support.grants.RecordingGrants``: engine ``GrantIssuer`` over ``access.Grants``.
- ``support.hosts.ScriptedHosts`` and behaviours: engine ``Hosts``.
- ``support.graph_store.MemoryGraphStore``, ``support.run_store.MemoryRunStore``,
  ``support.ledger.MemoryLedger``: application stores and ledger.
- ``support.launcher.FakeHostLauncher``: application ``HostLauncher`` and ``RunHosts``.
- ``support.providers.ScriptedProvider``: application ``LlmProvider``.
- ``support.components.ComponentHosts``: hosts behaving like LLM Call and Router.
- ``support.examples`` and ``support.configuration``: journey graphs, catalog, models,
  tariffs and budgets read from the contract examples and the server configuration.
- ``support.platform.Platform``: every use case composed over these fakes.
"""
