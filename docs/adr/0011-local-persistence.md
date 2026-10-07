# ADR 0011: Use one local transactional store behind persistence interfaces

- Status: Accepted on 2026-10-07 with S06 for local operation; PostgreSQL replaces SQLite from S08 (local) and S17 (cloud) under a later decision
- Recorded: 2026-09-28
- Decision-maker: Cesar Zea
- Accepted scope, 2026-09-28: local SQLite, backend-mediated storage, transactional reservations/state/evidence and no automatic paid replay. Detailed settings and recovery mechanics below remain proposed.
- Requirements: R11–R16, R20, R22
- Open questions: Q07–Q10, Q18

## Context and problem statement

The initial application has one local backend, one operator and independent component processes. Budget reservations, run state and evidence must survive a crash consistently. External provider calls cannot participate in the local database transaction, so a crash can leave their outcome unknown.

## Decision drivers

Simple local operation, atomic admission across all budget scopes, durable evidence, explicit dispatch uncertainty, bounded transactions and a replaceable storage adapter for future deployments.

## Considered options

| Option | Benefits | Costs and limitations |
| --- | --- | --- |
| SQLite in the backend | No separate database service; local transactional storage | One writer at a time; local-filesystem constraints |
| PostgreSQL | Suitable for future concurrent server processes | Additional service, configuration and operations for the initial local cycle |
| Independent JSON/event files | Human-readable artifacts | Cross-file atomicity, locking, recovery and accounting become application responsibilities |

SQLite documents its suitability for device-local storage and its single-writer constraint. These match the initial deployment; they do not establish future multiwriter capacity. [Appropriate uses](https://www.sqlite.org/whentouse.html).

## Decision outcome

The owner selected SQLite for the first cycle on 2026-09-28, with backend-mediated storage and interfaces allowing a later engine change. Propose one database on a local filesystem, owned exclusively through the backend's persistence adapter. Components receive no database handles or file paths as part of their execution contract. Domain modules use typed repository and transaction interfaces, not SQL or SQLite types. Graph source JSON remains an input artifact; run snapshots, evidence and accounting are stored together. Engine selection does not implicitly approve every setting or recovery rule below.

Start with rollback journaling (`journal_mode=DELETE`), `synchronous=EXTRA` and enabled foreign keys. Read back and verify these settings on connection setup. SQLite documents EXTRA as the stronger rollback-journal durability setting; filesystem/VFS behavior remains part of deployment verification. [Synchronous settings](https://www.sqlite.org/pragma.html#pragma_synchronous).

One backend process owns scheduling and writes; a second executor against the same store is refused. Serialize short write units, including nested-call admissions; never hold a database transaction while waiting for a component, provider or browser. Begin admission updates with `BEGIN IMMEDIATE`; lock waits are bounded by the operation deadline. A lock failure cannot fall back to dispatch without a reservation. [Transaction behavior](https://www.sqlite.org/lang_transaction.html).

Use ordinary current-state tables plus append-only accounting/evidence records. No general event-sourcing framework or event-bus service is required. Persist bounded text/JSON payloads in the same database initially, so committed evidence cannot reference a missing external file. Payload limits and redaction rules remain Q10/Q18; this proposal does not silently truncate data.

### Transaction boundaries

| Boundary | Changes committed together | What becomes permitted afterward |
| --- | --- | --- |
| T1: create run | Unique operator command and receipt, immutable definitions/input/profiles, saved-session association, limits, initial run state and event | Start owned hosts and readiness checks. |
| T2: reserve attempt | Active authority/deadline checks; identity, request snapshot, tariff/bound evidence; reservation in every scope; `reserved` attempt and event | Attempt is funded but cannot yet reach an external provider. |
| T3: authorize dispatch | Recheck stop/deadline/authority; atomically move that attempt to `dispatch_intent` and append event | Its designated sender may submit the exact saved request once; no hidden transport retry. |
| T4: receive result | Response/usage evidence, attempt disposition and settlement when possible; any eligible output publication and state changes | Return the committed result or make the dependent step eligible. Late results settle/record without graph advancement. |
| T5: stop or recover | Close admission, revoke current work authority, record run/call dispositions and events; preserve unresolved obligations | Cancel owned work and begin bounded cleanup. |

T3 is the durable authorization boundary. A stop accepted before T3 prevents dispatch. A stop after T3 cancels authorized work on a best-effort basis; the transport may already be sending. Do not claim that physical network transmission and a local stop are globally atomic. Recheck the stop before submission when possible, without assuming that this removes the race.

Uniqueness constraints cover attempt identity, source usage/settlement identity and per-run event sequence. One attempt has one accounting contribution, referenced by its ancestors. Conditional state updates prevent two senders from claiming the same attempt. The backend is the identity authority; caller-provided request IDs alone cannot create another charge or authorize a retry.

The [operator API proposal](../archive/previous-implementation/contracts/operator-api.md#start-command-and-durable-receipts) adds unique command identities and retained receipts/tombstones. Concurrent duplicate Starts resolve to one T1 result. Withdrawing an unconfirmed Start serializes against that same boundary: either it prevents admission, or it stops the already admitted run without erasing its receipt. A lost browser reply cannot authorize another execution.

### Crash and storage-failure cases

| Failure point | Required recovery |
| --- | --- |
| Before T2 commits | No reservation and no permitted external call. |
| After T2, before T3 | Invalidate the old sender's authority; recorded state proves dispatch was never authorized. Release the reservation with evidence; do not execute the queued request after restart. |
| During/after T3, before any durable result | If T3 committed, dispatch may or may not have occurred. Retain the obligation and mark the outcome unknown. If commit status cannot be established, suspend admission rather than assume rollback. |
| Provider completes before T4 commits | Preserve the bound; lack of a stored response is not proof that the provider did no work. No automatic paid replay. |
| T4 commits, then backend/browser loses the reply | Inspect the committed result and charge; duplicate delivery has no second effect. Recovery still interrupts any nonterminal run and does not continue its sequence. |
| Disk full, I/O failure or corrupt store | Stop new dispatch immediately. Attempt cancellation of authorized work; do not claim failed writes are durably logged. On recovery, retained reservations remain uncertain until reconciled. |

Database recovery starts before normal admission: validate the supported schema/configuration, invalidate prior execution grants, mark unfinished runs interrupted and reconcile owned processes and reservations. Never delete/recreate a damaged store as an automatic repair. A PID alone is insufficient proof that a process belongs to the previous run.

### Schema evolution, backup and retention

Version migrations explicitly; fail closed on a newer unsupported schema. Apply migrations only with execution stopped and a verified pre-migration backup, preserving attempt and monetary identities. Use a consistent SQLite backup operation rather than copying an active database file unsafely. [Backup API](https://www.sqlite.org/backup.html).

Restoring an older backup can hide later provider spending. Open a restored store without billable admission until that gap is reconciled; restarting the application is not evidence that its old balance is current. Do not merge or reset monthly ledgers implicitly.

Payload retention may remove or redact content only under the future explicit retention contract; preserve its absence marker, event identity and accounting evidence. Retention must not reduce recorded charges or release obligations. SQLite deletion is not a promise of secure erasure. Encryption, automated backup schedules and external blob storage are not selected by this ADR.

## Consequences

The first installation avoids a database service. Short transactions and bounded payloads constrain write contention; performance remains to be measured under Q18. SQLite is an adapter choice, not a component contract. Future server concurrency may require PostgreSQL, WAL or a different persistence strategy through a new decision and migration; swapping adapters alone does not prove equivalent recovery semantics.

The database can make local records atomic, but cannot guarantee exactly-once external effects. The supported initial recovery policy preserves uncertainty and requires reconciliation instead of automatic replay. Operator reconciliation must remain available when a provider cannot retrieve historic usage.

## Confirmation

QA06–QA11 and QA25 require deterministic interleavings, duplicate delivery, crash injection around T1–T5, lock contention, storage failures and restored-backup recovery. Verify foreign keys and durability settings on the chosen Python/SQLite runtime. Test migration failure without loss of the original database and accounting history. No database or application code is created by this proposal; package versions, payload limits and migration tooling remain to be selected before implementation.
