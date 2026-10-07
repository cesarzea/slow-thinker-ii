# Step 1 sprint report

| Document control | Value                                                                        |
| ---------------- | ---------------------------------------------------------------------------- |
| Document ID      | STEP-1-REPORT                                                                |
| Revision         | 1                                                                            |
| Report version   | `0.0.6.7`, sprint S06                                                         |
| Owner            | Cesar Zea                                                                    |
| Date             | 2026-10-05                                                                   |
| Delivery         | [Step 1](README.md), cycle [C12](../../continuous-improvement/cycles/012-core-step-1/report.md) |
| Source state     | Working tree of branch `core-foundation`, not committed                      |
| Status           | Locally verified after the owner's review; accepted by the owner on 2026-10-07 |

## Summary

Step 1 delivered the validated journeys J1–J3 and the activity view, and passed the
complete runner on 2026-10-04. The owner then reviewed the running product with quick
changes, deferring testing and validation to the close. The review reshaped how graphs
are edited and run: every edit is saved, versions are activated on purpose, runs execute
what is on screen inside the editor, the operator chooses where to observe a run, and
agents can have a memory as an isolated component. The close brought tests, gates,
journeys and documentation up to the reviewed product and passed the complete runner
again. Evidence: [verification record](verification.md).

## Delivered in the review

Grouped by functional unit; decisions are recorded in ADRs 0024–0026.

- **Saving, versions and branches** ([ADR 0024](../../adr/0024-working-copy-and-activated-versions.md)).
  Every edit is saved as a change; Undo and Redo move through the saved history;
  activation creates numbered versions; branches start from a version or a change and
  are drawn as lanes, without merge.
- **Editor.** A professional layout: header with the graph's version and save status,
  a floating canvas toolbar (Undo, Redo, Arrange with ELK and dagre modes, zoom, Fit,
  Outline, connection style), cards with ports and a memory chip, connection removal on
  the canvas, node deletion from the card, menu, keys and outline, double click to
  configure, fixed-size node dialogs with section navigation, compact and aligned
  configuration controls with presentation attributes, collapsible side panels with
  one control, a resizable right panel up to the full width, port sides, and three
  connection styles saved with the graph (curved, simple curve, routed around boxes).
- **Pages and access.** Components and Runs pages; spending shown to three decimals; an
  opt-in loopback mode without operator token, and the token kept per browser tab.
- **Run mode** ([ADR 0025](../../adr/0025-runs-of-changes-and-run-mode.md)). Run enters a
  mode of the same screen without executing; Execute runs the branch's latest change,
  never activating it, and asks for the message only when the Trigger says so (new
  Trigger option “On manual runs”). The run's address opens the editor in run mode,
  also from the Runs list; the separate run page is gone, and the activity page waits
  for its redesign behind the run's address.
- **Observation points** ([ADR 0025](../../adr/0025-runs-of-changes-and-run-mode.md)). The run,
  each node unfolding into what it records (activity, component calls, LLM calls,
  reports, output component, memory, results) and each connection, chosen on the left
  or with a dot on each connection, saved with the graph. The run panel shows their
  events live, to the millisecond, or one point's activity; a Content view hides
  lifecycle events.
- **Memory** ([ADR 0026](../../adr/0026-memory-position.md)). A new embedded position,
  `memory`, served by its own host process through two protocol operations, `recall` and
  `remember`. The first component, `memory@1.0.0`, keeps a run's latest exchanges and
  adds them to each message as a transcript. The platform holds none of its logic.
- **Models.** The demonstration configuration adds GPT-5 nano, the cheapest of the
  configured providers' models.

## Verification at the close

- All gates of the complete runner passed on the final source; see the
  [verification record](verification.md#complete-runner) for figures and times.
- Tests were added for every reviewed unit: change runs (application, HTTP, SQLite and
  migration 3 → 4), the memory position (engine, real host processes, host SDK, the
  Memory package), observation points and run mode, the side panels, Memory in the
  palette and node dialogs, and a browser journey in which an Editor with a Memory,
  whose Router sends its first reply back to it, recalls that exchange.
- The browser journeys were updated to autosave, run mode and the activity page's
  address.

## Open items for the owner

| Item | Detail | Proposed handling |
| ---- | ------ | ----------------- |
| Licenses of new interface dependencies | `obstacle-router` 0.1.2 (LGPL-2.1, routing around boxes) is bundled into the interface; `elkjs` 0.12.0 is EPL-2.0 (loaded on demand); `@dagrejs/dagre` and `@tisoap/react-flow-smart-edge` are MIT. | Decided by the owner on 2026-10-07: the repository is licensed under FSL-1.1-ALv2 with the contribution terms in the contributing guide ([ADR 0027](../../adr/0027-functional-source-license.md)), and the dependencies stay as they are. LGPL-2.1 requires that users can replace `obstacle-router`; serving routed connections as a separate chunk remains available if that is ever needed. |
| Trigger declaration | `manual_runs` was added to `trigger@1.0.0` as an optional field, without a version change. | Decided by the owner on 2026-10-07: it stays in `trigger@1.0.0`. |
| Activity page | Reachable only by the run's address followed by `/activity`. | Redesign in a later sprint. |
| Interface branch coverage | 90.59%, just above the 90% threshold. | Add tests in the next sprint to restore a margin. |
| Memory nodes and simultaneous messages | A memory is stateful, so its node takes one activation at a time; a second message that arrives while the first is being handled fails its activation with `node_busy`, and the run with it (for example, two writers feeding one Editor in parallel). | Input queues at node inputs (step 4) will hold the second message instead. |
| Demonstration servers | The real-provider server on port 8765 has stopped; its configurations in `.local/showcase` still name the earlier component resolutions. | Update the resolutions before starting it again. |

## Next sprints

Replanned with the owner on 2026-10-05; see the [roadmap](../roadmap.md).

- **Next sprint (step 2).** Labs, a workspace per objective that groups its graphs,
  runs and results; mem0 as a memory component, to validate how persistent memory will
  work; then shared context and variables as resources.
- **Later, without a sprint yet.** Pre-warmed component hosts, agents in separate
  containers (step 8), and memory that lasts across runs.
