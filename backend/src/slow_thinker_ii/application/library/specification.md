# Personal experiment use cases: specification

## S03 personal experiment library

Follow the [shared contract](../../../../../docs/contracts/personal-experiments.md) for wire values, data origins,
public interfaces, validation scope, errors, immutable identity, paging and failure
handling. Implementation owner: A.

Implement the public interface skeletons and application use cases: exact reads,
canonical replay/conflict handling, parent validation, bounded signed pagination
and save orchestration. No adapter/framework imports. Cursor keys are explicit;
constructors perform no storage access. Preserve existing application exports.

Acceptance follows the shared S03 scenarios. Development delivery does not claim
testing is complete. Keep module-private choices within these public contracts.

## Development implementation

`ExperimentLibrary` resolves exact identities through bundled summaries and the
repository, uses the validator for detail and canonical saves, and checks bundled
collisions without modifying trusted files. Personal identity and parent checks
remain one repository transaction. Validation checks parent existence; saving
rechecks personal parents atomically.

`draft(source, target)` reads the saved source using exact `GraphReference` values,
rejects self-derivation, and changes only `graph_id`, `revision` and `derived_from`.
JSON numbers remain Python values through canonical decoding and serialization,
including floating-point `1.0` and integers above JavaScript's safe integer range.
The operation uses the existing static and known-parent validation and returns
canonical domain JSON. It does not insert, reserve a target identity or invoke a
component/provider; occupied target identity decisions remain with Save.

HMAC-SHA256 cursors bind the requested page size, bundled position and personal
upper/last sequence. Cursor decoding rejects foreign keys, altered fields, invalid
ranges and changed page sizes. The repository fixes the personal boundary even
when the current page contains only bundled entries. Refresh starts a fresh window.
Focused S03 acceptance and scoped static checks pass; complete coordinator
verification remains pending.

## S04–S06 active delivery

Follow [the shared contract](../../../../../docs/contracts/product-workspace.md). Implementation owner: Coordinator.

Preserve exact definition/source/draft/validation/save APIs. Source patches operate on unsaved text in application.workspace and return canonical text; immutable save and lineage checks stay with ExperimentLibrary.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
