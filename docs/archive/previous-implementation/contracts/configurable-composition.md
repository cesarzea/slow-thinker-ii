# Configurable agent composition

**S06-COMPOSE / 1 — 2026-10-03.** Owner-authorized S06 contract. Graph identity,
profiles, component preparation and mediated-call rules remain unchanged.

## Generic execution

Provide independently packaged composed-call@0.1.0 with worker(agent) and
extension(resource) bindings and public invoke operation. Functional ComposedCall
is separate from its Host. Config is a self-contained object declaring input_schema,
worker_operation, worker_output_schema, extension_operation,
extension_input_schema, extension_output_schema, phase(before|after),
arguments (named source/pointer bindings), worker_input, result and output.
Binding source is input, worker_output or extension_output as appropriate to phase;
worker_input and result select source/pointer. output is either {constant:string}
or {pointer:string,outputs:nonempty unique string[]} reading extension output.
Result is {status:"succeeded",port:<declared>,value:<selected result>}.

Describe validates bounded self-contained schemas/pointers/ports and returns the
effective input/result schemas without business calls. Invoke performs one worker
and one extension call in declared order through invocation-scoped managed MCP,
validates each reply and the selected port, never retries or invents a fallback.
Failures expose stage/reason while retaining previous paid-call evidence. Nesting
uses existing lifecycle/depth/call/time budgets; no internal graph engine is added.
Static preflight checks effective operation schemas and explicit grants against
the selected actual instances. Prefer generic descriptor-declared relations;
never add an external-component type-name special case.
Compatibility checks reject known nested type and required-property mismatches
with bounded traversal of supported local references. They are conservative for
ambiguous or unsupported schema constructs and do not prove general JSON Schema
subsumption. Runtime validation of each actual input and output remains mandatory.

## Component-owned attachment declaration

An attachable descriptor supplies extensions["slow-thinker:attachment"]:

```json
{
  "version": 1,
  "label": "Choose an output",
  "phase": "after",
  "operation": "route",
  "input_argument": "value",
  "arguments": {"value":{"source":"worker_output","pointer":"/value"}},
  "result": {"source":"worker_output","pointer":""},
  "output": {"pointer":"/port","outputs_pointer":"/outputs"}
}
```

For nonrouting transformations output may be {constant:"next"}. An attachment
may declare worker_input for before-worker transformations. The component config
and declared operation describe effective extension schemas. Arguments/mapping
defaults come from the component; the incorporation dialog lets the user choose
the received worker-result field. Configured resources remain explicit and are
not automatically injected. Only ready installed compatible operations appear.
Discovery normalizes optional attachment, with attachment_status and bounded warning;
frontend InstalledType exports ComponentAttachment and validates this shape.
The normalized wire keys are attachment (object|null),
attachment_status (declared|generic|invalid), attachment_warning (string|null), and
composition_host (CompositionHost|null). Omitted keys preserve old catalog clients.
The optional input_argument names the declared argument modified by the incorporation
dialog's input_pointer; do not infer it from a property named value.

The composer descriptor declares extensions["slow-thinker:composition-host"]
{version:1,protocol:"decorator-v1"}; discovery returns this optional declaration.
Platform selection uses this protocol, not a concrete type ID. More independently
provided hosts can implement a future protocol without type-name branching.

## Plan wire contract and source preservation

Authenticated POST /api/v1/definitions/composition accepts:

```json
{
  "source":"<exact graph draft>",
  "action":"attach",
  "agent_id":"proposer",
  "component_id":"proposer-router",
  "type_id":"redirector",
  "type_version":"0.1.0",
  "config_source":"<exact component config>",
  "resources":{},
  "input_pointer":"/value",
  "routes":{"propose":{"next":"review","revise":null}},
  "max_activations":6
}
```

Action is attach, replace or remove. remove uses source/action/agent_id/component_id
and optionally routes/max_activations to resolve restored worker ports explicitly;
replace supplies the attach fields for the selected current extension. routes and
max_activations are optional where the current controller already supplies the
necessary unchanged relationship. Unknown fields/invalid configurations fail 422
invalid_composition; unavailable catalog/installation fails 503. No persisted
changes, business invocation, spending reservation or authority grant occurs.
Trusted installed describe is bounded and side-effect-free. Response:
{base_source:string,operations:PatchOperation[],changes:string[],warnings:string[]}.
PatchOperation remains {op:"add"|"replace"|"remove",path:string,value_json?:string}.
Source and config strings preserve arbitrary JSON integers through the existing
Python exact-json boundary. Source/model/callable secrets never enter metadata.
Patch operations edit individual structural keys. Applying a patch preserves
untouched source substrings, including decimal tokens, string escapes and
whitespace; inserting a value preserves its validated `value_json` spelling.
Composition plans contain at most 100 operations, matching the existing ordinary
browser patch boundary. Standalone backend patches retain their separate bound.
An idempotent composition plan may return an empty operation list after validating
the exact base and refreshed enclosing contracts. The client closes an approved
unchanged plan without submitting an empty patch; standalone empty patches remain
invalid.

ConfigurationClient.composition(body:string,signal:AbortSignal):Promise<CompositionPlan>
is a public API export. CompositionRequest is the above discriminated contract;
CompositionPlan exports the response. SourceWorkspaceProps optionally receives
planComposition(request:CompositionRequest):Promise<CompositionPlan> through app.
App owns current operator authentication; no singleton credential is introduced.
Workspace passes the exact latest source, then compares plan.base_source before
staging returned operations. A mismatch requires replanning. Apply confirms listed
functional permissions; shared references/route loss require explicit resolution.

## Structural semantics and limits

Preserve outer agent/node/display IDs. Move the current functional component to a
collision-free contained worker ID, retain its exact config/resources and transfer
its outgoing grants. Move existing contained-child parent references coherently.
Create the new owned extension and explicit worker/extension grants. Update node
operation/output to the composer's invoke and /port. Prefix affected same-graph
node-result pointers with /value; preserve unrelated source and external extensions.
The controller receives explicit port destinations and activation bounds, including
constant-output attachments. Sequence
conversion preserves step order and requires user-confirmed branching/limit.
Block unsupported external callers with a useful explanation rather than silently
changing their operation or result contract. Replacement/removal lists affected
ports; removing restores the current contained worker and strips only the known
added envelope. Shared resources remain shared; no retained run is edited.
If removal or replacement leaves a port without a meaningful current destination,
require explicit routes in the plan request. A reference to an owned child from
another component blocks its removal until the shared reference is resolved.
The single added-envelope rebase also applies to an extension-selected result;
the installed resulting schema must still support every downstream selection.
If a transformation collapses or changes a nested shape so that selection becomes
unresolved, the preview names the affected node and pointer and blocks. This
contract does not include arbitrary downstream-pointer override requests or infer
an alternative mapping from similar schemas.

Retain minimal structural provenance in extensions["slow-thinker:composition"]:

```json
{
  "version": 1,
  "agents": {
    "proposer": {
      "worker_id": "proposer-worker",
      "extension_id": "proposer-router",
      "nodes": {"propose": {"operation": "generate", "output": null}}
    }
  }
}
```

Each node record stores its original operation and output selector. The selector
is {constant:string}, {pointer:string}, or null for an originally absent output.
No configuration snapshot is stored: current worker configuration, resources and
outgoing grants are authoritative on restoration. decorator-v1 adds one known
/value envelope. Removal strips exactly that leading segment from same-graph
references to recorded nodes; references selecting the new /port or lacking that
prefix block with an explanation. Replacement retains the owned extension ID and
journal. This record enables reversible composition without historical run edits.

Nested attachment moves the existing journal entry to the retained worker ID;
removal moves it back to the restored outer ID. When a retained conditional
controller requires an output selector, restore an originally implicit `next` as
an explicit constant `next` and list that normalization in the preview.
Only directly invoking nodes supply editable destinations in a nested replacement
request. Enclosing consumers retain their routes and bounds, shown in the preview.
Inner removal may strip one leading `/value` from an enclosing worker-output
mapping only when the journal proves that the removed layer created that envelope
and the rederived selection remains compatible. Every rebase is listed explicitly;
whole-envelope and ambiguous dependent selections block with an explanation.

After an inner removal, update only overlapping immediate-parent journal selectors
from that child's proven original node records. This permits a subsequent parent
removal to restore the current worker operation rather than a removed composition
operation. Unrelated node records, ancestor journals, current worker configuration
and active outer routes remain unchanged. Consecutive two/three-layer removals
must preserve these invariants.

After editing a composed worker, refresh its installed operation schemas using
`replace` with the same owned extension ID, type, configuration and resources,
against the exact locally edited source. Intermediate stale wrapper schemas do
not prevent that repair. Refresh enclosing decorator-v1 ancestors, then validate
the complete resulting source, including same-graph result pointers. Ordinary
dialog Apply stages local edits and refreshed plans together, validates the final
candidate, rechecks source freshness and applies one coherent patch.

Each installed description has at most five seconds, including installation
verification before and after the probe. The complete planning operation has a
50-second aggregate deadline, the serialized HTTP preview has 55 seconds, and
the authenticated client has 65 seconds. No planning work continues past its
aggregate deadline.

Whole-result schema selections retain their resource scope. Partial selections
retain a private source definition scope and rebase local references into it.
Partial selections crossing nested `$id` resource boundaries or dynamic references
are rejected with a composition explanation; general scoped-resource resolution
is outside this delivery. Configured source schemas remain exact and unchanged.

Provide external example.response-marker whose own descriptor/dialogs/configuration
and after-worker attachment add a configured prefix to a text reply while preserving
its envelope. It is packaged/installed as an external authored component; no
backend/frontend branch may mention its type ID. Also demonstrate the Redirector
attached to a preexisting ordinary agent and the existing reviewer feedback cycle.
