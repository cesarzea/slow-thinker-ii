# ADR 0012: Review for a single-maintainer repository

- Status: Accepted; remote approval-count change applied and verified
- Recorded: 2026-10-01, Europe/Lisbon
- Decision-maker: Cesar Zea
- Refines: [Engineering baseline](0001-engineering-baseline.md)

## Context and decision drivers

Cesar Zea is the sole maintainer and has no independent approver. GitHub prevents
authors from approving their own pull requests. The existing one-approval rule
therefore blocks delivery even after review and successful verification. The owner
confirmed this constraint and explicitly authorized changing the required approval
count from one to zero while retaining the other protections.

## Considered options

| Option                                          | Consequence                                                      |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| Require an independent approval now             | Cannot be fulfilled under the current ownership model.           |
| Keep PRs and checks, with explicit owner review | Feasible, preserves traceable changes and automated enforcement. |
| Bypass all branch protections                   | Removes unrelated controls and is rejected.                      |

## Decision outcome

Set only the required approval count to zero, retaining PR-only changes, required
checks, strict branch freshness, administrator enforcement, linear history and
squash merges. The owner still reviews and decides whether to merge; CI success
does not constitute that decision. All commits and pushes retain Cesar Zea's
identity. No substitute account or artificial approval is introduced.

## Consequences and confirmation

Independent human review is unavailable; owner review cannot claim the same
assurance. Record review and verification evidence in delivery documentation.
Revisit the approval count when an independent maintainer becomes available.
Compare remote protection settings before and after the change: only the approval
count may differ. A failing required check must continue to block merging.

## Confirmation — 2026-10-01

The authenticated GitHub account was `cesarzea`. The review requirement changed
from one approval to zero. A complete comparison of main-branch protection before
and after the update confirmed that no other setting changed. Required checks
remain `verify`, `analyze (python)`, `analyze (javascript-typescript)` and `validate`;
strict freshness, administrator enforcement, the pull-request requirement and
linear history remain enabled. No pull request was merged by this configuration
change. Private before/after snapshots are retained outside version control.
