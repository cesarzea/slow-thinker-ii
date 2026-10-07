# features/graphs: specification

Graph list and creation.

- Lists graphs, most recently changed first, as a table: name (linked to the editor),
  active version (“v<n>” or “None”), branches (from `GET /graphs/{id}/branches`, one read
  per graph, “—” until read), last change (“Change <n> · <date and time>”) and last run
  (its status text, linked to the run view, from `GET /runs?limit=100`; “No runs” when
  none is listed). An empty state explains how to create the first graph.
- New graph asks for a name and reports `onCreate({id, name})`; the application creates
  the graph on the server at once (branch `main`, change 1) and opens the editor. A
  refusal stays in the dialog as “The graph could not be created. <message>”. The graph
  id is the name's slug plus four random hexadecimal characters.
- The page uses the application's shared page classes (`page`, `page-header`,
  `table-frame`, `data-table`, `status-pill`, `version-pill`, `empty-state`).

Acceptance: unit tests for the table, the empty state, a failed read, creation with its
refusal and slug generation.

Accessible names: heading “Graphs”; button “New graph”; dialog “New graph” with
textbox “Name” and button “Create”; table “Graphs” with columns “Graph”, “Active
version”, “Branches”, “Last change”, “Last run”, each row header a link named by the graph
and the last run a link named by its status.

## Public interface (`features/graphs/index.ts`)

`GraphsPage({client, creating, graphHref, runHref, onNew, onCancelNew, onCreate})`. The
page shows the New graph dialog while `creating` (route `#/graphs/new`); `onCreate`
returns a promise whose rejection the dialog shows. The slug is lowercase ASCII letters
and digits joined by hyphens, prefixed with `graph` when it would not start with a
letter, and at most 59 characters before the suffix; the suffix comes from
`crypto.getRandomValues`. Names are trimmed and must have 1–120 characters.
