# Experiment workspace

Slow Thinker II provides a local workspace for configuring, running and inspecting
collaboration experiments. Connect operator access to use the saved experiment
library. Credentials and provider endpoints belong to trusted backend settings;
they never belong in graph JSON.

## Configure an experiment

Select a saved experiment in **Experiments**. Create a draft with a new revision,
or change the graph ID to create a variant. **Structured forms** and **JSON source**
edit the same definition. Applying a form updates the unsaved source; validate and
save it before execution. Saved revisions are immutable.

**Components** lists instances and their registered schemas. Configure prompts,
input/output schemas, supported model parameters, managed children and resource
bindings. A binding identifies a dependency; it does not grant permission to call
it. Grant each required operation in the graph permissions.

Graph forms configure declared nodes, input bindings, sequence order, conditional
routes, activation limits and the final result binding. The supported initial
profiles are finite sequence and bounded conditional flow. Raw JSON remains
available for opaque configuration and extension fields. Form edits preserve
unrelated fields and JSON numbers, including integers above JavaScript's exact range.

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

The [resource collaboration example](contracts/examples/resource-collaboration.graph.json)
uses two independently packaged workers, OpenAI and DeepSeek, a calculator and
shared persistent memory. Its [input](contracts/examples/resource-collaboration.input.json)
asks for a workshop plan. Prepare its registered packages and reviewed profiles
before importing it; it is not one of the five bundled starter experiments.

## Execute and inspect

In **Runs**, choose a saved work session, supply input matching the selected graph
and start execution. Dirty drafts, pending edits and unavailable configuration
prevent Start. Selecting another revision does not replace a previously recorded
run's definition, graph, result or call evidence.

The canvas presents agents and their transitions. Configuration and system
markers are optional. Select an activation or call to inspect its exact recorded
inputs, outputs, nested calls, provider evidence and cost. Only reasoning actually
returned by a provider is recorded; it is not a complete account of internal thought.

## Limits and recovery

**Settings** configures call/run deadlines and run/session/month budgets within
the backend's ceilings. Changes cannot reduce a budget below its current committed
spending. Saved settings survive restart. Historical charges retain their original
tariff evidence; daily price refreshes do not recalculate them.

If a save or settings response is uncertain, retry the same command. If another
configuration revision has intervened, refresh and review the latest values before
submitting another change. Disconnecting clears unsaved operator work. Reconnect
with the existing operator credential to continue; it is not saved by the browser.

The [delivery contract](contracts/product-workspace.md) and
[verification record](verification.md) describe the current guarantees and limits.
