# ADR 0009: Export evaluated graphs as standalone Python programs

- Status: Proposed; recovered by the [scope review of 2026-10-06](../specification/scope-review-2026-10-06.md) and scheduled for S24, as readable, professional and reviewable code
- Recorded: 2026-09-27
- Decision-maker: Cesar Zea
- Requirements: R04–R06, R13–R16, R24, R27–R28
- Open questions: Q16, Q17, Q20, Q21

## Context and problem statement

The owner proposes a future Export as Python capability: export a complete graph as an independently executable, optimized Python implementation. The owner clarified that optimization primarily means removing platform logging, intermediation and supervision. This extends the experimentation process from defining, comparing and improving collaboration to deploying a selected variant outside the platform.

An exported program must preserve the graph's functional logic and identify its dependencies. Its execution profile deliberately excludes platform observation and supervisory behavior. Arbitrary custom components, external resources and dynamic control cannot be translated merely by serializing the graph or replaying a recorded execution.

## Decision drivers

Independent deployment, direct execution without platform overhead, readable generated code, exact component provenance, explicit portability, preserved functional logic and measured optimization.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Export graph JSON for the platform to execute elsewhere | Reuses the existing interpreter | Does not meet the requested Python implementation and platform independence |
| Generate Python control flow with direct calls and packaged components | Implements the requested standalone execution without platform logging, intermediation or supervision | Requires portable implementations and explicit separation of functional logic from platform services |
| Embed a local platform coordinator, policy checks and logging | Retains platform supervision | Reintroduces the overhead the owner explicitly wants removed |
| Generate an unrestricted Python translation of every possible extension | Appears to offer universal export | No general translation exists for arbitrary implementations and platform-only services |

## Decision outcome

The selected export direction is generated Python control flow with direct component/provider calls, without platform logging, intermediation or supervision. The detailed generator and portability contracts remain proposed. The output must not submit work to the platform or embed a replacement platform supervisor. Develop the export capability in a later functional cycle; first-cycle execution remains unchanged.

Preserve a domain model independent of UI, database and application server code now. The exporter can later consume a resolved execution representation; its exact form remains Q21. Start export support with finite sequences and portable Python components, then expand the supported profile explicitly.

### Standalone artifact

Recommend a readable Python project containing an entry point, generated control flow, required component implementations or pinned installable packages, configuration templates, dependency locks and usage instructions. Record the source graph revision, component/base resolutions, exporter version and optimization profile as build metadata; this does not require runtime logging.

The artifact must run without the Slow Thinker II application, backend, database, orchestration service or monitoring infrastructure. Include only functional component code and necessary standalone dependencies. Python, model SDKs, external provider access and configured resource services may still be required. Resolve secret references in the deployment environment; never copy platform credentials or historical payloads into the export by default.

### Complete graph and extension portability

Export every reachable functional behavior permitted by the supported graph definition. A historical trace is evidence for validation, not a replacement for branches, loops or dynamic decisions. When dynamic profiles become exportable, retain their decision logic and required component resolution; do not flatten one observed path into the entire program. An agent or controller performing a functional supervision role within the graph remains part of the program; platform execution supervision is removed.

Check the complete component and resource dependency closure, including inherited code and state requirements. Each extension needs a portable implementation, an explicit external-service dependency or a supported export adapter. Components in other languages may require packaged subprocesses or external services; a Python entry point does not make their implementations Python.

Report unsupported components, unavailable artifacts and platform-only dependencies before producing a successful export. Do not silently omit nodes, state, side effects or control paths. An export profile may require a deliberate graph change, but that change creates a new variant for evaluation. Exportability remains an optional capability of extensions and does not restrict the platform's general component model.

### Direct execution without platform services

The existing platform keeps central mediation and supervision for its own executions. The standalone export is a distinct execution profile, explicitly selected by the owner. Generated code calls Python components directly and configures familiar model clients to call their providers directly. External resources that require MCP or another protocol are contacted directly through that protocol, without a platform proxy.

Remove platform logs, trace/event collection, monitoring callbacks, proxy routing, permission-admission checks, watchdogs, stop supervision, cost accounting and budget enforcement from this profile. Do not reproduce those services in generated wrappers or a bundled coordinator. The exported program has no platform session/month ledger and makes no claim to enforce platform budgets or execution deadlines.

Preserve prompts, input/output transformations, configured model options, functional memory/resources, ordering, branches and functional error handling. Data validation or decision logic belonging to a component's declared function remains executable. Generate the scheduling necessary to express the graph itself, without a platform orchestration service. Preserve state separation where it affects results.

Component design must keep functional work separable from instrumentation and platform client configuration. The export adapter removes instrumentation and binds direct clients. A component whose functional result requires an unavailable platform service needs an explicit portable implementation or is reported as unsupported.

### Optimization and verification

The primary optimization is elimination of platform logging, mediation and supervision. Supporting optimizations include specializing known control flow, pre-resolving component bindings and omitting application UI/storage dependencies. These changes must not reintroduce a miniature platform around direct calls.

Changing prompts, models, context, functional memory, LLM call counts, meaningful ordering or component-level retry semantics changes the experiment and requires a new evaluated variant. Caching, batching, parallelization and process co-location require individual functional review. Removal of platform instrumentation and supervisory intervention is already part of the selected export profile.

Use deterministic component/provider fixtures to compare functional requests, data flow, outputs, side effects and component error handling on paths where platform supervision does not intervene. Separately verify the deliberate absence of platform logging, proxy calls and supervisory checks. Cases stopped only by platform budgets or watchdogs are intentionally different, not evidence of full execution equivalence. Evaluate real model outputs statistically where appropriate; identical text is not a valid general promise. Benchmark overhead, deployment requirements and resource use without promising lower model charges when model calls remain the same.

## Consequences

The experiment platform can produce independently deployable applications with inspectable build provenance and direct execution. This requires portable functional components and verification that distinguishes preserved graph logic from deliberately removed platform services. Exported code should meet the project's applicable engineering gates. Coverage grows by supported execution profile, rather than by claiming automatic translation of arbitrary extension code.

## Confirmation

Before implementing export, close Q21 and approve a concrete output project and supported-capability matrix. Verify execution with the platform unavailable, direct calls, absence of platform logging/intermediation/supervision, explicit external dependencies, rejection of unsupported graphs, exact dependency provenance and functional comparisons under deterministic fixtures. Measure optimization claims. No exporter or performance evidence exists yet.
