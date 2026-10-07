# S06 usability and comprehension review

| Document control | Value |
| --- | --- |
| Review ID | UX-S06-001 |
| Version | 1.0 |
| Date and timezone | 2026-10-02, Europe/Lisbon |
| Baseline | `a844514` — S06 configuration and results |
| Status | Review completed; corrections proposed, not implemented or approved |
| Scope | Existing configuration, execution and inspection UI |
| Owner | Cesar Zea |

## Assessment

The current UI does not yet provide a dependable product experience for configuring
and reviewing agent collaboration. It exposes substantial functionality, but users
must understand the internal component model, coordinate disconnected editors and
remember a fragile editing sequence. Some problems can produce incorrect edits or
invalid configurations; they cannot be resolved by spacing, colors or tooltips alone.

The strongest direct observation is a selection mismatch: clicking **Reviewer** in
the graph opens `node: review` as raw JSON while the **Agent** editor continues to
select **proposer**. The user is not merely searching for a distant form; the two
parts of the screen can refer to different agents.

Technical verification remains valid evidence for its tested cases. It does not
establish usability acceptance. The owner rejected the current interaction, and
this review identifies concrete gaps in U01–U07 of the
[completion contract](../../specification/s06-product-completion.md).

## Reading guide

- [Findings](findings.md): 26 prioritized issues, their evidence, consequences and proposed corrections.
- [Control inventory](control-inventory.md): what each existing control family means, why it is difficult to understand and how it should be presented.
- [Evidence record](evidence.json): reviewed states, baseline, observations and verification limits.
- [Observed agent-selection screen](agent-selection.png): the raw object summary shown after selecting Reviewer; the agent editor is farther down the page.
- [Interface concept review notes](design-review-notes.md): subsequent owner requirements, deferred nested graphs and unresolved resource-link presentation.
- [Implementation feasibility](feasibility.md): fit with the project, reusable implementation, required contract changes and remaining user journeys.

## Method and boundaries

This is an expert walkthrough and source review, not a measured study with
representative users. The primary assumed user understands agents, prompts and
experiments, but does not know this application's Python packages, JSON Pointer
paths, controller operations or persistence implementation. Extension developers
are a secondary audience requiring complete technical access. These audience
assumptions should be checked with the owner before detailed redesign.

The walkthrough covered Experiments, Agents, Connections, Task inputs, Components,
Resources, Settings, Runs, successful and failed saved runs, and the technical
inspector. Representative definitions were `resource-collaboration/example-2` and
`bounded-review/example-1`. Static inspection covered controls not safely exercised
in the live workspace, including saves, imports, deletion, permissions, cancellation
and uncertain-command recovery. Frontend/backend contracts were traced where a
form's meaning depended on the execution profile.

The existing operator credential was used for access; subsequent interactions
were navigation, selection and disclosures. No experiment, grant, budget or saved
credential configuration was changed, no run was started and no paid model call
was made. The existing local services were restarted to inspect saved data. The initial
catalog failure coincided with those services being stopped; it is not evidence of
a backend catalog defect. The UI's misleading connected/empty/error presentation
is assessed separately.

Evidence labels in the findings distinguish **observed** screen behavior,
**source-confirmed** implementation and **inferred** user consequences. Failure
paths established by source inspection were not reproduced by altering live data.
No completion-time, error-rate, SUS score or WCAG conformance claim is made.

The review applies task-oriented heuristics concerning status, familiar concepts,
error prevention, recovery and information hierarchy. These are evaluation criteria,
not automatic proof of a defect. See [Nielsen Norman Group's usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/).
Form guidance and keyboard questions use the [W3C guidance on labels and instructions](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html).
For an inspector implemented as a modal in a future design, the relevant reference
is the [WAI-ARIA modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/);
the current complementary panel is not assumed to be a modal merely because it overlays content.

## Main conclusions by user task

| User task | Current assessment | Principal findings |
| --- | --- | --- |
| Understand the collaboration | The canvas communicates sequence, but its selection opens internal records and its preview represents saved source. | UX01, UX02, UX07 |
| Change an agent's behavior | Prompt/model controls exist, but selection, pending edits and compatibility are unreliable as a combined journey. | UX01, UX03–UX05, UX08 |
| Add an agent or component | Creation is split across advanced instance and node editors, without guided required configuration. | UX13, UX26 |
| Attach tools or memory | Shared consumers and explicit permissions are valuable; incompatible choices and technical grants undermine comprehension. | UX09–UX12 |
| Define collaboration and feedback | Forms require source/target/path/port knowledge; some sequence controls offer invalid or ineffective settings. | UX06, UX14, UX15 |
| Define required task data and output | Schema builders exist, but expose schema vocabulary; run forms do not preserve the same level of guidance. | UX11, UX16, UX17 |
| Execute and recover | State safeguards exist, but blocked Start, failures and cancellation lack sufficient explanation or placement. | UX18, UX19, UX24 |
| Understand outcomes and cost | Text is readable; result identity, final-versus-intermediate meaning, numerical fidelity and budget scope need correction. | UX19–UX23 |
| Inspect detailed evidence | Exact identities and evidence access are useful, but technical events are the first inspection experience. | UX19, UX25 |

## Priorities

**P1** means a core task can edit the wrong object, lose work, run/save values other
than those shown, produce an invalid configuration through ordinary controls, or
misrepresent result evidence. Resolve these before proposing S06 product acceptance:

- UX01: one selected agent across graph and editor.
- UX03–UX05: truthful pending state, preservation of edits and a workable revision lifecycle.
- UX06: controls that match the actual sequence/conditional execution contract.
- UX08: a visible recovery path for incompatible model parameters.
- UX20: truthful raw-result labeling and precision preservation.

**P2** means a task is available but unnecessarily difficult to discover, understand,
complete or recover. These issues are still relevant to S06 usability acceptance;
priority is not permission to defer its ordinary user journeys indefinitely.

## Proposed interaction model

Keep the graph and the selected object's editor together. In design mode, selecting
Proposer should show its name, purpose, instructions and model in a nearby inspector.
Tools, memory and connections should expose the effect of each choice, with internal
composition and raw source available deliberately through Advanced. On a small
screen, use an explicit editor view with a clear return to the graph.

Selection must identify both the collaboration step and the component instance:
the same instance may be used by multiple steps. Show where an edit is shared before
committing it. Do not flatten composition, silently copy resources, grant authority,
discard unknown fields or pretend that every extension is an LLM call.

Use a single coherent pending-change model and a clear experiment save action.
Immutable revisions remain the reproducibility boundary; users should not have to
discover that boundary by receiving a conflict after editing. If the graph cannot
preview draft changes yet, explicitly label it **Saved revision preview** and show
when it differs from the draft.

In run mode, selection should explain the chosen invocation: input, output, status,
duration and cost when available. Intermediate responses and the experiment result
must be distinguishable. A readable activity view can summarize existing evidence;
technical events remain accessible. Do not infer quality, acceptance, influence or
complete private reasoning from completion status or message exchange.

This proposal does not require full drag-to-connect authoring, a new execution
engine, mem0 integration or automated evaluation. Those remain separate scopes.
Some desired history metadata may need API additions and should be estimated
separately from labels and layout.

## Acceptance scenarios for a correction

1. Click Reviewer, edit its instructions, and confirm that every selection label,
   preview and saved change refers to Reviewer. Repeat with a reused component.
2. Type without pressing a field-specific Apply. Switch agent, section and experiment;
   return and verify preservation or an explicit discard decision. Save/Run must not
   silently use older values than the visible edit.
3. Start from a saved example, change a prompt and save a new revision without JSON,
   losing work or encountering a preventable identity conflict.
4. In a sequence, edit an existing previous-response mapping and save successfully.
   No conditional-only metadata is inserted. Explain that the sequence returns all
   node outputs; do not offer an ineffective final-result selector.
5. In a bounded review, configure first-pass optional feedback, branch names, return
   route, Finish and result source. The user can explain each effect before running.
6. Change model or effort with an existing incompatible override. Show the issue and
   an explicit correction action; never strand the value behind a disabled control.
7. Configure persistent/shared memory with ordinary controls. Explain retention and
   affected agents, filter incompatible resources, and grant required access explicitly.
8. Create a task field and a nested response schema. Give meaningful labels/examples;
   show the matching run form and field-specific validation without requiring JSON
   for the supported ordinary types.
9. Open an existing success and failure. Identify the exact revision, task, outcome,
   available response, cost scope and next action. Completion must not imply quality.
10. Explain why Start is blocked, stop an active test run from its status area, and
    recover uncertain commands without issuing duplicate work.
11. Verify exact structured-result numbers through the full API-to-UI path and make
    raw-versus-normalized labels accurate.
12. Complete these journeys by keyboard; verify visible focus, inspector return,
    narrow layouts and field errors. Measure contrast, zoom/reflow and assistive
    technology behavior separately before making accessibility claims.

For each scenario record unassisted success, requests for explanation, wrong turns,
lost changes and whether the user can correctly explain the result. Agree targets
before testing a redesign; this review does not invent measured targets or outcomes.
Retain the technical verification gates, and supplement them with these complete
task journeys and owner review.

## Delivery preparation follow-up

The owner subsequently authorized analysis and documentation of the revised
workspace. The [S06-UX specification](../../specification/s06-workspace-redesign.md)
and [preparation review](preparation-review.md) record the complete target,
interface handoffs and module tickets. The audit above remains evidence about the
existing application; it does not claim that the correction has been implemented.
