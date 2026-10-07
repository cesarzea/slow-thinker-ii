# app: specification

Routing, access, connection and the product shell.

## Routes

`#/graphs` (list), `#/graphs/new`, `#/graphs/<id>` (editor), `#/graphs/<id>/runs` (runs
of one graph), `#/graphs/<id>/runs/<run>` (the editor in run mode, showing that run),
`#/graphs/<id>/runs/<run>/activity`,
`#/runs` (runs of every graph) and `#/components` (components page). Unknown routes,
including trailing slashes and extra segments, go to `#/graphs`.

The main navigation has three sections: Graphs for the graph list, New graph and the
editor; Runs for both run lists, a run and its activity; Components for the components
page.

## Behaviour

- Port from `archive/s06-c11-wip` `frontend/src/app/`: `routes.ts` (new route set),
  `use-connection.ts`, `access-panel.tsx` and `access-entry.tsx` without the public
  viewer, `use-workspace-route.ts` and `draft-guard.tsx` against a minimal
  `DraftModel { dirty: boolean; save(): Promise<'saved' | 'failed'>; discard(): void }`.
- The shell's top bar, after the approved redesign: the brand mark “ST” and the product
  name, the main navigation as pills with the current section marked
  `aria-current="page"`, the compact spending with the used amounts in bold, and the
  disconnect action. Leaving an editor with unsaved changes, through any link, Back or
  a typed hash, asks to save, discard or stay.
- The banner shows each used amount with exactly three decimals, rounded half up with
  exact decimal arithmetic on the API's decimal string (“0.0835” shows “$0.084”); a
  nonzero amount that rounds to zero shows “<$0.001”. Limits keep `moneyLabel`, so
  configured limits such as `1.00` or `20` show “$1.00” and “$20.00”. Text that is not a
  non-negative decimal is shown as received.
- `main.tsx` imports `@xyflow/react/dist/style.css`.
- `styles/base.css` holds the redesign's design tokens (`--bg`, `--surface`,
  `--surface-2`, `--surface-3`, `--line`, `--line-strong`, `--text`, `--muted`,
  `--subtle`, `--accent` and its variants, `--danger`, `--success`, `--warning`, the
  component colours, `--radius`, `--radius-lg`, `--shadow`, `--shadow-float`,
  `--font-body`, `--font-mono`), base element styles in the mockup's 13px system type,
  and earlier token names as aliases while every feature moves to the new ones.
  `styles/pages.css` holds the list pages' shared classes: `page`, `page-header`,
  `table-frame`, `data-table`, `status-pill`, `version-pill`, `empty-state`,
  `page-failure`.

## Composition

- On start the interface reads `GET /access` without a token and shows “Connecting…”
  meanwhile. With `"none"` it connects at once, sends no Authorization header and
  hides Disconnect. With `"token"`, or when the read fails, it reconnects with the
  operator token kept for this tab or shows the access entry.
- Connect keeps the token in `sessionStorage` (key `slow-thinker-ii.operator-token`),
  so a reload reconnects without asking and closing the tab forgets it. Disconnect and
  any 401 or 403 remove it. Every storage access is guarded; when storage is
  unavailable the token lives only in page memory and a reload asks again.
- A 401 or 403 from any request returns to the access entry with “The operator token is
  no longer accepted. Connect again to continue.”, or, on a connection without operator
  authentication, “This server now asks for the operator token. Connect to continue.”
- Features are composed here, since they never import each other: the graphs page's
  New graph creates the editor's `newGraphDocument` on the server (`POST /graphs`) and
  opens the editor on branch `main`, which gets no unstored document; the editor's
  `renderRun` draws the runs feature's `RunPanel` with the activity feature's
  `ObservationFeed` as its feed; the editor's `runId` comes from the run route and its
  `onRunChange` moves between the editor's and the run's routes, which are the same
  editor, so the guard never asks between them; the editor's `renderHistory`
  draws `features/versions` `HistoryPanel`, whose read-only canvas is the editor's
  `GraphPreview` without counts; the editor also gets `graphsHref` and `runsHref`.
- The runs list is `features/history` `RunsPage`: the application builds its run and
  activity links from the routes, and its Graph filter navigates between `#/runs` and
  `#/graphs/<id>/runs`. The editor receives `runsHref`, the hash of its graph's runs.
- The components page is `features/catalog` `ComponentsPage`.
- The editor registers its `DraftModel` after every render; the guard reads it when the
  route leaves the editor (links, Back, typed hashes) or on Disconnect. Edits are saved
  as they are made, so the guard asks only when the last save failed.
- Usage is read on connection and every 30 seconds; “Spending unavailable” when it
  cannot be read.

## Acceptance

Unit tests cover route parsing and building, navigation sections, the banner amounts,
guarded navigation, the access modes, the token kept for the tab, access entry and
credential invalidation.

## Accessible names

Start: text “Connecting…”. Access entry: textbox “Operator token”, button “Connect”, and
the note “Use the operator token configured on this server. It is kept in this tab until
you disconnect or close it.” Shell: banner with navigation
“Main” holding the links “Graphs”, “Runs” and “Components”, the current one with
`aria-current="page"`; text “Today $<used> of $<limit>” and “This month $<used> of
$<limit>”, for example “Today $0.000 of $1.00” or “Today <$0.001 of $1.00”; button
“Disconnect”, absent without operator authentication. Unsaved-changes guard: dialog “Unsaved changes” with buttons “Save”,
“Discard” and “Stay”.

The token field is a password input labelled “Operator token”; browsers and Playwright
expose it as a text box, while jsdom-based tests find it by its label.
