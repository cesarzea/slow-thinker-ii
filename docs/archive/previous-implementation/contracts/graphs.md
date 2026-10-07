# Graph contract

**Status: Approved first-cycle contract.** R01–R04, R09–R10, R16–R19, R24; [ADR 0005](../../../adr/0005-versioned-contracts.md).

## Proposed domain structure

| Field | Meaning |
| --- | --- |
| `schema_version` | Exact graph contract version, initially `0.1-draft`. |
| `graph_id`, `revision` | Definition identity and immutable semantic revision. |
| `derived_from` | Optional exact parent definition reference for manual variant lineage. |
| `components` | Configured instances pinned to type/version, configuration and resource bindings. |
| `controller` | A component and operation responsible for control decisions. |
| `nodes` | Component operations and explicit input bindings. |
| `permissions` | Allowed managed calls between configured components. Unlisted calls are denied. |
| `limits_profile` | Reference to an approved policy; actual configurable values are resolved at admission. |
| `extensions` | Explicit metadata extension point. |

The [review-cycle example](examples/review-cycle.graph.json) uses proposer, reviewer, model resource and sequence controller instances. Three nodes refer to two agent identities. Configured resources and controllers are not counted as extra reasoning agents.

The [initial example set](examples/README.md) also includes a single agent, a two-agent handoff and two rounds of review. S03 adds JSON import/edit and immutable personal definitions alongside these bundled graphs. Every definition uses the same graph schema and supported execution profiles; the [personal experiment guide](../personal-experiments.md) describes authoring and execution.

## Control policy

The illustrative controller is a component exposing `next`. Its configuration contains an ordered `steps` list. The proposed request contains completed node IDs; its output is either `schedule` with one eligible node or `complete` with no nodes. Platform validation constrains the controller's choices and retains sole dispatch authority.

This is the **initial sequence profile**, not a universal workflow language. It must reject branching, repeated node IDs, cycles, parallel scheduling and mutation requests under this profile. Reusing a component in distinct nodes remains valid. Other controller profiles can support different topology without imposing this sequence rule on the entire platform.

The owner added a separate bounded conditional review profile to the first cycle on 2026-09-29. It combines ordinary LLMCall agents with a redirector usable independently or embedded in an agent. Declared outputs and a user-authored Python script determine routing. The [conditional routing contract](conditional-routing.md) defines the delivery sprint's composition, repeated-activation bindings and stop/error behavior. This scope addition does not change Sequence semantics or claim that cycles are already executable.

The semantic model of arbitrary transitions, events, joins, and dynamic mutation remains future-cycle Q16. Q13 must approve the initial generic boundary and finite-sequence contract without implementing those later mechanisms. The candidate schema does not claim future control behaviors are implemented by accepting extension metadata.

## Inputs

Each argument binding is one of:

- `literal`: an explicit JSON value.
- `run_input`: a JSON Pointer into the separate execution input.
- `node_output`: a JSON Pointer into an earlier node's result.

Bindings are data, not executable expressions. Missing pointers are validation/execution errors, never empty strings silently inserted into a prompt. Input payload compatibility is checked against the target operation schema once values are available.

In the example, the reviewer receives `/problem` and the draft's `/value`; revision receives both plus the review's `/value`. LLMCall success envelopes expose text or structured JSON at `/value`; failure envelopes never become successful bindings. Validate resolved inputs against each instance's configured effective schema. The supplied [input fixture](examples/problem.input.json) is separate from the graph. Future looping controllers must define which activation a reference means; a node ID alone is insufficient in that case.

## Permissions and resources

Graph approval permits the runtime to invoke listed node operations and the selected controller. Component-originated nested calls require explicit `permissions`. Binding a resource slot does not itself grant invocation permission.

The example permits proposer and reviewer to invoke only the model resource's `complete` operation. It does not give them general access to the trace, other graph definitions, or arbitrary platform operations.

## Revisions, state and layout

An admitted run retains the exact graph revision, resolved component descriptors, effective limits and input. Runtime changes are later functionality and must create attributable revisions rather than modifying history. Semantic variants and screen-layout changes are distinct; layout is stored outside this domain schema.

Fresh run state is the default. Persistent resources require explicit bindings, lifecycle policy and provenance. Shared state must be visible in comparisons because it can affect outcomes.

## Future standalone export

[ADR 0009](../../../adr/0009-standalone-python-export.md) proposes compiling a complete supported graph revision to a standalone Python application with direct calls. The selected profile removes platform logging, intermediation and supervision, including platform budget enforcement and watchdogs. It preserves functional control/data flow, resolved component/base versions and required resources. A successful export cannot silently omit functional behavior or substitute one historical trace for the graph definition. Export capability metadata and generated formats remain Q21; the current graph schema is unchanged.

## Semantic validation checklist

- Resolve all instance/type/version and operation references; validate each instance configuration.
- Ensure the controller has the control role and the executor supports its precise profile.
- In the sequence profile, include every node exactly once and prohibit output references to later nodes or self.
- Validate required resource slots, referenced roles and corresponding invocation permissions.
- Reject permissions naming unknown callers, targets or operations; define duplicate-rule behavior before implementation.
- Resolve real provider, installation and limit profiles; reject unknown or unbounded billable configurations.
- Freeze effective inputs and policies before side effects; validate resolved invocation shapes before dispatch.

Schemas cannot establish these cross-reference or behavioral properties alone. The [open questions](../specification/open-questions.md) identify the unresolved contracts needed for executable admission.

## S03 personal definitions

The [personal experiment library](personal-experiments.md) extends selection with
JSON import/edit, immutable saves and manual lineage using this same graph schema.
Its static validation boundary is distinct from installed runtime preflight.
