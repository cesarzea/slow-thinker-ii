# Roadmap

| Document control | Value                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------- |
| Document ID      | PLAN-CORE                                                                              |
| Revision         | 2                                                                                      |
| Owner            | Cesar Zea                                                                              |
| Date             | 2026-10-05                                                                             |
| Working method   | [M07](../continuous-improvement/methods/007-validated-journeys.md)                     |
| Previous plan    | [Sprint roadmap of the previous implementation](../archive/previous-implementation/specification/sprint-roadmap.md) |

Each step closes with validated journeys, the complete verification runner and a
recorded owner acceptance. Step 1 is approved; on 2026-10-05, closing the step 1
review, the owner scheduled step 2 as the next sprint and set its scope. Later steps are candidates in an indicative
order; each requires its own journey validation before work starts.

| Step | Scope                                                                                                     | State                                  |
| ---- | --------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 1.1  | Build, configure and run graphs of Trigger, LLM Call, Router and Output nodes (journeys J1–J3)            | Accepted by the owner on 2026-10-07 |
| 1.2  | Activity view of every run                                                                                | Accepted by the owner on 2026-10-07; run mode's observation points cover live watching; the page awaits redesign |
| 2    | Labs (a workspace per objective with its graphs, runs and results); mem0 as a memory component to validate persistent memory; shared context, shared variables and memory as resources | Next sprint; journeys to validate before work starts |
| 3    | Tools and MCP servers assigned to nodes                                                                   | Candidate                              |
| 4    | Joins, conversation threads and queue components at node inputs                                           | Candidate                              |
| 5    | Batch experiments: task sets, repeated runs and comparison against objectives                             | Candidate                              |
| 6    | Improvement cycles: proposal and evaluation of variants                                                   | Candidate                              |
| 7    | API triggers and execution, users, subscription and usage billing                                         | Candidate                              |
| 8    | Isolated container execution with unchanged monitoring, one container per agent                           | Candidate                              |
| 9    | Standalone export without platform supervision                                                            | Candidate                              |

Every step keeps the engineering standards, mediated and recorded execution, and
the [container readiness rules](../adr/0023-container-ready-component-boundary.md).

## Ideas without a step yet

Recorded by the owner on 2026-10-05, for later planning:
- pre-warmed component hosts, so that a run does not wait for its hosts to start;
- memory that lasts across runs for the built-in Memory component (step 2 validates
  persistent memory with mem0 first);
- one container per agent, as part of step 8.

Revision 2 follows the [step 1 sprint report](step-1/sprint-report.md).
