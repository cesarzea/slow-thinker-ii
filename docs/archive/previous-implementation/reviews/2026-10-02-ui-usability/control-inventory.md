# Control and comprehension inventory — UX-S06-001

This inventory covers the existing UI's control families, including advanced
configuration. Repeated schema-generated fields are grouped by behavior. It is
not a claim to have exercised every value or extension. Evidence, severity and
source references are in the [findings](findings.md); verification limits are in
the [review](README.md). All presentation changes below are proposals.

The intended distinction is between **what the experiment does**, **how a user
configures it**, and **how the platform implements it**. Technical access remains
necessary for extension authors, but internal identifiers should not be the only
explanation offered to experiment designers.

## 1. Access, navigation and experiment identity

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Operator key; Connect | Authorizes local workspace access. Acquisition and verification are unclear; possessing a key is presented as being connected. | Explain where the existing access key comes from; distinguish connecting, verified access, rejection and unavailable service. | UX24 |
| Disconnect operator access | Removes client access and local state. The effect on an unsaved draft and a running server job is not stated. | Explain these effects and protect pending edits before disconnecting. | UX04, UX24 |
| Experiments, Components, Resources, Runs, Settings | Useful top-level separation. Components means installed types, while Resources means instances in an experiment; this relationship is implicit. | Add short purpose descriptions and visible experiment/run context where relevant. Preserve tab state. | UX13, UX21 |
| Refresh configuration; Refresh library | Reload different catalogs. Their distinction and the effect on current work require implementation knowledge. | Name the data being refreshed and report its status without presenting an error as an empty collection. | UX24 |
| Experiment selector; revision; agent/node counts | Select a saved definition. Graph IDs, revision strings and node/component counts do not establish purpose or current draft status. | Show a readable experiment name, revision and saved/draft state; keep exact IDs available. Explain reused agent instances when counts differ. | UX01, UX05, UX13 |
| Load more experiments | Pages through the definition library. The user needs to know what is loaded and whether selection changes. | Keep current selection explicit and explain loading, end-of-list and failure states. | UX24 |
| Graph ID; New revision; Create draft from saved definition | Derive another immutable definition. Creation precedes editing in the present workflow, but New revision becomes disabled once the source is dirty. | A coherent Edit / Save new revision journey that preserves edits; identity choices should not require starting over. | UX05 |
| No unsaved changes; draft status | Reports source differences, not every visible field buffer. It can contradict what the user has typed. | One truthful pending-change state covering visible edits, validation and uncertain saves. | UX03 |
| Apply on individual fields | Transfers local field text into the source draft; it does not save an experiment revision. Other controls apply immediately. | Prefer consistent editing and a clear experiment save action. If Apply remains necessary, state its scope and include unapplied text in pending status. | UX03, UX16 |
| Validate definition | Checks the applied draft. Users may expect it to validate all visible text. Errors identify source paths more readily than the form to correct. | Include pending values or explain exclusions; link each error to its object and field. | UX03, UX16 |
| Save definition | Persists an immutable revision. This is easy to mistake for updating the selected saved revision. | Explain the resulting revision, validate identity before submission and keep draft text on failure. | UX05 |
| Discard draft | Restores source, without an adequate review of lost changes or a unified field-buffer reset. | Confirm the concrete scope of discard and reset all corresponding pending state. | UX03, UX04 |
| Import file; Advanced JSON; raw source editing | Necessary escape hatch for hand-authored definitions and extensions. Replacement and validation behavior are not an ordinary editing journey. | Keep deliberate advanced access; preview replacement, retain exact source and explain import errors locally. | UX04, UX16, UX26 |
| Uncertain save recovery | Reuses a command whose server outcome is unknown. Technical replay wording can be confused with saving or executing again. | Explain that confirmation was lost and that recovery checks/reuses the same operation; never imply a duplicate run is needed. | UX03, UX18 |

## 2. Graph and selection

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Agent card: icon, type, name | Good starting point, but type/step/component identities are not unified with the editor. | Use the agent name prominently, its component type second, and the selected step when an instance is reused. | UX01, UX13 |
| Entry/exit arrows and ports | Represent control routing. Visible handles suggest drag-to-connect despite that interaction being disabled. | Show readable direction and exit names; offer an explicit connection-edit action. Do not imply unsupported graphical authoring. | UX07, UX15 |
| Click agent | Opens a selected-object summary; does not change the Agent editor selection. | Select the same object everywhere and open its nearby configuration. | UX01 |
| `node: draft`, `node: review`; JSON summary | Internal step identity, component, operation and input bindings. It is the first response to a normal graph click. | Human-readable agent/step summary; raw definition behind Advanced. | UX01, UX02 |
| No activations in the visible snapshot | Describes runtime evidence, including when no run is being inspected. | Omit runtime absence messages in design mode; explain them only for a selected run. | UX01 |
| Structure / Execution | Switches structural and runtime views. The distinction between edited draft, saved definition and historical execution is not sufficiently prominent. | Display which revision/run the graph represents. Never let draft editing change historical evidence. | UX07, UX21 |
| Show agent configuration | Reveals model/settings on cards, but the canvas can represent saved source while forms contain edits. | Label the preview accurately and show pending divergence until draft rendering exists. | UX07 |
| Show system elements; evidence controls | Exposes mediation details valuable for inspection. Ordinary users should not have to configure the orchestrator to edit an agent. | Keep optional system visibility, explain markers and show recorded traffic in run context. | UX15, UX25 |
| Zoom, fit view, pan, Reorganize graph | Useful viewing controls. They change presentation, not execution order. | Retain; distinguish layout changes from flow changes and provide usable keyboard access. | UX07, UX25 |
| Resource buttons and evidence list below graph | Alternate navigation to resources/internal records; not a direct configuration journey. | Show resource purpose and users, with a clear Configure action; keep the accessible evidence list. | UX12, UX13, UX25 |

## 3. Agent behavior, composition and model settings

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Agent selector | Selects an editor independently of the canvas. IDs such as proposer are clearer than step IDs but still lack shared selection. | Synchronize with the graph and identify all affected steps. | UX01 |
| Configure worker; Configure parent agent | Distinguishes internal LLM work from composition behavior. Two large forms make a single conceptual agent look like unrelated objects. | Organize by purpose: Instructions, Model, Response, Tools and memory, Routing; expose composition details when needed. | UX02, UX12 |
| Instructions | Prompt governing the LLM call. Plain text is understandable, but the effective value and commit state are not. | Give it primary placement, a useful height and explicit pending state; explain how supplied task/context relates to these instructions. | UX03, UX11 |
| Model profile; model resource binding | One selects provider/model settings, another connects a component instance. Both can appear to be the same Model choice. | One ordinary model choice with provider/model and effective settings; explain resource sharing and profile identity in details. | UX08, UX11, UX12 |
| Reasoning effort | Model-specific reasoning setting. Blank/unsupported/default states and cost/latency implications are unclear. | Show supported choices and effective default. Explain that it controls model behavior, not guaranteed access to complete internal reasoning. | UX08, UX11, UX25 |
| Maximum completion tokens | Caps generated output under provider semantics. Empty input gives no clear effective value. | Show the effective output limit, its source and supported range; explain possible truncation and budget interaction. | UX08, UX11, UX22 |
| Temperature | Sampling setting whose compatibility depends on model/effort. A retained invalid value can become disabled and impossible to clear normally. | Offer Use model default / Remove override and explain compatibility beside the field. | UX08 |
| Response format: text / JSON | Determines whether an LLM response is plain text or structured. Changing mode affects the associated schema. | Explain both formats in user terms and the effect on existing response fields before removal. | UX11, UX16 |
| Response fields | Defines expected structured output. Users need a field builder with examples, rather than schema terminology alone. | Field name, readable label, type, required status and sample response; keep exact schema available. | UX16 |
| Advanced model parameters and extensions | Provider-specific options not covered by ordinary forms. They must survive unrelated edits. | Preserve complete source, indicate known incompatibilities and avoid silently resetting unknown values. | UX08, UX26 |
| Worker binding; Worker operation | Chooses which internal component performs the work and which operation is called. It is not an ordinary prompt setting. | A named internal capability with required inputs/outputs; operation IDs in Advanced when no ordinary choice is needed. | UX12, UX26 |
| Input schema; Worker output schema | Internal composition contracts, distinct from the experiment task form and model response schema. Their similar names invite confusion. | State whose input/output is described, where values originate, and the consequence of changing it. | UX11, UX16 |
| Result pointer | Selects a value within the worker response. An empty pointer and nested wrappers require JSON knowledge. | Describe Whole response versus a named field; show an example and retain the exact pointer. | UX11, UX14 |
| Managed parent | Declares containment for an internal component. The user cannot infer lifecycle and authority implications from the label alone. | Keep in composition details with a description of ownership and affected references. | UX12, UX26 |

## 4. Tools, memory, routing components and permissions

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Calculator / Memory resource selectors | Bind a resource instance. Current choices can include incompatible model resources. | Filter by required operations; show existing incompatibilities as errors, not valid alternatives. | UX09 |
| Use calculator | Enables ContextualCall's deterministic calculation stage, not arbitrary autonomous model tool use. | Explain when calculation happens, which expression is read and where the result is placed. | UX11, UX12 |
| Expression pointer; Calculation field | Map task data into calculation and inject its output into worker context. Both names hide the data movement. | “Calculate expression from …” and “Provide the answer to the agent as …”, with field suggestions and preview. | UX11, UX14 |
| Calculator Max exponent / Max expression bytes / Max nodes / Max result bytes | Bound expression complexity and size. Max nodes concerns the expression parser, not graph agents. | Resource safety limits with units and examples; distinguish parser nodes from graph nodes. | UX11, UX22 |
| Read memory / Write memory | Enable explicit composition steps. They do not alone establish retention, visibility or permissions. | Show when reading/writing occurs and the data involved, together with access status. | UX10–UX12 |
| Memory key; Memory field | Select a stored entry and the worker-context field that receives it. They are different from the namespace and a model context window. | Use a short data-flow example and effective defaults; warn about shared keys when relevant. | UX11, UX12, UX14 |
| Retention | Chooses whether memory is run-scoped or persistent. Currently appears as Advanced JSON for a bundled component. | Ordinary This run / Across runs choices, describing survival across executions. | UX10 |
| Namespace | Groups stored keys; it is not itself a complete privacy/sharing setting. | Explain its storage effect alongside actual consumers and permissions. | UX10–UX12 |
| Max entries; Max value bytes | Memory capacity bounds. Labels lack useful units, defaults and consequences at capacity. | Show readable capacity and explain rejection behavior without implying automatic summarization or eviction. | UX11, UX22 |
| Private/shared resource; consumer list | Describes who references an instance. Existing consumer labels are valuable, but binding does not guarantee authorization. | Show affected user-facing agents and separate access from sharing. Explain the impact of editing the shared instance. | UX12, UX13 |
| Router resource; declared Outputs | A reusable routing component can be embedded in an agent. Exit declarations occur in multiple places. | Show the internal router within Routing and reconcile declared exits visibly. Preserve standalone use for experts. | UX15 |
| Selector | Python callable reference selecting a declared exit in the reviewed router. The field does not accept arbitrary inline Python code. | “Routing function”, expected reference syntax, input/output contract and valid exits; show a small example. | UX15 |
| Caller / Target / Operations; Grant / Revoke | Explicit authority over mediated calls. Users must reconstruct parent/worker/resource call chains. | Explain capability-level access beside the relevant tool; explicit grant/revoke with affected-operation detail. Never grant silently. | UX12 |
| Advanced resource bindings/configuration | Allows custom slots and extension data. Generic fields cannot assume every component is an LLM. | Retain a complete expert path, informed by declared capabilities and meaningful validation. | UX09, UX26 |

## 5. Graph structure, data mappings and control flow

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Node selector; component; operation | A graph step invokes an agent instance. Selecting by step ID is separate from selecting the agent. | “Step using Reviewer”, with reuse context and valid operations; synchronize the selected step. | UX01, UX14 |
| Add agent node / Remove node | Adds/removes a step, not necessarily its component instance. Creation is separate from building/configuring that instance. Removal has dependencies. | Guided Add agent/step journey; explain reused components and show affected routes/mappings before removal. | UX13, UX16 |
| Target input | Names the input delivered to an operation. Users must know the operation contract. | Suggest accepted fields with descriptions and types; retain custom names where the schema permits. | UX14 |
| Source: task input / completed agent response / fixed value | Chooses where a value comes from. A data reference does not determine execution order. | Readable “Give Reviewer the proposal from Proposer” summary with type and example. | UX14 |
| Source node; Response field path | Selects a producing step and value path. The same label is used for task data; wrapper paths expose internals. | Contextual Task field / Agent response field choices with exact pointer as an advanced value. | UX14 |
| Fixed value; nested value builder | Supplies literal data. Types, null, absent and empty values differ. | Make these states explicit, preview the actual delivered value and retain exact numbers. | UX14, UX16 |
| Optional feedback / latest completed response | Uses a previous completed invocation, allowing no value on the first pass. This is specific to supported conditional behavior. | Explain first-pass behavior and which previous response is selected; do not insert this metadata into sequence graphs. | UX06, UX14 |
| Output port: constant / response field | Selects a named control exit; it is distinct from the response content. Sequence definitions reject a node output selector. | Offer only where supported; explain “Which branch does this step choose?” and preview its value. | UX06, UX15 |
| Execution profile; Flow component; Flow operation | Select coordinated execution machinery. Independent raw choices can leave an incompatible combination. | Purpose-oriented Sequence / Bounded review choices for supported profiles; preserve custom controller access in Advanced. | UX06, UX15 |
| Sequence order controls | Set the order of steps in finite sequence execution. They do not define arbitrary conditional transitions. | A readable ordered list consistent with the graph; show dependencies and invalid reorder consequences. | UX06, UX07 |
| Entry node | First step in a conditional graph. Technical node IDs make the choice harder to relate to the canvas. | “Start with Proposer”, linked to the visible step. | UX15 |
| Maximum activations | Bounds step activations. It is not the same as review rounds, model calls or maximum call depth. | Explain a concrete loop, including what counts and what happens at the limit. | UX15, UX22 |
| Route source / port / destination; Add/remove route | Defines what happens after a named exit. Several fields must agree across graph and component configuration. | Show “When Reviewer chooses revise → Proposer”; validate declared exits and reveal dependent changes. | UX15, UX16 |
| Finish | Ends the control path. It does not itself identify what response is returned as the result. | Explain Finish execution separately from Return this result. | UX15 |
| Final result source and path | Selects returned content in conditional execution. Sequence execution instead returns all node outputs, even if a result binding was accepted in source. | Conditional: readable result selection. Sequence: explain the aggregate and do not offer an ineffective selector. | UX06, UX15, UX19 |

## 6. Schema builders and task entry

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Task inputs / Input schema | Defines what a person supplies when starting a run. This differs from internal operation inputs. | “Information required to run this experiment”, with a matching run-form preview. | UX16, UX17 |
| Field name; type; Required; title; description | Core schema authoring is present, but technical names and labels are not clearly separated. | Human label and help first, stable technical key in details; show required/default meaning. | UX11, UX16 |
| Nested objects and arrays; items | Describe grouped fields and repeated values. Depth and multiple Apply levels increase bookkeeping. | Consistent nested editor with a sample response/task value and a single coherent pending state. | UX03, UX16 |
| Minimum/maximum; exclusive bounds; min/max length; pattern; enum | Validation constraints. Schema keywords obscure ordinary rules. | “At least”, “Less than”, “Allowed values”, “Text format”; explain inclusive/exclusive and string-length semantics. | UX11, UX16 |
| min/max properties; additionalProperties; array constraints | Advanced shape restrictions. Their effect is difficult to predict from the raw keyword. | Plain-language rule summaries with examples; retain schema keywords in advanced details. | UX16 |
| Remove field; change type | Can invalidate references or leave incompatible constraints. | Show affected mappings and a deliberate migration/removal choice; preserve unsupported source without hiding active constraints. | UX16 |
| Advanced schema JSON | Supports constructs beyond the builder. First-party enum retention currently falls here unnecessarily. | Use fallback only for genuinely unsupported constructs; explain the limitation and preserve source. | UX10, UX26 |
| Run form: task values | Reuses only part of the schema information. Labels/help/choices are less informative than the authored schema. | Honor descriptions, required status, supported enum choices and constraints; validate near the field after meaningful interaction. | UX17 |
| Run input JSON fallback | A nested input can force the entire task into a JSON box. | Recursive form entry for supported ordinary types; a clearly labeled advanced JSON mode for full access. | UX17 |
| Validation messages such as `/expression: must NOT …` | Exposes validator wording before the user has entered values. | Explain the required correction in user language, associate it with the field and avoid an immediate page-level error for untouched input. | UX17 |

## 7. Execution, history, results and evidence

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Saved session / New session | Groups runs and cumulative spending across visits. The term can be confused with browser login or an individual run. | Explain its persistence and budget scope; show the selected session before Start. | UX21, UX22 |
| Start run; disabled state | Executes a saved definition, subject to readiness/input/access/budget constraints. The blocking reason is not always adjacent. | State what is missing and link to its correction; identify the exact revision to run. | UX03, UX18 |
| Stop run | Requests cancellation. Its placement under New run is disconnected from the active run. | Place beside active status and explain requested versus confirmed stop, preserving uncertain-command recovery. | UX18 |
| Pending/replay/withdraw controls | Recover ambiguous commands or pending local intent. Technical names can imply duplicate execution or cancellation of confirmed work. | Describe the actual next action and what is known; distinguish an unconfirmed request from a server run. | UX18 |
| Run status; failure reason | Execution lifecycle, not a quality verdict. Codes such as startup_failure lack useful recovery guidance. | Readable outcome, captured failure cause where available, partial result availability and next action. | UX19 |
| Run history buttons | Graph ID, status and short run ID distinguish entries poorly. Date/task summary and selected state are absent. | Clear selection and available revision; extend API for date/task metadata if needed rather than inventing it. | UX21 |
| More runs | Replaces the current page; wording suggests appending, and previous-page navigation is absent. | Honest Next/Previous paging or true accumulated loading. | UX21 |
| Result heading; draft/review outputs | Exposes internal node IDs and a sequence aggregate. Similar responses do not explain what the reviewer concluded. | Agent/step names, invocation context and aggregate versus final-result meaning. Show an explicit recorded verdict only if present. | UX19 |
| Formatted text / structured response | Readable content is useful. Nested rendering must preserve context and distinguish sibling fields. | Keep readable output with field labels, expansion and accurate source access. | UX19, UX20 |
| Original response · JSON | Currently reconstructed JSON, potentially altered by numeric parsing before rendering. | Label normalized data truthfully; preserve original captured source end to end where promised. | UX20 |
| Inspect run / technical event table | Begins with runtime events and host lifecycle, requiring implementation knowledge. | Agent activity first; event names, correlation IDs and host events in a technical view. | UX25 |
| View call / view content / missing or redacted evidence | Opens captured artifacts. Presence does not establish complete internal thought or causal influence. | Meaningful action labels, clear input/output/available-reasoning distinctions and explicit absence/redaction reasons. | UX19, UX25 |
| Inspector Close; keyboard behavior | Close exists and headings receive focus; Escape/return focus and covered background behavior are incomplete. | Choose modal or nonmodal semantics, then implement and test the complete keyboard lifecycle. | UX25 |

## 8. Component/resource catalogs, settings and budgets

| Current item | Meaning and comprehension problem | Proposed presentation | Findings |
| --- | --- | --- | --- |
| Component type/version, role, installation, operations | Catalog of registered implementations. Technical metadata does not explain what a type does or how to use it. | Purpose, capabilities, requirements and a configuration entry point; implementation identifiers in details. | UX13, UX26 |
| Add component instance | Advanced creation of an empty instance, separate from creating a step. It does not guide required configuration. | Guided creation from a type with defaults, required fields, capability bindings and explicit access decisions. | UX13 |
| Resource Retention / Namespace / Model profile | These fields are shown even on resource types where they do not apply. | Capability-specific summaries; use Not configured only for a relevant unset value, not inapplicability. | UX13 |
| Resource recorded activity | Shows observed use, not merely a configured connection. The distinction matters for analysis. | Separate Configured for these agents from Used in this run. | UX12, UX25 |
| Model inventory: provider/model/profile, supported options, defaults/maxima | Useful capability facts, scattered between settings and agent selection. | Show relevant support and effective defaults at model selection, with fuller catalog detail here. | UX08, UX11, UX23 |
| Tariff status; reviewed-until date | Determines pricing readiness. It does not verify credentials or provider availability. | Explain precisely what is ready, show a readable expiry/timezone and identify any unavailable price. | UX23 |
| Run deadline | Maximum overall run time under the platform policy. The relationship to individual calls is unclear. | “Maximum run duration”, scope and expiry behavior with readable units. | UX22 |
| Call deadline | Bounds an individual mediated call, not necessarily only an LLM request. | State which calls it covers and how it interacts with the run deadline. | UX22 |
| Startup / Shutdown deadlines | Bound component lifecycle operations. They compete with ordinary run controls despite being operational tuning. | Advanced execution limits, with examples of startup/shutdown failure. | UX22 |
| Maximum calls | Bounds admitted calls under the execution policy. Users may count agents or model requests instead. | Explain what counts, including mediated resource calls, and show usage when available. | UX15, UX22 |
| Maximum call depth | Bounds nested calls. It is different from total calls and repeated graph activations. | Describe a parent → worker → model example and the effect of exceeding the bound. | UX15, UX22 |
| Maximum payload bytes | Bounds communication size. Bytes are not tokens or visible character counts. | Show readable size units with exact bytes in detail and explain which messages are checked. | UX22 |
| Run / Session / Month budgets | Three cumulative scopes; ceilings and recorded spending are retained. A changed cap is not a spending reset. | Separate scopes visually, show current consumption/reservations/available allowance, currency, period and effective-change timing. | UX22 |
| Recorded / Pending / Limit amounts | Settled charges, reservations and cap. Long decimal values preserve small costs but require interpretation. | Explain pending reservations and show remaining allowance without rounding small charges to zero. | UX22 |
| Server ceiling; configuration revision | Limits edits and detects concurrent changes. Raw revision strings are secondary to the user's task. | Show the allowed range by field; keep version details available for recovery. | UX23 |
| Apply settings; Use latest server limits | Settings save is coherent, but the reset action reads the cached catalog rather than fetching fresh values. | Distinguish Discard edits from Reload server values; offer a clear conflict-recovery path. | UX23 |
| Settings errors / Replay unchanged settings command | Recovery protects against duplicate or uncertain changes, but generic error codes do not identify a correction. | Field-specific errors and an explanation that retry reuses the same operation. | UX23 |

## Cross-cutting comprehension requirements

For every editable field, a user should be able to identify **what it controls,
whose value it is, its effective/default value, what happens if it changes, who
else is affected, and whether it is saved**. For every execution display, the user
should know **which experiment revision, session, run and invocation it describes**.

Ordinary controls should neither require users to reconstruct Python call chains
nor pretend that all extensions share the same capabilities. A component may be
stateless, stateful, composed, shared or independent. The UI should obtain its
specialized behavior from explicit contracts, with complete advanced access.

Accessibility review remains partial. Native labels and fieldsets are useful;
full keyboard journeys, visible focus and return focus, validation announcements,
contrast, zoom/reflow and assistive technology testing still need dedicated
verification. This inventory makes no conformance claim.
