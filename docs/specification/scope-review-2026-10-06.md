# Scope review of 2026-10-06

| Document control | Value                                                                 |
| ---------------- | --------------------------------------------------------------------- |
| Document ID      | SCOPE-REVIEW-2026-10-06                                               |
| Owner            | Cesar Zea                                                             |
| Dates            | 2026-10-06 to 2026-10-07                                              |
| Result           | [Requirements revision 3](requirements.md) and [roadmap revision 3](roadmap.md) |

Rewriting the requirements for the new execution core (R01–R31 into CR01–CR18) and
replacing sprints S01–S16 with steps 1–9 reduced the scope in points the owner never
explicitly approved. The owner found it on 2026-10-06. This record compares the
previous documentation with revision 2 and keeps the owner's decision on every item.
From now on, every rewrite of a scope document lists what it removes, reduces or
changes, for the owner's approval.

Compared: the previous requirements (R01–R31), the previous sprint roadmap (revision 9,
S01–S16) and open questions (Q01–Q23), the README published on `main`, against
requirements revision 2 (CR01–CR18), roadmap revision 2 (steps 1–9), ADRs 0015–0027 and
the code of the `core-foundation` branch.

## Dropped from the scope

| #   | What it was                                                                                                     | Where it was           | Decision  | Owner's note                                                                 |
| --- | --------------------------------------------------------------------------------------------------------------- | ---------------------- | --------- | ---------------------------------------------------------------------------- |
| 1.1 | Deep analysis of the collaboration, with its evidence semantics                                                 | R25, R26; S09          | Recover   | One of the product's strengths: it makes it possible to propose improvements towards cost, time, results, accuracy |
| 1.2 | Graphs that change while they run; reusable subgraphs                                                           | R04; S10               | Recover   | Fundamental                                                                  |
| 1.3 | Pause and resume; extensible messages and events                                                                | S11                    | Recover   | Necessary                                                                    |
| 1.4 | Creating and changing experiments with a prompt                                                                 | S13                    | Recover   | Necessary                                                                    |
| 1.5 | Component inheritance with version ranges and exact resolutions                                                 | R27, ADR 0008          | Recover   | Include in the scope                                                         |
| 1.6 | OpenAI, LangChain and LangGraph compatibility; permission-filtered MCP proxy                                    | R06, R08               | Recover   | Include in the scope                                                         |
| 1.7 | "Collaboration techniques" as an extension role                                                                 | R03                    | Recover   | Later, as a library of patterns on reusable subgraphs                        |
| 1.8 | Workspaces and the user and workspace dimension in the data                                                     | Agreed on 2026-10-04   | Recover   | Workspaces must exist, several per user, each with its own resources        |

## Reduced scope

| #   | Before                                                                                       | Where it was          | Decision | Owner's note                                                                                             |
| --- | -------------------------------------------------------------------------------------------- | --------------------- | -------- | -------------------------------------------------------------------------------------------------------- |
| 2.1 | Export to readable, standalone Python code                                                   | R28, ADR 0009, S15    | Recover  | Readable, professional and reviewable code; it may keep the graph's architecture with thin intermediate classes |
| 2.2 | Deadlines per call and per run, including waits and retries                                  | R13                   | Recover  | Necessary                                                                                                |
| 2.3 | Evaluation with task sets, criteria, weights, repetitions and evaluator reliability          | S07, Q15              | Recover  | Necessary                                                                                                |

## Delivered and lost

| #   | Capability                                                              | Where it was   | Decision | Owner's note                                                       |
| --- | ----------------------------------------------------------------------- | -------------- | -------- | ------------------------------------------------------------------ |
| 3.1 | Editing and importing the graph as JSON                                 | S03; R17, R31  | Recover  | Necessary; graphs are still JSON documents, only the interface is missing |
| 3.2 | Daily automatic import of tariffs                                       | Q03            | Recover  | Necessary                                                          |
| 3.3 | A calculator tool and key/value memory                                  | S05, Q22       | Discard  | Forget it                                                          |
| 3.4 | Work sessions with their budget; experiments and variants with provenance | S03, S06; R14, R16 | Recover | Necessary                                                       |
| 3.5 | Workspace resources view                                                | S06            | Recover  | Necessary                                                          |

## Changes of approach

| #   | Change                                                     | Decision                                                   |
| --- | ---------------------------------------------------------- | ---------------------------------------------------------- |
| 4.1 | Order of priorities                                        | Redone with everything recovered: [roadmap revision 3](roadmap.md) |
| 4.2 | Independence from the original Slow Thinker project        | Confirmed                                                  |
| 4.3 | Documents inconsistent with the scope                      | Corrected with revision 3                                  |

## Added in the review

- The final platform's purpose and rationale, now in the [requirements](requirements.md):
  graphs proposed, imported or designed on the same level; Labs for manual, supervised
  and automatic experimentation; demonstrated comparisons on incremental test sets.
- Companies, users and workspaces, with isolation between companies from S07
  ([ADR 0028](../adr/0028-companies-users-and-workspaces.md)).
- A marketplace of graphs and components.
- Self-serve sales without staff: registration, prepaid credits, payments and a paid
  launch; the platform on AWS with container isolation and cost control.
- Placement of nodes in containers, threads inside a container and mutual TLS between
  containers ([ADR 0029](../adr/0029-node-placement.md)).
- Deep analysis based on a plan per graph, after the platform handles persistent
  storage, queues and concurrency.

Not adopted: SSH between containers, replaced by mutual TLS; one container per agent by
default, replaced by placement per trust boundary.
