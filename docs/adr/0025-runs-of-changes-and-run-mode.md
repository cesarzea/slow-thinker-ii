# 0025. Runs of changes, run mode and observation points

| Decision control | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Status           | Accepted                                                     |
| Date             | 2026-10-05                                                   |
| Deciders         | Cesar Zea (owner)                                            |
| Amends           | [ADR 0024](0024-working-copy-and-activated-versions.md): runs no longer need an activated version |

## Context and problem

With [ADR 0024](0024-working-copy-and-activated-versions.md), Run executed the active
version, which could come from another branch and differ from what the editor showed.
During the step 1 review the owner asked that Run execute what is on screen, that a run
be watched on the same screen, only slightly changed, and that the operator choose
where in the graph to watch, with the choice kept for the next time.

## Decision

- A run executes a version or a change. The editor's Run executes the branch's latest
  change after saving pending edits; it is never activated for that. A run records the
  change it executed and, when that change was activated, the version.
- Run is a mode of the editor, not a separate page. It shows the graph read-only with
  its counts, the observation points on the left and the run panel on the right;
  Execute starts the run. The run's address opens the editor in run mode, also from
  the runs list. Edit returns to editing.
- Observation points are places of the graph where the run's events are recorded: the
  run, each facet of a node (activity, component calls, LLM calls, reports, output
  component, memory, results) and each connection. They are derived from the
  recording contract only. The chosen points are saved with the graph's `view`, like
  the layout, so they return while the points exist.
- The run panel shows the events of the observed points, or of one point the operator
  selects, as they arrive; a Content view leaves out lifecycle events.
- A run of an earlier document is drawn with the working copy's current layout.

## Consequences

- The database records `graph_change` for every run, and `graph_version` may be null
  (schema version 4). The operator API's `POST /runs` takes `version` or `change`.
- Experiments no longer create versions; activation keeps its meaning of choosing the
  graph's official version.
- The separate run page is gone; the activity page stays reachable by its address
  until it is redesigned.
