# Bounded conditional collaboration

Implementation contract for the first-cycle routing extension approved on
2026-09-29. The components and graph profile below are not yet implemented.
Existing finite Sequence definitions and result envelopes remain compatible.

## Component boundaries

| Package / type ID | Public functional class | MCP operation | Responsibility |
| --- | --- | --- | --- |
| `components/redirector` / `redirector` | `Redirector` | `route` | Run a configured deterministic Python selector and validate its declared output port. |
| `components/routed-call` / `routed-call` | `RoutedCall` | `invoke` | Invoke a normal worker and then a redirector through the platform. |
| `components/bounded-flow` / `bounded-flow` | `BoundedFlow` | `next` | Validate transition history and choose one next node, completion or exhaustion. |

Package version starts at `0.1.0`. Each is independently prepared and hosted using
the existing component installation contract and optional host SDK. No package
imports backend internals. All managed cross-component calls use the
[managed gateway](managed-gateway.md).

## Redirector

Configuration declares unique nonempty `outputs`, a JSON `input_schema`, and a
`selector` import reference such as `review_rules:choose`. The selector is packaged
in the exact installed environment and included in its locked artifacts; no file
path, source-code string or import reference arrives in invocation arguments.
Loading occurs during trusted component setup/description, not inside the backend.
Explicit preparation may take `--selector-project PATH` to include a user selector
project's wheel in the exact hashed installation closure. The bundled example
uses a public selector entry in the existing example package; its reasoning worker
still uses ordinary LLMCall.

The user function has the contract `choose(value: JsonValue) -> str`. For example:

```python
def choose(value: JsonValue) -> str:
    if not isinstance(value, dict) or not isinstance(value.get("accepted"), bool):
        raise ValueError("A validated review with accepted is required")
    return "accept" if value["accepted"] else "revise"
```

`route` accepts `{"value": ...}` and returns `{"port": "accept"}` for a declared
port. The public `Redirector.route(value)` applies the configured schema, calls
the selector once and validates the string result. Unknown ports, invalid input,
selector exceptions and non-string results are explicit errors, with no fallback
route and no repeat execution. The platform retains the failed invocation.

Determinism is a requirement on authored selectors, not a Python sandbox guarantee.
Selectors must not perform external calls; managed external work belongs in a
component using the gateway. A blocking or looping selector remains subject to
platform call/run deadlines and owned-process termination.

## RoutedCall composition

RoutedCall is a reusable composition, not reviewer-specific reasoning code.
Configuration declares `input_schema`, `worker_operation`, `worker_output_schema`,
`router_input_pointer` and `outputs`. Required resource slots are `worker` and
`router`. The backend checks their effective operations and permissions at preparation.

The bundled descriptor constrains the worker to role `agent` and the router to
role `resource`. These are descriptor constraints, not hardcoded Python-class
restrictions; another conforming registration can reuse the implementation with
a different worker-role constraint. This sprint adds no wildcard role semantics.

Its input is passed unchanged to the worker's declared operation. After successful
worker completion, extract `router_input_pointer` from the worker result and call
the router's `route` with `{"value": extracted}`. For a normal LLMCall reviewer,
`worker_operation` is `generate` and the pointer is `/value`.

Return `{"status":"succeeded","port":"accept","value":worker_result}`.
Keep the original worker envelope under `value`; no model-output fields disappear.
Failure of the worker, extraction or router produces an MCP error with stage and
reason, no eligible `port`, and no downstream activation. Do not retry either call.
Use the existing MCPError path with `data={stage, reason}`; ProcessOperation retains
that data in an error result. Successful operation schemas do not imply a separate
success-shaped error envelope. Redirector and BoundedFlow use the same explicit
MCP failure path for selector failures or invalid history.
The public `RoutedCall.invoke(arguments, invocation)` uses the bound normal MCP
client and validates the router reply against `outputs`.

The containing graph binds ports to destinations. The composition does not know
which graph node will receive its result. The reviewer remains an ordinary LLMCall
worker; the wrapper adds a deterministic routing responsibility after its one call.

## BoundedFlow controller

Configuration declares `entry`, `routes` and positive integer `max_activations`:

```json
{
  "entry": "propose",
  "routes": {
    "propose": {"next": "review"},
    "review": {"accept": null, "revise": "propose"}
  },
  "max_activations": 6
}
```

The value 6 is an example configuration, not a platform-wide fixed limit. Each
route maps a declared port to a declared node or `null` for successful completion.
Reject empty/unknown entries, destinations and port sets at configuration time.

`next` accepts `{"completed":[{"node":"propose","port":"next"}, ...]}`.
Validate the complete history from the configured entry, including the port of
each completed node. Return exactly one of:

- `{"action":"activate","nodes":["review"]}`;
- `{"action":"complete"}` when the last declared route is terminal;
- `{"action":"exhausted","reason":"activation_limit_reached"}` when the next
  activation would exceed the configured limit.

Evaluate a valid terminal route before exhaustion, so acceptance on the final
allowed activation succeeds. Invalid history is an error, not exhaustion. The
controller is stateless and makes no model calls. The executor independently
validates the returned decision before scheduling any operation.

## Graph and immutable execution plan

Add optional `execution_profile`; absence means the current `sequence` profile.
The new value is `bounded-conditional`. Its controller must have the BoundedFlow
configuration above, validated against the graph nodes. Add top-level `input_schema`
for declared run input and `result` for the final selected binding. Existing examples
derive their current `/problem` input schema when the optional field is absent.
The conditional `result` is a required `node_output` binding with a declared node,
`activation: "latest_completed"` and a JSON Pointer. It cannot be optional or a
literal/run-input binding. A terminal path must have a successful source activation
to publish that result; otherwise the run fails with an explicit binding error.

Conditional nodes add a required `output` selector, exactly one of
`{"constant":"next"}` or `{"pointer":"/port"}`. The selected value must be a
string in that node's configured controller ports. No normal result may silently
choose a default route after selection fails.

For conditional `node_output` input bindings, require
`"activation":"latest_completed"`. This resolves the most recent successful
activation of the named node strictly before scheduling the current activation.
Optional `"missing":"omit"` omits the argument only if that node has never
completed; a missing pointer in an existing output is still an error. Other
bindings remain required. Sequence does not gain these cyclic semantics.

Example feedback binding:

```json
{
  "source": "node_output",
  "node": "review",
  "activation": "latest_completed",
  "pointer": "/value/value",
  "missing": "omit"
}
```

Use new immutable definition records and a separate ConditionalProgram; do not
hardcode agent names or reinterpret SequenceProgram. Each scheduled activation
retains a unique identity, ordinal and exact source activation/payload references.
Record the selected port and the controller decision. Do not use a dictionary
keyed only by node name as the durable execution history.

Successful terminal output contains `status: "accepted"`, the declared selected
`value`, its source activation and total activation count. Exhaustion fails the run
with `activation_limit_reached`; retain all proposals and reviews but do not claim
acceptance. Budget, deadline, stop and recording failures use the existing outcomes.

## Containment and visible graph

Add optional instance field `contained_by` naming another configured instance.
Containment is presentation/ownership metadata only: it grants no permissions,
merges no state and makes no direct connection. Reject missing parents or cycles.
The main example displays proposer and reviewer, with review return and accept exit.
The review worker and redirector are inside the reviewer composition and may be
expanded. Their managed calls and individual evidence always remain inspectable.

## Example and acceptance

Provide one new bundled example with a task containing explicit requirements.
Configure proposer and reviewer prompts and model bindings independently. The
reviewer returns validated JSON with `accepted: boolean` and concrete `findings`.
The proposer receives the original problem, last proposal and latest findings
explicitly. The example selector examines the validated review; it adds no LLM call.

Test reject-then-accept, immediate acceptance, exhaustion, malformed reviews,
unknown ports, selector exceptions, nonterminating selectors, missing bindings,
stale invocation authority, stop/deadline/budget races and retained source identity.
No runtime graph mutation or arbitrary parallel scheduling is introduced here.
