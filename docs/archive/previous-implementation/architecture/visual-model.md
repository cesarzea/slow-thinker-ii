# Visual model

> **S06-UX target update — 2026-10-02.**
> The prepared [S06-UX interaction contract](../contracts/workspace-interaction.md)
> adds the owner-requested optional resource layer, dedicated toolbar, adjacent
> inspector and contextual navigation. It preserves agent-focused defaults, exact
> execution identities and mediation semantics. The initial presentation below is
> historical where it conflicts with that target; the new behavior is not yet implemented.

**Status: Agent-focused presentation approved on 2026-09-30.** The current
[sprint contract](../specification/agent-canvas-sprint.md) supersedes the earlier
proposal to show the component inventory as separate canvas nodes.

## Agent canvas

The canvas shows the experiment's agent steps and collaboration routes. It does
not display the platform's component registry. A single-agent experiment has one
rectangle with an accessible AI-agent icon, the type **LLMCall**, the name
**Proposer** on another line, and an outgoing arrow ending in empty space.
Its left input and right output connectors are visible, and an incoming arrow
starts in empty space at the declared entry step. Both boundary arrows follow the
card's current connector position. They add no visible platform nodes.

Each declared step has a stable planned-node identity. Two steps may use the same
agent, but repeated runtime activations do not create extra agent instances.
Unknown extension steps retain their original type and a generic component icon.
Graph-shaped agent output remains inspectable output, never a replacement for the
experiment's execution graph. Screen positions cannot change execution semantics.

The canvas exposes **Structure**, **Execution** and **Reorganize graph**, plus two
independent options, initially disabled:

- **Show configuration** adds the configured LLM model and reasoning effort inside
  the agent rectangle. For compositions, resolve their model-bearing worker.
  Distinguish graph configuration from the admitted saved-run configuration.
  Never present missing effort as a known provider default or a placeholder model
  as the actual executed model. Missing information is explicitly unavailable.
- **Show system elements** adds small black circles at route midpoints and terminal
  endpoints. These symbolize orchestration mediation without adding controller or
  output boxes. Inspection by hovering/clicking these markers is a later feature.

Control arrows show declared routes, including reviewer feedback and terminal
acceptance. They are not evidence of a direct peer call. Permissions, model
bindings, controller operations, internal component calls and later inferred
influence must remain semantically distinct from control routes.

## Resources and evidence

A **Resources** list sits below the canvas. **Explore graph and evidence** provides
keyboard-accessible selection of components, planned nodes, exact activations and
calls. Internal components and orchestration records remain inspectable here.

Execution mode annotates each agent-step card with its latest recorded state and
activation count. It does not silently select the last invocation when an exact
activation is requested. The inspector identifies the selected run, revision,
component, planned step and activation or call as applicable.

Selecting a component or planned node shows configuration and matching recorded
activations. Selecting an activation opens that invocation's effective inputs,
outputs, reports and nested calls. Selecting a call follows its exact identity to
arguments, response, provider usage and cost. Input bindings retain their original
source references; the UI must not imply every earlier response was included.

The [observation contract](../contracts/observation.md) distinguishes captured,
missing, redacted and unavailable data. Reported reasoning is evidence supplied by
a component, not a complete account of private reasoning. A message alone does not
prove influence. Structured/text outputs render as inert data. Costs distinguish
settled amounts from outstanding obligations and retain their accounting scope.

## Workspace and interaction

The selected bundled graph is visible before execution. A saved execution always
uses its admitted definition, independently of the currently selected example.
Session navigation, input forms, Start/Stop controls, history and the inspector
remain outside the canvas. Graph editing, uploads and dynamic editing are later
capabilities. All product-authored content and accessible labels are English;
user input and recorded evidence retain their original content.

Starting requires valid input and a resolved definition. Pending or uncertain
commands recover by identity; they never blindly replay execution. History
navigation remains disabled during active execution in the first profile.
Credentials remain in memory and never enter visual configuration summaries.

Preserve dragged positions and viewport during polling/status/cost changes. Fit
once when an exact definition arrives. Reorganize explicitly restores layout and
fit. Separate reciprocal forward/return routes so their labels remain readable.
Showing inline configuration must leave enough space for cards and arrows, also
on narrow screens. Provide equivalent evidence access through ordinary focusable
controls; color or pointer-only interaction must not be the sole means of access.

## Live updates

Read authoritative bounded snapshots through the same-origin operator API. Keep
at most one read outstanding per selected view, discard obsolete selection
responses and retain exact snapshot boundaries while paging. The view token covers
all returned state, including shared budgets; event sequence alone is insufficient.

A disconnected browser retains its last view marked stale and reconnects through
reads. It cannot mark a run finished merely because the connection failed. Disable
new Start when active-run status is unknown; Stop acknowledges its outcome or
reports uncertainty. Terminal execution may still have unsettled costs or pending
cleanup, which remain explicit. No UI action may infer or replay component calls.

## Verification and future work

The [sprint acceptance cases](../specification/agent-canvas-sprint.md#delivery-review-and-testing-phase)
cover actual browser geometry, display options, saved model provenance, keyboard
inspection, repeated invocations, English UI and existing recovery behavior.
Current pass/fail evidence belongs in the [verification record](../verification.md).

Marker inspection, extension-specific renderers, later editing tools, influence
analysis and numeric visual/performance targets remain separate work. The
[question register](../specification/open-questions.md) tracks outstanding decisions.
