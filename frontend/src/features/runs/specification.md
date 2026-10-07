# features/runs: specification

Run mode's panel, shown by the editor on the right of the same screen (see
[ADR 0025](../../../../docs/adr/0025-runs-of-changes-and-run-mode.md)).

- **Before Execute.** When the Trigger asks for the message on manual runs (its
  `manual_runs` is `ask`, the default), the message is editable for this run only;
  otherwise the panel shows the Trigger's message it will send. The graph's limits
  follow. Execute saves pending edits through the editor and starts the branch's latest
  change; a graph with errors or not yet saved cannot be executed, and says why.
  Refusals such as `too_many_runs` are shown in the panel.
- **During and after the run.** Polls `GET /runs/<id>` every second until the run ends:
  status with reason and detail, duration, activations, LLM calls, cost and budget used,
  Stop while running, Run again once it has ended, the observed points' events supplied
  by the application, and what the run executed (`version 3` or `change 151`). It
  reports the activation and message counts to the editor, which draws them on the
  canvas.
- Back to editing closes run mode, from the panel's header or its footer.

Acceptance: tests of executing with and without asking for the message, a run that does
not start, Stop, Run again, and the counts and status of a finished run.

## Accessible names

| Element | Role and name                                                                                                           |
| ------- | ----------------------------------------------------------------------------------------------------------------------- |
| Panel   | complementary “Run”; textbox “Message” when the Trigger asks; buttons “Execute”, “Stop”, “Run again”, “Back to editing” |
| Status  | status text “Completed”, “Stopped: <reason>”, “Failed: <reason>”, “Cancelled”, “Running”, with the detail below         |

## Public interface (`features/runs/index.ts`)

- `RunPanel({client, graphId, graphName, runId, message, ask, limits, blocked, prepare,
onStarted, onReset, onCounts, onClose, feed})`: `runId` is null before Execute;
  `prepare` saves and names what Execute runs; `feed(runId)` renders the observed
  events, which the application takes from the activity feature since features do not
  import each other.

## Implementation decisions

- The status line (`role="status"`) names the reason with these labels: activation limit
  reached, time limit reached, run budget exhausted, daily budget exhausted, monthly
  budget exhausted, a component could not start, an activation failed, interrupted by a
  server restart, internal error. A starting run shows “Starting”.
- Figures come from the run's totals; while a run is active, activations are summed from
  `activations_by_node` and the other figures show “—”. Budget used is the cost against
  the graph's `budget_usd`.
