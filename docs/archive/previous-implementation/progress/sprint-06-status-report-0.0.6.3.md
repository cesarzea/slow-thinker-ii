# Sprint Status Report — S06

| Document control   | Value                                                               |
| ------------------ | ------------------------------------------------------------------- |
| Report ID          | SPRINT-S06-003                                                      |
| Report version     | **0.0.6.3** — V0.0, Sprint 6, Revision 3                            |
| Owner              | Cesar Zea                                                           |
| Reporting date     | 2026-10-03, Europe/Lisbon                                           |
| Scope              | Usable experiment configuration, versioning and execution workspace |
| Delivery status    | Locally verified; ready for owner usability review                  |
| Publication status | Uncommitted local delivery; publication not authorized              |

This report records the authorized redesign after the owner rejected the usability
of [Revision 2](sprint-06-status-report-0.0.6.2.md). Its complete snapshot retains
the earlier passing checks and subsequent rejection. Technical verification does
not constitute owner acceptance or a stable product release. Report versions remain
separate from package versions in the [central register](../../../../CHANGELOG.md).

## Delivered outcome

The searchable experiment collection leads into contextual Design, Resources,
Versions, Runs and Experiment settings. Component library and Workspace settings
retain global scope. The full-width canvas shows agents and execution transitions,
with optional configuration, resource connections and system markers. Selecting
an agent opens its inspector beside the graph. Long instructions expand into a
keyboard-accessible editor using the same draft buffer.

Ordinary fields, composition, compatible resources, explicit permissions and the
supported sequence/conditional profiles configure one controlled draft. Pending
or invalid edits remain visible and participate in navigation and execution guards.
Save creates an immutable revision; uncertain replies recover the same frozen
command. Versions offers saved history, comparison and derivation. Runs spans all
work sessions and retains each admitted definition, result and exact evidence.

The account/credit footer is an explicitly illustrative preview. Existing USD
accounting, deadlines, reservations and limits remain authoritative. No real
account or credit transactions are implemented.

## Acceptance and verification

The [S06-UX specification](../specification/s06-workspace-redesign.md) and governing
contracts define W01–W14. The [workspace guide](../workspace.md) describes usage.
The unchanged mandatory `make verify` passed **2,280 Python tests, 747 frontend
tests and 33 browser journeys**. Strict typing, lint, formatting, source limits,
module boundaries, dead-code detection, CodeQL, build, coverage and the existing
accounting mutation runner passed. No verification threshold or exclusion changed.

Frontend coverage is **97.26% lines, 90.7% branches,
97.02% functions and 96.04% statements**.
CodeQL reports no errors or warnings; 100 Python informational notes remain.
Accounting mutation results are 141 killed, 58 surviving and one timed out;
these are recorded rather than represented as complete effectiveness.
The [verification record](../verification.md#s06-workspace-redesign--2026-10-03)
and [sanitized evidence](../evidence/s06-workspace-redesign-verification-20261003.json) retain results and limitations.

| Acceptance    | Evidence                                                                                                                                                                                       |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| W01, W04, W09 | Complete collection/history, migration, immutable saving, lineage, exact comparison and uncertain-command application/storage tests; ordinary production-catalog save/import browser journeys. |
| W02–W07, W12  | Controlled selection/buffering, prompt dialog, declared/generic configuration, composition/bindings/grants, supported routing and reference-aware structural command tests.                    |
| W08, W11      | Resource-border geometry, polling, historical run identity, cross-session history and exact retained activation/call evidence tests.                                                           |
| W10           | Task/session/limit controls and authoritative start/stop/recovery tests, including stale receipts and navigation while commands are pending.                                                   |
| W13–W14       | Explicit illustrative footer, full-width/adjacent layout, keyboard focus and 390×844 automated browser journeys; direct 1440×900 keyboard and overflow inspection.                             |

## Local demonstration

A separate local HTTP/SQLite instance runs simulated component providers. An
ordinary Reviewer prompt edit created revision `r-5604b31a965e40bdb8792300fae50ba7`;
history and comparison retained the original. Run `caf3751032914555a0e32bdd059a675b`
completed a proposer/reviewer feedback loop in four activations. Its accepted
output and recorded activation evidence were inspected. A resource was added and
configured through forms, then its temporary draft was discarded.

The fixture records USD 0.0000003 of simulated accounting; actual provider spending
was zero. This demonstration does not claim new real-model validation. Existing
user data and the previously authorized USD 3 real-spending ceiling were preserved.
The browser at `http://127.0.0.1:5191/` is a transient local demonstration.

## Scope boundaries and review

Supported profiles remain finite sequence and bounded conditional collaboration.
Advanced JSON handles extension constructs outside ordinary forms. Graph nesting,
direct graphical connection editing, real accounts/credits and S07 evaluation are
not activated. No commit, push, merge or release forms part of this delivery.

The owner must review the redesigned interaction before user acceptance is recorded.
[C08](../../../continuous-improvement/cycles/008-workspace-redesign/report.md) evaluates
engineering practice separately and makes no unsupported productivity claim.

## Revision history

| Version | Date       | Change                                                                                                                                                          |
| ------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.0.6.3 | 2026-10-03 | Contextual workspace redesign, controlled draft/save lifecycle, functional version history/comparison, exact retained evidence and complete local verification. |
| 0.0.6.2 | 2026-10-02 | Earlier product completion; passing technical checks followed by owner usability rejection. Preserved as a complete snapshot.                                   |
| 0.0.6.1 | 2026-10-02 | Initial structured workspace checkpoint; preserved as a separate snapshot.                                                                                      |
