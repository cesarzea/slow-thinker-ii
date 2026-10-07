# Working with personal experiments

Owner: Cesar Zea. Scope: S03. Status: implemented and verified locally.

Personal experiments use the same JSON graph format as the bundled examples.
Each saved definition is identified by its exact `graph_id` and `revision` and
stored in the local backend database. Saving never overwrites an existing revision.

## Open an experiment

Run the application with the explicit execution configuration described in the
[development guide](development.md#configure-model-execution). Connect operator
access and choose an experiment. The selector includes its revision; two revisions
can share a graph ID. Use **Refresh library** to begin a fresh listing and
**Load more experiments** when another page is available.

The canvas shows the selected saved graph. Its **Experiment definition** editor
loads domain JSON separately, preserving numeric values in the authoring text.
Definitions and credentials are not persisted in browser storage.

## Create and configure a revision

1. In **New revision or variant**, enter a new revision. Keep the graph ID for
   another revision of the same experiment, or change it to create a variant.
2. Select **Create draft from saved definition**. The backend copies the exact
   selected source and records its identity in `derived_from`.
3. Edit **Definition JSON** or use **Import UTF-8 JSON file**. The editor accepts
   at most 1 MiB of UTF-8 text; configured backend limits may be smaller.
4. Select **Validate definition**, then **Save definition**. Confirmation refreshes
   the library and selects the exact saved revision.

For LLMCall, agent settings are under `components.<agent>.config`: instructions,
input schema, generation parameters and output format. Resource bindings remain
under `components.<agent>.resources`; model profiles are approved backend settings.
Use the [LLMCall contract](contracts/llm-call.md) and
[graph examples](contracts/examples/README.md) for complete definitions.

An imported document must supply its own identity. Different content at an occupied
identity produces a conflict; identical canonical content confirms the existing
definition. Optional `derived_from` must reference a known saved parent. An unsaved
draft does not modify its parent, the canvas's saved definition or previous runs.

## Recover a rejected or uncertain save

Validation messages identify affected JSON paths. Definition validation checks
structure and declared contracts; execution checks input, installed contracts,
profiles, tariff availability, limits and budgets again.

If Save is unconfirmed, its effect may already have been stored. **Retry same save**
replays the frozen source to confirm the outcome. A failed library refresh after
confirmation retains the saved identity and offers selection recovery. Until that
selection changes, the editor returns to the originally selected saved source.
**Discard draft** returns to that source; it does not delete a saved revision.

## Run and inspect

Choose a saved work session, provide the graph's input and select **Start run**.
Start is unavailable while the definition is dirty or saved selection is unresolved.
The run uses the selected saved revision and freezes its admitted definition.
New revisions cannot change that snapshot or its recorded result.

Use session history to inspect retained execution, calls, content, results and
costs. Personal graphs retain the existing deadlines and run/session/month budgets.
Supported execution profiles remain Sequence and bounded conditional review.

See the [S03 delivery specification](specification/personal-experiments-sprint.md)
for acceptance status and the [library contract](contracts/personal-experiments.md)
for exact API, identity and validation semantics.
