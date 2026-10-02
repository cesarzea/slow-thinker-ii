# First-cycle contracts

**Status: Approved first-cycle baseline; local implementation verified.** The schemas and bundled definitions describe the local implementation. Example credentials, rates and installation identities are deliberately absent; runnable packages live under `components/`. See the [verification record](../verification.md) for evidence and limits.

| Contract | Purpose | Review artifacts |
| --- | --- | --- |
| [Components](components.md) | Types, operations, configuration, resources, state and concurrency | [Manifest schema](schemas/component.schema.json); [LLMCall](examples/llm-call.component.json), [derived reviewer](examples/grounded-review.component.json), [model](examples/model.component.json), [controller](examples/sequence.component.json) |
| [LLMCall](llm-call.md) | Configurable single model invocation and explicit output validation | [Configuration](schemas/llm-call-config.schema.json); [results](schemas/llm-call-result.schema.json); [text](examples/llm-call-text.config.json) and [JSON](examples/llm-call-json.config.json) configurations |
| [Initial OpenAI profile](openai-initial-profile.md) | Low-cost model, request/response/error matrix, cache accounting and conservative reservation | Reviewed low-cost profile, capacity-based reservation and preserved native results |
| [Python component API](python-component-api.md) | Public types, invocation and inheritance hooks | [GroundedReview code specimen](examples/grounded-review.md) |
| [Registration and installation](component-installation.md) | Trusted classes, isolated locked environments, explicit updates and independent launch | [Registration schema](schemas/python-registration.schema.json); [base](examples/llm-call.registration.json) and [derived](examples/grounded-review.registration.json) examples; [offline packaging evidence](../evidence/packaging-review-20260928.json) |
| [Component lifecycle](component-lifecycle.md) | Startup, readiness, invocation reuse, nested calls and owned-process teardown | Proposed host states and failure cases |
| [Call authority](call-authority.md) | Per-invocation identity, permissions, causal context and revocation | Proposed admission path and authorization cases |
| [Graphs](graphs.md) | Instances, node operations, control policy, input references and permissions | [Graph schema](schemas/graph.schema.json); [five bundled examples](examples/README.md); [run input](examples/problem.input.json) |
| [Conditional routing](conditional-routing.md) | Packaged deterministic selectors, composed agents and bounded feedback | [Proposer–reviewer example](examples/bounded-review.md) |
| [Managed MCP gateway](managed-gateway.md) | Invocation-scoped outgoing calls, filtered discovery and optional reports | Host SDK and ordinary MCP/LangChain clients |
| [Inspection projections](inspection-projections.md) | Exact definitions, distinct activations, relationships and reported evidence | Structure/Execution views and linked inspectors |
| [Execution and evidence](execution.md) | Lifecycle, accounting and event provenance | [Event envelope schema](schemas/event.schema.json); [event example](examples/run-started.event.json) |
| [Accounting policy](accounting-policy.md) | Currency/periods, exact amounts, tariff revisions and settlement | Ten worked acceptance cases; [storage transaction proposal](../adr/0011-local-persistence.md) |
| [Observation](observation.md) | Event catalog, payload provenance, capture failures and analysis boundaries | Proposed required fields; existing envelope remains illustrative |
| [Operator API](operator-api.md) | Browser commands, durable receipts, recovery, projections and inspection | Authenticated routes, durable receipts, bounded projections and browser inspection |
| [MCP profile](mcp-profile.md) | Protocol revision, transports, identities and supported features | Profile proposal; partial SDK feasibility evidence, full conformance pending |
| [SDK feasibility](sdk-compatibility.md) | Tested client/transport candidates and concrete compatibility gaps | Captured temporary probe results; full platform conformance pending |

## Validation levels

1. Parse JSON and reject malformed or unsupported schema versions.
2. Validate structure with [JSON Schema 2020-12](https://json-schema.org/draft/2020-12).
3. Resolve component types and validate their configuration and operation schemas.
4. Check graph semantics, permissions, input references and supported execution profiles.
5. Resolve real installation, provider and limit profiles and perform execution admission.

Fixture validation covers levels 1–4; production preparation and admission also resolve level 5. Installed acceptance checks exercise the actual isolated environments. Successful fixture validation alone does not establish MCP interoperability, persistence correctness, or runtime behavior.

## Extension and compatibility rules

Core objects reject unknown fields. Explicit `extensions` objects reserve namespaced metadata; component `config` is validated by its exact manifest version. An extension's presence does not authorize execution or imply runtime support.

Schemas refer only to local definitions or explicitly registered schema URNs from this package. Resolve these through a trusted local registry; the runtime must not fetch arbitrary schema references from the network. User-supplied input/output schemas in the initial LLMCall profile use local fragment references only. Artifact schemas are application contracts, not replacements for the authoritative MCP protocol schemas.

Changing meaning requires a new contract revision and compatibility review. No automatic migration behavior has been approved. See [ADR 0005](../adr/0005-versioned-contracts.md) and [Q13](../specification/open-questions.md).

The [personal experiment library](personal-experiments.md) defines the authorized
S03 authoring, immutable revisions, validation, paging and operator/client boundary.

## S04–S06 active contracts

- [Model resources](model-resources.md): provider-neutral calls and reviewed tariffs.
- [Tools and memory](tools-memory.md): deterministic tools, scoped storage and composition.
- [Product workspace](product-workspace.md): configuration discovery, structured editing and safe settings commands.

Implementation and mandatory local verification are complete. The
[delivery block](../specification/s04-s06-delivery.md) maps acceptance to evidence;
owner review and hosted verification remain separate publication checkpoints.
