# Personal experiment use cases

Owns exact saved-definition reads, immutable saves, known-parent checks and bounded
library pages. Bundled definitions remain trusted and personal definitions are
append-only through an injected repository.

`draft(source, target)` returns a validated, canonical unsaved variant of an exact
saved source. It preserves numeric values and changes only identity and lineage;
saving remains an explicit separate operation.

Consume this capability through `from slow_thinker_ii.application import library`.
Construct `ExperimentLibrary` with explicit bundled, repository and validator ports
and a process-local signing key of at least 32 bytes. Construction performs no I/O.
See [specification.md](specification.md) for its contract.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
