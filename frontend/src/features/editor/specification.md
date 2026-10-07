# features/editor: specification

The graph editor of journeys J1–J3 ([validated page](../../../../docs/specification/core-step-1-journeys/README.md)),
with the working copy and activated versions of
[ADR 0024](../../../../docs/adr/0024-working-copy-and-activated-versions.md).

## Behaviour

- **Document model.** A local, typed copy of the [graph document](../../../../docs/contracts/graph-document.md)
  with pure operations: add node from a declaration (`initial_config`, unique id and
  name), rename, delete (removing its connections), connect, disconnect, move, set
  configuration, add and remove an embedded component at its position (output or
  memory, one of each, the output's removal taking its connections), set limits. Effective
  ports follow the contract.
- **Autosave and versions.** Every edit is saved about 600 ms later as a change of the
  open branch (`POST /graphs/{id}/changes`); a graph created on the graphs page and not
  stored yet is stored by the first save (`POST /graphs`). Undo and Redo move through
  this session's states, and each is saved as a change. “Activate as v<n>” saves what
  is pending and activates the latest change; Run enters run mode, where Execute runs
  the branch's latest change. There is no
  Save button and no unsaved-changes guard; pending edits are saved when the editor
  closes.
- **Header.** Breadcrumb “Graphs / <name>”, the active version (“v<n> · Active”), the save
  status (“Saving…”, “Saved”, or the failure with “Try again”) with “<n> changes not in
  v<n>”; History (when the application renders it), Runs (when given its address),
  “Activate as v<n>” while the branch has changes not in the active version, and the
  mode switch “Edit” and “Run”.
- **Canvas.** React Flow with one handle per effective port, `isValidConnection`
  allowing only output-to-input, and a floating toolbar: Undo, Redo, Arrange, zoom out,
  the zoom level, zoom in, Fit and Outline. Cards show the kind tile and label, the node
  name, the `card` values (an LLM as a chip), with a memory a chip with its label and its
  own `card` values, and, with an output component, a band with its label and the
  outputs it provides. Left and right ports are listed in the card's
  ports row (the band's in the band), named beside handles on the card's edges; ports set
  to the top or bottom (`port_sides`) are spread evenly along that edge and named under or
  over their handles. Hovering or focusing a handle shows the port's full name and what
  it is connected to. A hovered or selected connection names its source port near its
  origin. Components are added by a click in the palette or dragged onto the
  canvas; components that only go inside a node (group “Inside a node”, such as
  Memory) are dragged onto a node or added to the selected node, and the status bar
  says why when neither applies.
- **Side panels.** The palette and the right panel collapse to rails with the same round
  control on their inner edge; a click anywhere on a rail opens it. The right panel's
  inner edge resizes it by dragging, up to covering the canvas; a double click switches
  between full width and 320 px. Collapsed states and the width are remembered in the
  browser.
- **Run mode.** Run keeps the same screen: the canvas shows the graph read-only, its
  toolbar changing only this view (Undo and Redo of that view, Arrange, zoom, Outline,
  connection style), with activation counts on cards and, at the middle of each
  connection, its observation dot with the number of messages it carried; a click
  observes it or stops observing it. The palette gives way to the observation points:
  Run, each node unfolding into what it records (Activity, Component calls, LLM calls,
  Reports, its output component, its memory, Results) with a checkbox that is mixed when
  only some are observed, and each connection; All and None. Choosing a point's name
  shows only its activity in the run panel. The choice is saved with the graph's
  `view.observe`. The right panel is the run panel the application renders through
  `renderRun(context)`. A run in the address (`runId`) opens run mode at that run, drawn
  from the document it executed with the working copy's layout; executing or leaving
  run mode reports the run through `onRunChange`.
- **Outline.** In place of the canvas: the nodes in flow order with their kind, problems
  and where their outputs lead; choosing one selects it.
- **Inspector.** For the selected node: its tile, editable name, component and a menu
  (Remove <component>, Delete node); configuration rows with a pencil to edit and a
  click to show the values, Expand all, Add component; where its ports sit (Left and
  right, Top and bottom, or Custom with a side per port); connections into and out of
  the node; its problems. Without a selection: the graph's name and its four run limits,
  committed on Enter or when a field loses focus.
- **History.** The History button shows the panel the application renders through
  `renderHistory(context)` in place of the inspector.
- **Node dialog.** One dialog per node, of a fixed size and place, with its sections
  grouped by component, each group headed by the component's tile and label; the
  embedded component's sections look like the host's. Apply validates the whole
  document through the API; Cancel discards; Remove <component>, shown while that
  component's section is open, lists the connections that will be removed (none for a
  memory). The inspector's menu offers one Remove <component> per embedded component.
- **Status bar.** Whether the graph is checked and its problems (a list that selects
  their node), the node and connection counts, and “Saved <time> · change <n>”; a notice such as “Deleted <node> · Undo” with button “Undo: Deleted <node>”.

## Acceptance

Unit tests cover every document operation, effective ports, connection validity,
embedding and removal at both positions, autosave, undo and redo, activation, run mode
and its observation points, the side panels, the history slot, diagnostics display and
dialogs. Browser journeys J1–J3 and the memory journey run against the real backend.

## Accessible names

Browser journeys locate controls by role and accessible name; these names are part
of the specification.

| Element                  | Role and name                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Palette                  | navigation “Components” with searchbox “Search components”, regions “Platform” and “Installed”; button “Add <label>” per component, which can also be dragged onto the canvas                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Node card                | group named by the node name                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Port handle              | button “<node name> input <port>” or “<node name> output <port>”; while hovered or focused, a tooltip with the port's name and “To …”, “From …” or “Not connected”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Port sides               | region “Ports” in the inspector with combobox “Port sides” (“Left and right”, “Top and bottom”, “Custom”); with Custom, a combobox per port named “Input <port>”, “Output <port>” or “Input and output <port>”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Header                   | heading (level 1) with the graph name; status with the save state; buttons “History”, “Activate as v<n>”; group “Mode” with buttons “Edit” and “Run”; link “Runs”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Canvas tools             | buttons “Undo”, “Redo”, “Arrange the graph” (shown as “Arrange”, fits the screen), “Arrange options” opening menu items grouped under “ELK with ports” (“Arrange: Fit to screen”, “Arrange: Compact”, “Arrange: ELK with ports (by flow)”), “ELK tree” (“Arrange: ELK tree, left to right”, “… top to bottom”) and “Dagre tree” (“Arrange: Dagre tree, left to right”, shown with “(horizontal flow)”, and “… top to bottom”), “Zoom out”, “Zoom in”, “Fit to screen”, toggle “Outline”, “Connection style” opening menu item radios “Curved connections”, “Simple curve connections” and “Connections routed around boxes” and, for curved connections, slider “Curvature”; Undo and Redo show their text and their shortcut as tooltip |
| Outline                  | list “Outline”, a button per node; list “Connections from <node>”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Inspector                | complementary “Selected node” with a heading named by the node and textbox “Node name”, or complementary “Graph” with textbox “Graph name” and the limits below                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Node menu                | button “Delete node” and button “More actions for <node>” with menu items “Remove <label>” and “Delete node”; on the canvas, button “Delete <node>” on a selected card and menu “Actions for <node>” (right click) with “Edit configuration”, “Delete” and “Remove <label>”; in the Outline, button “Delete <node>” per entry                                                                                                                                                                                                                                                                                                                                                                                                            |
| Configuration row        | region named by the section title; button named by the title to show the values, described by its one-line value; button “Edit <section title>”; button “Expand all” or “Collapse all”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Connections in inspector | list “Incoming connections” with buttons “Remove connection from <node> · <port>”; list “Outgoing connections” with “Remove connection to <node> · <port>”; combobox “Connect <port> to” per output                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Connection on the canvas | image “Connection from <node> · <port> to <node> · <port>”; once selected, button “Remove connection from <node> · <port> to <node> · <port>”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Node dialog              | dialog named by the node name; vertical tablist “Sections” with tabs named by section titles; buttons “Remove <label>”, “Cancel” and “Apply”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Add component            | button “Add component”, then a dialog “Add component” listing buttons named by component labels                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Run limits               | spinbuttons “Maximum activations”, “Maximum running nodes”, “Time limit (s)” and textbox “Budget per run ($)” in the Graph inspector                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Status bar               | “No problems”, or button “<n> problems” opening the list “Problems”; “Saved <time> · change <n>”; a notice such as “Deleted <node> · Undo” with button “Undo: Deleted <node>”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Side panels              | buttons “Hide components” or “Show components”, “Hide panel” or “Show panel”; complementary “Panel” for the collapsed right rail; separator “Resize the panel”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Run mode                 | navigation “Observation points” with buttons “All”, “None”, checkboxes “Observe <point>”, buttons “Show what <node> records” or “Hide what <node> records”, list “What <node> records”; observation dots “Observe <from> · <port> to <to> · <port>” (pressed while observed); group “Canvas tools”                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Palette, inside a node   | region “Inside a node” with buttons “Add <component>”                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

Interaction details relied on by the journeys: adding a node selects it; the node name
field commits on Enter or when it loses focus; comboboxes are native `select`
elements; a newly created graph shows the empty canvas with the palette.

## Public interface (`features/editor/index.ts`)

- `Editor({client, graphId, created, onDraft?, runsHref?, graphsHref?, renderHistory?,
renderRun?, runId?, onRunChange?})` opens the latest change of branch `main`, or, for a
  graph not stored yet, the document `created` on the graphs page. `onDraft` receives a `DraftModel` that is
  dirty only after a failed save. `runsHref` and `graphsHref` link the header to the
  graph's runs and to the graphs page.
- `HistoryContext {graphId, branch, latestChange, activeVersion, onRestore(document),
onBranchChange(name), onActivated(version), onClose()}`, given to `renderHistory`. The
  panel stays open across branches.
- `RenderRun`, given a `RunPanelContext {graphId, graphName, runId, message, ask, limits,
blocked, prepare(), onStarted(runId), onReset(), points, focus, onClearFocus(), labels,
onCounts(counts), onClose()}`: everything the run panel needs from run mode.
- `GraphPreview({document, catalog, activations?, messages?, arrangeable?, observation?})`:
  the read-only canvas; without counts it shows no badges or labels; `arrangeable` adds
  the editor's toolbar and draggable cards for this view only; `observation` draws the
  connections' observation dots.
- `newGraphDocument(id, name)`: the local document of a new graph with default limits.

## Implementation decisions

- Node identifiers derive from the component type (`llm-call`, `llm-call-2`, …) and do
  not change on rename; names start from the label and are unique ignoring case. A new
  node goes to the first cell of a four-column grid (steps of 270px and 240px) that
  keeps at least 24px between its 220px card and every other card, including cards moved
  by hand; cards are taken as at most 200px tall. A dropped component is centred under
  the pointer. The view frames all nodes whenever nodes are added or removed.
- The editor fills the window below the application header (at least 560px) in fixed
  grid rows: the 52px header, the body and the 28px status bar. The canvas height does
  not depend on the inspector's content; the palette and the inspector scroll on their
  own. Below 960px wide the parts stack.
- One save runs at a time and the latest document wins; a failed save keeps the edit for
  “Try again”. An unchanged document answers 200 and adds no change. “<n> changes not in
  v<n>” counts the branch's changes after the active version's change (from the latest
  100), plus each new change saved since.
- Undo and Redo work along the branch's history: this session's edits (the last 100),
  then the branch's earlier changes (the latest 100, read when reached), so they are
  available after a reload. Each step is saved as a new change; any other edit clears
  the redo path. The status bar shows “Undone: …” or “Redone: …” for a few seconds,
  described like the History panel (`describeChange`). Ctrl or ⌘ with Z undoes, with
  Shift and Z or with Y redoes, except in fields and dialogs.
- A node is deleted, with its connections, as one change: with Delete or Backspace while
  it is selected (never while typing or in a dialog), the trash button at a selected
  card's top right corner, the card's right-click menu, the inspector's trash button or
  ⋮ menu, or the trash button of its Outline entry. There is no confirmation: the status
  bar shows “Deleted <name> · Undo” for a few seconds. Selecting a connection clears the
  node selection, so Delete acts on one of them.
- Apply in a node dialog validates the document before and after the dialog's changes
  and stays open only for errors on that node that the changes introduce, so graphs can
  be built step by step.
- Embedding a component removes connections from the node's replaced outputs (the Add
  component dialog says so). Connections that leave outputs a node no longer has are
  listed in the inspector with Remove. Outgoing connections follow the node's output
  order.
- Configuration rows start collapsed for each selected node; Expand all opens them all.
  A row's one-line value joins its fields' short values: an LLM by its label, a schema by
  its number of properties.
- A port's side comes from `port_sides`; the document lists only ports that are not on
  their default side, keeps no entry for a node at the default and none for deleted
  nodes or ports. Cards stay 220px wide; long port names are shortened with an ellipsis.
  Custom writes every port's side.
- All connections of a canvas are routed together (`canvas/routing/`): around the cards
  with `@tisoap/react-flow-smart-edge` (orthogonal with rounded corners, leaving and
  reaching each handle along its side), slanted pieces squared, pieces that would run on
  top of another route moved 8–24px aside, recomputed whenever a card or handle moves.
  When no route is found, a connection goes straight out of both handles and across
  halfway. Connections are drawn as the graph's `view` says: React Flow's curves with
  its `curvature` (0.25 unless set), React Flow's simple curves (`simple`), or routes around
  the boxes, in the editor, the run
  view and previews alike, each version with its own view. The “Connections” menu
  changes it as an ordinary, undoable change; its Curvature slider (0 to 1, steps of
  0.05, shown for curved connections) previews while it moves and saves one change when
  released. Lines are 1px in React Flow's grey and 1.5px in the accent colour while
  hovered or selected.
- While a connection is hovered or selected, its source port's name is shown beside the
  line leaving the source, on the side away from other routes and clear of every card,
  handle, line and message count where possible; it is shortened when it does not fit.
- A connection has a closed arrowhead at the target, of a fixed size; a click selects it, and its × button,
  Delete or Backspace remove it (never while focus is in a field or a dialog); Escape or
  a click on the empty canvas clears the selection.
- Arrange uses ELK's `layered` algorithm (`state/elk-graph.ts`), loaded on first use: its
  API as a lazy chunk and its engine as a web worker. Each card keeps its measured size,
  with its ports fixed on their sides where it draws them; Triggers take the first layer
  and loops are broken depth first from them. By flow keeps one row of layers; to fit the
  screen wraps the layers to the canvas's width ÷ height, 56px apart so that routes pass
  between cards; compactly wraps them with tighter spacing. Arrange never changes port
  sides. React Flow's layout examples are offered too: ELK's tree (`layered`, right or down,
  cards node to node without ports, 100px between layers and 80px between cards) and
  dagre's tree (`rankdir` LR or TB, `nodesep` 40, `ranksep` 80, measured card sizes;
  dagre loads on first use as its own chunk). React Flow's horizontal flow example is the
  dagre tree from left to right, so it has no entry of its own. The positions are saved as
  one change, then the view is framed at most at
  100%. Without ELK, the editor's own layered layout (`state/arrange*.ts`) is used.
