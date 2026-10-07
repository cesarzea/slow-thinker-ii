# features/activity: specification

The S06 part two activity view of a run, and the live feed of the observed points that run
mode shows in its panel.

- Reads `GET /runs/<id>/events` in pages until `finished`, polling while the run is
  active.
- Timeline rows in sequence order: time, node, kind label (message, activation, LLM
  call, router, report, result, end) and summary; tokens, cost and duration aligned on
  the right. LLM call rows expand to the request (system and user messages,
  parameters), the reply, usage, reserved amount, cost and rates. Router rows expand
  to the call's arguments and result. Reports are labelled “Reported by <component>”.
- Filters: All, Messages, Calls.
- Side summary: status, duration, activations, messages, LLM calls, tokens in and
  out, cost, budget used, and a per-node table of activations and cost.
- Payloads render as text or structured JSON, never as HTML; reuse `EvidenceContent`
  and `useRead` from `archive/s06-c11-wip` `features/inspector/`.

Acceptance: unit tests render a recorded J3 event log fixture and check order,
expansion, filters, totals and the reported-evidence label.

## Accessible names

| Element  | Role and name                                                     |
| -------- | ----------------------------------------------------------------- |
| Page     | heading “Activity”                                                |
| Filters  | radio group “Show” with “All”, “Messages”, “Calls”                |
| Timeline | list “Timeline”; each row a button that expands its detail region |
| Totals   | region “Totals”; table “Activations by node”                      |

## Public interface (`features/activity/index.ts`)

- `ActivityPage({client, graphId, runId, runHref})`, with the link “Back to the run”; it
  is reachable by the run's address followed by `/activity` while it waits for its
  redesign.
- `ObservationFeed({client, runId, points, focus, labels, onClearFocus})`: the run's
  events recorded at `points` (see `eventPoint` in `api`), as they arrive, newest last.
  Each item names its point, kind and time to the millisecond (`0.800 s`), shows what it
  carried (a message's payload, a model's reply or error, a result, a report, or a
  call's result, or its arguments when it returned nothing) and its recorded detail on
  demand. With a `focus` the title is “Activity of <point>” with a button “All observed”,
  otherwise “Observed”. A choice “Content” (the default) or “All events” leaves out, or
  shows, the lifecycle events (`host.ready`, `run.running`, `activation.started`,
  `activation.completed`, `activation.cancelled`); it is remembered in the browser.

## Implementation decisions

- Kind labels: `run.started`, `run.running` and `host.*` → “start”; `message.*` →
  “message”; `activation.*` → “activation”; `llm.called` → “LLM call”; `component.called`
  at the output position → the component's label in lower case (“router”), at the node
  position → “call”; `report` → “report”; `run.result` → “result”; `run.finished` → “end”.
- Messages lists `message.*` rows; Calls lists `llm.called` and `component.called` rows.
- A report is attributed to the component of the next `component.called` event of the
  same activation, or else to the node's host component.
- Names come from the document the run executed, its version or its change, and from
  the catalog; until they load,
  identifiers are shown.
- Totals come from `run.finished` when present, otherwise from the events read so far;
  budget used compares the cost with the run budget recorded in `run.started`.
- The Totals status is the run's status line (`runStatusText`), as in the run view.
- The run-end row reads “Completed: no message pending and no node running” for a
  completed run; otherwise the status line, followed by “. <detail>” when the detail is
  not empty, for example “Stopped: activation limit reached. The run reached its limit of
  3 activations before Proposer could start.”
