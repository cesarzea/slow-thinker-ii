# Interface concept review notes

| Document control | Value |
| --- | --- |
| Record ID | UX-S06-001-N01 |
| Date and timezone | 2026-10-02, Europe/Lisbon |
| Owner | Cesar Zea |
| Status | Owner requirements recorded; design review continues |
| Scope | Follow-up to the interface concept images; no implementation authorization |

These notes supplement the [usability review](README.md). They distinguish owner
requirements from proposed interaction details. The original audit remains evidence
about the existing application, not the concept images. Statements below summarize
the Spanish-language design discussion in English; they are not verbatim quotations.

## Owner requirements

| ID | Requirement | Delivery boundary |
| --- | --- | --- |
| DR01 | Provide a visible **Add component** action in the agent-composition editing experience. The reviewed image omits it. | Include in a later concept revision; placement and compatible-choice interaction still need design review. |
| DR02 | The application layout must use 100% of the available browser width. | Use a fluid workspace rather than a fixed-width centered page; sidebar, graph and inspector share the available width, with ordinary internal padding. |
| DR03 | An agent must eventually be able to contain a graph as its implementation. | Future capability explicitly deferred; do not implement nested-graph execution or editing as part of this visual review. |
| DR04 | Resource use is configurable per agent. A shared resource may be used by some agents or by all, according to configuration. | Never infer universal use from a resource being listed for the experiment. Distinguish configured bindings from observed runtime calls. |
| DR05 | Clarify the relationship between resources listed below the graph and the agents that use them. The owner cannot see that relationship in the graph image. | Resource-link visualization is unresolved; a list of resources alone does not settle the graph representation. |
| DR06 | Long agent instructions must be expandable for comfortable reading and editing. | Preserve this earlier requirement in the next concept revision. |
| DR07 | Resource connections must meet an unoccupied part of the agent card border, without a circular handle. They must not attach to the circular execution-flow ports. | Keep dashed resource bindings visually and geometrically separate from execution connections. |
| DR08 | Prompt expansion must use a discreet icon inside the textarea, rather than a separate labeled button in the section header. | The revised concept places the icon in the upper-right inner corner. Preserve accessible naming, keyboard access and a usable hit target during implementation. |
| DR09 | Keep global **Workspace settings** in the lower-left sidebar above the signed-in user's account-menu access, together with available credit or consumption information. | Visually separate this persistent global area from experiment navigation. The concept uses monthly spending and remaining budget with illustrative amounts, not a verified credit balance or implemented account system. |
| DR10 | Replace the monetary usage presentation with available credits that decrease with consumption. | Supersedes DR09's initial monetary illustration. Display an illustrative remaining credit balance and usage; credit valuation, deduction rules and replenishment are not defined by the mockup. Preserve the existing cost-accounting requirements. |
| DR11 | Graph visibility controls must be pressed/unpressed toggle buttons in a dedicated graph toolbar. The toolbar also accommodates Add agent, Add resource, Delete and further actions or menus. | Replace inline checkboxes; distinguish stateful visibility controls from editing actions. The concept keeps Resources pressed and Configuration/System unpressed. This is a design requirement, not authorization to implement new graph-editing behavior. |
| DR12 | Show a horizontal consumption bar with credit figures in small text below it. Do not redraw the concept for this adjustment. | Supersedes the prominent credit balance in the latest image. Keep figures readable; the bar's allocation, scope and treatment of reserved usage depend on the credit contract still to be defined. |
| DR13 | For the current interface, users and credits are illustrative placeholders; their actual behavior remains to be defined and implemented. | Explicitly identify this area as a preview using English product copy. Keep the credit bar and small figures from DR12, but do not imply real authentication, a funded balance or actual deductions. Existing operator access and real cost limits remain authoritative. Credit and account semantics no longer block this UI scope. |
| DR14 | Include a history of graph changes and versions. | Cover saved graph revisions and their changes within the selected experiment. Keep this distinct from execution history and installed component versions. Detailed interaction and API contracts belong to the upcoming specification. |

At the initial note-taking checkpoint, the owner requested recording these points
without regenerating the image. Subsequent requests authorized revised concept
images, including the DR07 endpoint correction. They do not authorize application
implementation. No application code, configuration, graph or runtime data is changed
by this record.

The subsequent DR13 clarification explicitly defers real user accounts and credit
accounting. It supersedes the earlier prerequisite to settle those systems before
delivering their visual area. DR14 adds graph-version history to the requested
design scope. These requirements do not authorize application implementation.

The [implementation feasibility assessment](feasibility.md) evaluates the latest
concept against the existing contracts and implementation. It records dependencies
and scope boundaries, not approval to implement them.

## Proposals already discussed, not completed contracts

- Keep workspace navigation separate from experiment navigation. The revised
  concept uses Experiments, Component library and Workspace settings globally;
  Design, Resources and Runs belong to the selected experiment.

  **Subsequent navigation revision:** inside an experiment, the main sidebar now
  identifies that experiment and contains Design, Resources, Runs and Experiment
  settings; All experiments returns to the collection. The owner then requested
  persistent global Workspace settings, usage and user-menu access in a separate
  lower-left footer (DR09). This supersedes the earlier image's selected global
  Experiments item while viewing experiment detail. Settings scopes must remain
  explicit despite sharing the sidebar.
- Treat the instruction editor's compact and expanded views as the same draft,
  with experiment-level saving. Search, cursor retention and the exact expanded
  layout are proposed interaction details.
- Derive composition controls from declared extension points, configured instances
  and compatible catalog entries. Tools & memory and Routing are illustrative
  groups, not mandatory sections for every component. Presentation metadata and
  compatibility contracts still require specification.
- Distinguish contained components from bindings to shared resources. Adding a
  binding must not silently duplicate a resource or grant additional authority.

## Proposed graph-version history

Add **Versions** to the selected experiment's navigation, alongside Design,
Resources and Runs. Use saved immutable revisions as the history unit; a working
draft is not a saved revision and individual keystrokes are not history entries.
Proposed ordinary actions are:

- Browse revisions with their exact identity, available save metadata and recorded
  source revision. Do not infer chronological order from opaque revision labels.
- Open a historical graph and configuration in read-only mode.
- Compare two saved revisions, initially defaulting to the recorded source where
  it is available. Explain agent, configuration, connection, resource and permission
  changes without requiring raw JSON; retain exact technical differences as detail.
- Create a new editable draft from a selected historical revision. Saving produces
  a new revision and preserves previous revisions and their execution evidence.

Existing immutable identities, source retrieval and `derived_from` provide a
foundation, not a complete chronological history or comparison API. Define complete
experiment-scoped pagination, trustworthy ordering and metadata origins during
analysis. Historical dates or authors that were not recorded must remain explicitly
unavailable; the demonstration user must never be used as an attribution source.
Revision lineage can branch and cross experiment boundaries, so do not invent a
single chronological parent chain from the listing order. Version comparison here
means definition changes, not automated quality or influence evaluation.

## Open visual decision: resource relationships

The earlier preference for an agent-focused default graph remains recorded. The
latest observation adds the need to understand each agent's resource bindings;
it does not establish whether resource nodes should always be visible.

**Recommendation for review:** offer an explicit **Show resources** view/layer.
When enabled, show a shared instance once and connect it only to its configured
consumers. Make those links visually distinct from control-flow arrows. Selecting
an agent or resource should highlight its corresponding relationships. Keep
orchestrator/system markers under their separate visibility control.

In either view, resource summaries should identify the actual consumers and offer
a route to configuration. Being available in the experiment, being bound to an
agent, being authorized for an operation and having been used in a run are separate
facts. Their presentation must not imply equivalence.

The subsequent concept images illustrate this layer at the owner's request. Its
default visibility and complete interaction contract remain under review; image
generation does not approve application implementation.

## Analysis and documentation checkpoint

After DR13–DR14, the owner authorized preparation of the complete analysis and
engineering documentation. The resulting [delivery specification](../../specification/s06-workspace-redesign.md)
closes the bounded target and distinguishes future capabilities. The
[preparation review](preparation-review.md) records the handoff walkthroughs and
remaining implementation/verification phases. No new image or application code
was produced in that phase.
