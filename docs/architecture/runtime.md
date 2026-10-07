# Runtime scenarios

The scenarios follow journey J3, [funny story with review](../contracts/examples/funny-story-with-review.graph.json).

## Save a version

1. The editor sends the document to `POST /graphs/validate` while the user edits and
   shows the diagnostics on the affected nodes and dialog sections.
2. Save sends `POST /graphs/{id}/versions`. The application validates again, stores
   version *n* and returns its number. Nothing else changes.

## Start a run

```mermaid
sequenceDiagram
  participant UI as Interface
  participant App as Application
  participant Hosts as Host launcher
  participant Eng as Engine
  UI->>App: POST /runs (graph, version, input)
  App->>App: validate version, compile plan, record run.started
  App->>Hosts: launch Proposer, Reviewer and its Router (concurrently)
  Hosts-->>App: ready (record host.ready)
  App->>Eng: execute(plan, input)
  App-->>UI: 202 run_id
  Eng->>Eng: Trigger activation emits input on story.out
```

## Activation with an embedded Router

```mermaid
sequenceDiagram
  participant Eng as Engine
  participant Rev as Reviewer host (LLM Call)
  participant GW as LLM gateway
  participant Prov as DeepSeek adapter
  participant Rt as Router host
  Eng->>Rev: activate(message) with grant and time budget
  Rev->>GW: POST /v1/chat/completions (grant, model deepseek/deepseek-flash)
  GW->>GW: authorize grant, validate parameters, reserve run/day/month
  GW->>Prov: one bounded request
  Prov-->>GW: reply and usage
  GW->>GW: settle, record llm.called
  GW-->>Rev: Chat Completions reply
  Rev->>GW: platform.report (step)
  Rev-->>Eng: emissions [out: {"score": 5}]
  Eng->>Rt: select_output(received {"score": 5}, node_input story)
  Rt-->>Eng: port revise, payload story
  Eng->>Eng: deliver to proposer.in (record message.sent)
```

## Loop and completion

The `revise` delivery starts Proposer's second activation, whose output starts
Reviewer's second activation. When the Router selects `accepted`, the Output
activation records `run.result`. The queue is empty and nothing is running, so the
engine records `run.finished` with status `completed`, and the application stops the
hosts.

## Activation limit

If every review returns `revise`, the eleventh activation would exceed
`max_activations` = 10. The engine refuses to start it, cancels running
activations, records the pending delivery as dropped and finishes with status
`stopped` and reason `activation_limit`.

## Budget denial

If a reservation would exceed a budget, the gateway answers `402 budget_exhausted`,
asks the application to stop the run with that scope, and the LLM Call activation
fails. The run finishes `stopped` with `budget_run`, `budget_day` or `budget_month`.
