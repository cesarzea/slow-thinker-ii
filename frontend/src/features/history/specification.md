# features/history: specification

The runs list, routes `#/runs` (every graph) and `#/graphs/<id>/runs` (one graph).

- Reads `GET /runs?graph_id=&limit=100` (without `graph_id` for every graph), newest
  first, and `GET /graphs` once for the graph names and the Graph filter.
- Heading “Runs”, or “Runs of <graph name>” for one graph; the graph id stands for a
  name that is not known.
- A table of the runs, newest first: Run (“<graph name> · Run <n>”, linked to the run,
  which opens its graph's editor in run mode), Version (`v3`, or `change 151` for a
  change never activated), Status (`runStatusText`), Started (local date and time),
  Duration, LLM calls and Cost. Duration comes from the totals,
  otherwise from the start and end, otherwise “—”; LLM calls and Cost come from the
  totals, “—” without them.
- n is the run's position among the runs of its graph in the fetched list, oldest
  first. In the list of every graph it
  counts only that graph's runs among the newest 100, so a graph with older runs
  outside that page shows lower numbers than its run view.
- The Graph select offers “All graphs” and every graph by name, alphabetically; a graph
  of the route that is not listed is added under its id. Choosing reports the graph, or
  `null` for all graphs; the application navigates.
- Empty states: “No runs yet. Open a graph and choose Run to start one.” and, for one
  graph, “This graph has no runs yet. Open it and choose Run to start one.”
- Polls every 5 seconds while any listed run is starting or running, and stops when all
  have finished. A failed read keeps the runs shown, reports “Could not load the runs.
  <message>” with “Try again”, and polling continues while the last runs read include
  an active one.

Acceptance: unit tests for run numbering, row formatting, the table, the Graph filter,
empty states, polling and a failed read.

## Accessible names

| Element | Role and name                                                                                                                                             |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Page    | heading “Runs” or “Runs of <graph name>”, level 1; combobox “Graph” with options “All graphs” and the graph names                                         |
| Table   | table “Runs”; column headers “Run”, “Version”, “Status”, “Started”, “Duration”, “LLM calls”, “Cost”; each row header is the link “<graph name> · Run <n>” |
| States  | text “Loading the runs…”, the empty-state texts, and alert “Could not load the runs. <message>” with button “Try again”                                   |

## Public interface (`features/history/index.ts`)

`RunsPage({client, graphId, runHref, onGraphChange})`: `graphId` is the listed graph
or `null` for every graph; `runHref` is `(graphId, runId) => string`; `onGraphChange(graphId | null)` reports the Graph filter.
When `graphId` changes, the run list starts afresh while the heading and the Graph
filter stay mounted, so the filter keeps the focus.

## Implementation decisions

- The page uses the application's shared page classes (`page`, `page-header`,
  `table-frame`, `data-table`, `status-pill`, `empty-state`, `page-failure`); the status
  shows as a coloured dot and the status text.

- The run duration repeats the few lines of `features/runs` `runDuration`, since
  features do not import each other.
- Started uses the English medium date and time style in the browser's time zone.
