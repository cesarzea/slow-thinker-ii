# 0028. Companies, users and workspaces

| Decision control | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Status           | Accepted; delivered from S07                                 |
| Date             | 2026-10-07                                                   |
| Deciders         | Cesar Zea (owner)                                            |
| Requirements     | CR19, CR20, CR21                                             |
| Origin           | [Scope review of 2026-10-06](../specification/scope-review-2026-10-06.md), item 1.8 |

## Context and problem

S06 is single-user. On 2026-10-04 the owner agreed that the data model would carry a
user and workspace dimension from the start, and it did not. The platform will be a
paid multi-user service: users belong to companies, and a company's data and runs must
never reach another company. Security and isolation have to shape the data model
before more is built on it, while registration and subscriptions can wait.

## Decision

- **Companies, users, workspaces.** A user belongs to a company; a company has several
  workspaces; a user accesses one or more workspaces of their company. Workspaces never
  span companies.
- **Every request is authorized** against the user's access to the workspace it
  touches. Graphs, Labs, runs, events, budgets and resources belong to a workspace.
- **Isolation between companies** holds in storage, in execution and in what the
  interface shows; a container never mixes workspaces ([ADR 0029](0029-node-placement.md)).
- **A workspace holds shared resources:** storage, databases, API connections and their
  credentials, available to its Labs and graphs through the platform. A Lab belongs to
  a workspace and holds graphs, experiments, variants and work sessions.
- **S07 has no registration.** Four seeded users, two in each of two companies; in each
  company one user opens two workspaces and the other one. Their test credentials come
  from local configuration, never from the code. Registration, invitations and member
  management come in S19.

## Consequences

- The operator API and every store gain a workspace scope; S06 data is migrated into a
  first company and workspace.
- Whether daily and monthly budgets apply per workspace or per company is decided when
  S07 is prepared, beside the work session budgets of CR12.
- Model providers stay platform services; provider credentials per workspace remain a
  later option ([ADR 0019](0019-platform-llm-service.md)).
