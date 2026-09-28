# LLMCall contract

**Status: Proposed detailed contract.** The owner accepted text or schema-validated JSON output and a structured failure retaining invalid output, with no implicit repair call. References: R02, R08, R11–R14, R27, R29; Q13, Q20.

## Responsibility and identity

`LLMCall`, type ID `llm-call`, performs one logical model invocation per activation through its bound model resource. Instructions and inputs determine its role. Proposer, planner and reviewer are configured instances of this type, not separate implementations. The example release `0.1.0-example` is a review fixture, not an installed package.

The [descriptor](examples/llm-call.component.json) exposes `generate`. The [Python interface](python-component-api.md) defines the proposed code extension points. The component is stateless: input history is supplied explicitly, no conversation is retained, and the instance configuration is immutable during a run.

This describes the initial single-call component, not a required base class or algorithm for all agents. Components that use memory, invoke tools or coordinate several model calls can expose their own operations and resource bindings. Inheritance and composition remain available; adding such behavior must declare its execution policy rather than silently change LLMCall's one-call contract. Managed resource calls still pass through the platform.

## Configuration

| Field | Meaning |
| --- | --- |
| `instructions` | System instructions for this instance. |
| `input_schema` | JSON Schema for the named argument object accepted by `generate`. |
| `parameters` | Explicit, supported native generation options. An empty object uses the resolved model profile defaults. |
| `output.format` | `text` or `json`. |
| `output.schema` | Required for JSON; forbidden for text. The schema can describe any JSON value. |

The graph binds the required `model` resource slot. Its resource instance selects provider/model; the effective provider settings and invocation options are recorded with the run. Routing aliases used by familiar clients resolve to this binding, not to arbitrary provider access.

The owner selected a very inexpensive OpenAI model for the first cycle. The [initial provider profile](openai-initial-profile.md) proposes GPT-6 Luna and records current price evidence; account access, request mapping and billable bounds remain unverified.

See the [configuration schema](schemas/llm-call-config.schema.json), [text configuration](examples/llm-call-text.config.json) and [JSON configuration](examples/llm-call-json.config.json). These fields are configuration, not additional mandatory arguments added to the usual model-client call.

Validate configured input/output schemas themselves before admission. Input has an object root; output schemas use object-form JSON Schema declarations and may describe scalars, arrays or objects. Support JSON Schema 2020-12 with local fragment references only in user-supplied schemas; reject remote references instead of fetching them. Size/complexity limits remain Q18.

Reserved client/routing fields cannot be supplied through `parameters`: `model`, `messages`, `stream`, `response_format`, `n`, `base_url`, `api_key`, `timeout` and `max_retries`. The component requests one non-streamed response. Unsupported generation options fail before dispatch; adapters must not discard them. The exact supported model option matrix remains Q04.

## Effective operation schemas

The reusable type descriptor declares an object input and a stable result envelope. On binding an instance, validate and specialize its effective `generate` input schema from `input_schema`. Specialize the success branch of its output envelope from the configured format/schema. Resolve trusted package schema references locally and expose complete effective schemas through the instance's graph-scoped MCP capability.

Discovery and caches must include instance identity and configuration revision; two differently configured instances must not share an incorrectly cached schema. The platform validates effective contracts independently of component claims. The failure branch remains available without being checked as a successful `value`.

## Default message construction

1. Validate the resolved argument object before calling the model.
2. Produce a `system` message with `instructions`.
3. In JSON mode, append a second `system` message containing the following fixed instruction and the serialized output schema: `Return exactly one JSON value conforming to this schema, with no surrounding text:` followed by a newline and the schema.
4. Produce a `user` message containing the serialized argument object.

Serialize these objects as UTF-8 JSON with sorted keys, compact separators, preserved Unicode and finite numbers. JSON property names are preserved. There is no expression evaluation or implicit insertion of prior activations, traces or thinking into messages. A subclass may implement a different documented message builder.

The initial JSON mode requests a textual JSON response and validates locally. It does not claim native structured-output support from every model provider. A future native enforcement mode must be explicit and capability-checked. Save the actual messages sent so that the output instruction is visible in the trace. Unsupported message roles/providers remain part of Q04's compatibility checks.

## Success and failure

The [result schema](schemas/llm-call-result.schema.json) defines these outcomes:

```json
{"status": "ok", "format": "text", "value": "A proposed solution."}
```

```json
{"status": "ok", "format": "json", "value": {"summary": "Review", "citations": []}}
```

Graph bindings read successful content at `/value`, with deeper pointers for structured values. Validate JSON output against the configured schema before exposing success. Text output is returned unchanged; no automatic whitespace trimming.

| Error code | Trigger |
| --- | --- |
| `invalid_json` | The entire received text is not one valid JSON value. Reject surrounding prose, fenced JSON, duplicate object keys, non-finite numbers or incomplete JSON. JSON whitespace around a value is allowed. |
| `output_schema_mismatch` | Parsed JSON fails the configured output schema. |
| `output_validation_failed` | A derived component's additional output checks reject the result. |

Each validation failure contains `message`, the exact received model text in `raw_output`, and non-empty `issues` with JSON Pointer `path` and a diagnostic message. Parsing failures use the root path. Diagnostic wording is informative, not a stable machine key. See [invalid JSON](examples/llm-call-invalid-json.result.json), [schema mismatch](examples/llm-call-schema-error.result.json) and [derived validation failure](examples/grounded-review-reference-error.result.json).

Mark the MCP tool result as an error and expose the structured failure, not a successful output binding. The sequence executor stops on this unhandled failure. Retain the original received text before any subclass transformation; preserve the provider response and available usage as call evidence under the recording/retention contract. Validation failure does not cancel the cost of a completed provider call.

No automatic repair, schema coercion or second LLM call is performed. Additional repair/retry work requires an explicit policy and a separately recorded and budget-authorized attempt. Client and provider-adapter retries must not silently bypass that policy. The first reference behavior uses one attempt. The general retry configuration remains Q08.

Routing, provider, transport, refusal, incomplete-response and missing-text failures are model-operation failures, not empty strings or JSON validation failures. The [initial provider matrix](openai-initial-profile.md#response-preservation-and-functional-interpretation) proposes checks before text parsing, including rejection of a token-limited response that happens to contain valid JSON. Their wire envelopes remain Q04/Q08; the result schema here covers complete model responses and their validation. The [SDK review](sdk-compatibility.md) provides limited client/mock evidence; LLMCall execution and live provider behavior have not been tested.

## Separation for standalone export

Message construction, parsing and domain validation are functional code. Client endpoint binding, logging, event collection and platform supervision are separate. The future direct export retains functional validation while removing platform instrumentation and mediation, as selected in [ADR 0009](../adr/0009-standalone-python-export.md).
