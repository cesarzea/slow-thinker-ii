# S03 Live Execution Validation

| Document control | Value                                         |
| ---------------- | --------------------------------------------- |
| Report ID        | SPRINT-S03-LIVE-001                           |
| Owner            | Cesar Zea                                     |
| Date             | 2026-10-02, Europe/Lisbon                     |
| Status           | Completed; functional recording verified      |
| Scope            | One personal graph, one real OpenAI execution |

This supplements the [S03 status report](sprint-03-status-report.md). The earlier
shared verification and isolated demonstration used simulated model transport.
This additional execution was explicitly requested by the owner and used the
existing local runtime and authorized provider credential.

## Scenario and execution

The browser created, configured, validated and saved
`git-workshop-collaboration · v1`, derived from `bounded-review · example-1`.
The task was an offline Git onboarding workshop for six developers: exactly
90 minutes, seven prescribed agenda segments, three exercises, three pairs,
a prepared repository, named responsibilities and a final poll and competency
checklist. A deliberately incomplete first proposal exercised the feedback path;
this was a controlled example, not a naturally occurring initial model failure.

Both agents used the existing inexpensive `gpt-6-luna` OpenAI profile. The reviewer
retained its ordinary LLMCall worker and embedded deterministic Redirector.
The graph allowed at most six activations. Existing USD 3 run, session and monthly
caps, call/run deadlines and immutable tariff snapshots remained enforced.
The expired provider-review period was renewed before admission with a new local
configuration revision; historical execution configurations were retained.

| Observation        | Recorded result                                                     |
| ------------------ | ------------------------------------------------------------------- |
| Run                | `e2cf376c479f49679afdd4e06c4bb949`                                  |
| Outcome            | Completed; final proposal accepted; process cleanup confirmed       |
| Collaboration      | Three proposer/reviewer rounds; six activations                     |
| Reviewer routes    | `revise`, `revise`, `accept`                                        |
| Real model calls   | Six, with provider request IDs, native responses and verified usage |
| Mediated calls     | 25, including control, agent, model and routing calls               |
| Recorded cost      | USD 0.001177650; no outstanding reservation                         |
| Retained lifecycle | 39.558 seconds, including preparation and cleanup                   |

## Independent checks and findings

The retained definition exactly matches the saved personal JSON. Both revised
proposals received the previous proposal and the preceding review findings
unchanged, with bindings to the exact recorded source activations. All paid calls
completed normally. Independent decimal arithmetic reconciled their input, cache
write and output usage with the frozen tariff and the aggregate cost.

The final agenda has seven rows, the prescribed durations and continuous
09:00–10:30 times. Exercise placement, responsible roles, outputs, offline
preparation, pair arrangement, poll and competency checklist were also checked.
History displays the saved v1 graph and its three activations per agent.
The [sanitized evidence summary](../evidence/s03-live-execution-20261002.json)
records the outcome; complete native responses and task recordings remain local.

The second proposal already met the explicit requirements. Its reviewer response
misidentified the row containing the poll and checklist and demanded an explicit
three-minute checklist allocation, which the task did not require. This appears
to be an unnecessary rejection and caused a further round. The platform retained
that response without correcting or suppressing it.

This validates one real execution path and its recording. It does not establish
reviewer reliability, causal influence attribution or an improvement over a
single-agent baseline. No product code was changed and no additional paid run
was needed for the recording audit.
