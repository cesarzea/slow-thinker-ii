# Experiment workspace

Slow Thinker II provides a local workspace for configuring, running and inspecting
collaboration experiments. Connect operator access to use the saved experiment
library. The current [composition and dialog correction](specification/s06-composition-and-dialogs.md)
is in verification; earlier whole-interface checks do not establish this scope's
completion. Owner usability acceptance remains pending. The versioned sprint report and
verification record retain evidence and limits.
Credentials and provider endpoints belong to trusted backend settings;
they never belong in graph JSON.

## Configure an experiment

**Experiments** is the complete searchable collection. Open an experiment to enter
its **Design**, **Resources**, **Versions**, **Runs** and **Experiment settings**
sections. **All experiments** returns to the collection. **Component library**
and **Workspace settings** have global scope.

Configuration dialogs keep local edits until **Apply** stages them in the shared
working draft. **Cancel**, Close and Escape discard that dialog's edits. **Save
revision** validates the draft and saves a fresh immutable revision when editing
an existing one. Invalid text stays visible for repair. Leaving a changed experiment
offers Save, Discard or Cancel. An unconfirmed save retries the same frozen source.

In **Design**, select a graph agent to open its adjacent read-only summary.
Each concept has an **Edit** action opening its own dialog. A composed agent presents
its functional worker's declared settings once, with a breadcrumb identifying the
configured element. Components own these concepts, fields and summaries; the platform
interprets their declarations. External components without presentation metadata
receive a generic schema-based configuration dialog and optional expert source.
Resource controls identify shared consumers. Bindings select dependencies;
**Permissions** explicitly authorizes their operations. Expand the icon inside
Prompt to expand its editor inside the same dialog.
**Add component** selects a compatible installed extension and previews its input,
output, routes and grants before staging the change. **Replace** and **Remove**
preserve current worker edits and list affected connections. Old manually composed
instances without a reversible journal remain configurable; structural changes
require the recorded provenance rather than guessed restoration. Declared resource
bindings offer compatible connections;
there is no universal tool, memory or routing category imposed on every agent.

Select a connection to map task inputs or completed responses, set
fixed inputs, reorder sequences and configure conditional routes. **Finish** ends
a route. Optional feedback omits a value when no completed response exists. Choose
the final result's source node and response field. Suggested paths help with
registered outputs; custom paths remain available for extension payloads.

Use **Experiment settings** to define the information a run requires. The schema builder
supports fields, types, required fields, nested objects, arrays and common
constraints. If a definition has no explicit input schema, select its type before
adding fields. Include every input needed by the graph's mappings.

**Component library** is the installed type/version inventory; it is distinct from
instances in an experiment. The graph toolbar offers guided **Add agent**, **Add
resource** and **Delete** commands. Deletion lists affected references and repairs
known dependencies only after confirmation. **Edit definition** opens exact JSON
and validation in a focused dialog sharing the same working draft. The toolbar's
**Graph list** provides structural selection without using the canvas. Neither
view is appended below the graph. Collection actions support file import and creation
from templates. Unsupported authored constructs retain generic fields and optional
expert source. Bundled ordinary configuration does not require JSON. Ordinary forms
preserve unrelated source, including numbers above JavaScript's exact integer range.
Finite sequences and bounded conditional flow are supported; full graphical
authoring is a later milestone.

## Models, tools and memory

**Resources** shows the selected experiment's resources and reviewed model
profiles. `model-provider` selects OpenAI or DeepSeek independently for each bound
agent. Supported reasoning modes are discovered from that profile. Tariff status
is separate from definition validity: an unavailable, stale or expired profile
can prevent admission even when the graph itself validates.

The calculator accepts bounded decimal arithmetic. Key/value memory supports
version-checked updates and configurable run-local or persistent retention. Bind
the same memory instance to share state, or separate instances for isolation.
`ContextualCall` can read memory, calculate, invoke a managed worker and save its
result; each stage passes through platform permissions, deadlines and observation.

The **bounded-review** template demonstrates composition: its Reviewer is a
`RoutedCall` with an internal `LLMCall` worker and `Redirector`. Expand **Components**
to inspect or configure both. The Redirector declares `accept` and `revise` output
names and references an installed deterministic routing function. Acceptance ends
the run; revision returns feedback to the Proposer. The **repeated-review** template
instead follows a fixed sequence; its repeated steps do not imply internal routing.

The optional **Show resources** canvas layer renders bound non-model instances once
and connects only their configured consumers with dashed lines at plain card borders.
Model configuration stays in agent settings. Bindings are configuration evidence,
not proof that a resource was called during a run.

The Collaboration toolbar separates editing actions, pressed visibility buttons
and layout controls. Input/output arrows and feedback routes stay visible;
**Arrange** resets the layout and fits its contents. Later execution updates preserve
dragged positions and the user's viewport. The compact resource strip below the
canvas identifies the actual configured consumers of each displayed resource.

The [resource collaboration example](contracts/examples/resource-collaboration.graph.json)
uses two independently packaged workers, OpenAI and DeepSeek, a calculator and
shared persistent memory. Its [input](contracts/examples/resource-collaboration.input.json)
asks for a workshop plan. Prepare its registered packages and reviewed profiles
before importing it; it is not one of the five bundled starter experiments.

## Execute and inspect

**Versions** lists immutable saved history and lineage. Compare two exact revisions
to inspect definition changes, including exact numeric values. **Create draft from
this version** derives a new working revision; it never overwrites history. This
comparison does not evaluate answer quality or run performance.

In **Runs**, experiment history includes all sessions, with an optional exact
revision filter. Select an old run to inspect its admitted definition. Choose a
saved work session or expand **New session** for a new run. Expand
**New run** when reviewing a completed run, supply input matching the selected
graph and start execution. Dirty drafts, pending edits and unavailable configuration
prevent Start. Selecting another revision does not replace a previously recorded
run's definition, graph, result or call evidence.

Completed runs show readable results, with separate sections for named node
outputs and **Original response · JSON** for exact content. Runtime text is
rendered as text, never executable HTML. The new-run setup is collapsed while
reviewing a terminal result.

**Run activity** places the admitted graph and selected evidence before history.
Its toolbar offers recorded activity separately from the structural **Graph list**.
Raw event records and exact payloads are deliberate details. A recognized accepted
review result presents its answer first, with status, activation count and
inspectable provenance; unknown result shapes retain their original content.

The canvas presents agents and their transitions. Configuration and system
markers are optional. Select an activation or call to inspect its exact recorded
inputs, outputs, nested calls, provider evidence and cost. Only reasoning actually
returned by a provider is recorded; it is not a complete account of internal thought.

## Limits and recovery

**Workspace settings** configures call/run deadlines and run/session/month budgets within
the backend's ceilings. Changes cannot reduce a budget below its current committed
spending. Saved settings survive restart. Historical charges retain their original
tariff evidence; daily price refreshes do not recalculate them.

If a save or settings response is uncertain, retry the same command. If another
configuration revision has intervened, refresh and review the latest values before
submitting another change. Voluntary disconnect uses the unsaved-change guard;
forced loss of operator access clears protected state immediately. Reconnect
with the existing operator credential to continue; it is not saved by the browser.
The account and credit footer is explicitly an illustrative preview. Its static
figures are unrelated to real USD limits, reservations and recorded spending.

The [delivery contract](contracts/product-workspace.md) and
[verification record](verification.md) describe the current guarantees and limits.
