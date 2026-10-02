# Provider-neutral acceptance specification

Follow [A01–A07](../../../docs/specification/s04-s06-delivery.md) and the
[model resource contract](../../../docs/contracts/model-resources.md).

Use root-owned recorded tariff/workspace fixtures and public package entry points.
Tests own their isolated SQLite stores and immutable model policies. Verify exact
request options, pre-dispatch rejection, native usage and reasoning retention,
conservative reservation, integer-quanta settlement, calendar/timing ambiguity,
independent daily source retention and historical snapshot/charge stability.

Ordinary SDK/LangChain cases use actual loopback HTTP gateway, managed authority,
real host transport and pricing with simulated native HTTP replies. Preparation
uses production InstalledWorkflowPreparer with description-only installations;
its evidence establishes admission/snapshot freezing, not installed inference.
Fixtures never read provider credentials or perform paid calls.

Outgoing-client regressions inspect the production preparer's frozen launch
evidence. Description-only calculator/memory installations isolate composition:
hosts without outgoing access retain their exact client sets, granted callers
without slots retain gateway access, and legacy client records survive injection.
Actual installed entrypoint startup remains coordinator verification.
