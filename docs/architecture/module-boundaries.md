# Source organization and module boundaries

**Status: Accepted first-cycle layout; implementation and automated boundary checks are in progress.** R02, R05, R21–R22, R27–R28; Q14, Q17, Q20. The engineering obligations in [ADR 0001](../adr/0001-engineering-baseline.md) are accepted. The current implementation and verification limits are recorded in the [verification record](../verification.md).

## Repository layout

```text
backend/
  src/slow_thinker_ii/
    contracts/       shared boundary values and error identities
    definitions/     graph/component validation and immutable snapshots
    execution/       lifecycle and scheduling rules
    access/          permission and caller-context rules
    accounting/      money, reservations and settlement rules
    observation/     evidence envelopes and capture rules
    application/     coordinated use cases and transaction ports
    adapters/        HTTP, MCP, process hosting and SQLite implementations
    bootstrap/       configuration and dependency composition
  tests/
    unit/
    contract/
    integration/
frontend/
  src/
    app/             routes, composition and cross-feature selection
    features/
      sessions/
      experiment-selection/
      execution/
      graph-view/
      inspector/
    api/             validated application API boundary
    ui/              reusable presentation without experiment logic
  tests/
    integration/
    journeys/
components/
  llm-call/src/slow_thinker_llm_call/
  sequence/src/slow_thinker_sequence/
  openai-model/src/slow_thinker_openai_model/
examples/
  grounded-review/src/example_grounded_review/
tooling/             repository verification and fixture checks
docs/                architecture, contracts and review artifacts
```

Component and example packages also own their package metadata, tests and resources. The existing `slow_thinker_llm_call` and `example_grounded_review` entry-point names are preserved. The backend, controller and provider packages use these names in their development installations; production environment preparation is tracked separately. Each independently launched component is an installable package; sharing this repository does not allow importing backend internals.

The initial schema/graph fixtures remain under `docs/contracts` while under review. At implementation setup, designate one canonical location per contract and reference or generate from it; do not maintain separate manually synchronized copies in backend, frontend and documentation. No files are moved by this proposal.

## Backend dependency direction

| Module group | Permitted production dependencies within the backend | Forbidden dependencies |
| --- | --- | --- |
| `contracts` | None | Domain services, application, adapters, bootstrap |
| `definitions`, `execution`, `access`, `accounting`, `observation` | Public `contracts` values and each module's own internals | Sibling domain internals/services, application, adapters, frameworks/provider SDKs |
| `application` | Public APIs of the domain modules and contracts | Concrete adapters, bootstrap, framework/provider/storage types |
| `adapters` | Public application ports and domain/contracts values needed for translation | Other adapter internals or bootstrap |
| `bootstrap` | Public factories/APIs needed to construct the application | No incoming production imports from other modules |

Domain modules own their rules and expose narrow public operations. The application coordinates them: for example, a call-admission use case combines access, execution and accounting inside one transaction, then hands the saved dispatch intent to an injected transport port. Domain accounting does not call the scheduler or write observation storage directly. This prevents a cycle between routing, lifecycle and charging.

Keep shared `contracts` limited to identities and immutable boundary values required by multiple modules. It must not become a collection of generic helpers, mutable registries or unrelated models. Module-specific types stay with their owning module; mappings at the application boundary are preferable to exposing private objects.

External I/O belongs in adapters or independently hosted resource components. The backend's MCP adapter invokes the approved OpenAI resource operation; it must not also instantiate a second provider client that bypasses that component. SQL and FastAPI types stay inside their adapters. Dependency injection occurs in bootstrap; core modules cannot discover or construct concrete adapters themselves.

The application transaction port coordinates repositories under one unit of work. An adapter must not commit each repository independently when a use case requires atomic reservations/state/evidence. Nor may the application keep that transaction open while awaiting a provider. These boundaries implement the [storage proposal](../adr/0011-local-persistence.md), not a generic dependency-injection framework.

## Public entry points and encapsulation

Each Python capability exposes its supported symbols through a small explicit package entry point. Cross-module imports use that entry point; paths to `_internal` modules or implementation classes are forbidden. Export lists must enumerate symbols rather than re-export everything. Importing a public module cannot launch hosts, contact providers, open databases or change global configuration.

Each frontend feature exposes named exports through its public entry point. Feature internals are private. `app` composes features through typed data/callbacks; a graph view does not import inspector internals to manipulate its state. `ui` contains reusable presentation, not budget policy or backend transport logic. The `api` boundary validates external data before domain-facing use; unchecked casts and `any` are not substitutes for validation.

State belongs to an instance/use case or an explicit persistence scope. No mutable module-global run, current caller, provider client with switched authentication, or budget balance. Read-only constants are allowed. Configuration is resolved at composition/admission and passed explicitly; domain code must not look up environment variables during an operation.

Component packages expose their own operations and extension hooks. A derived reviewer may import `LLMCall` through `slow_thinker_llm_call`; it cannot import its private implementation. Tools, memory and future collaboration components need not inherit from that class. Functional component code must remain separable from hosting/observation so the future standalone export does not inherit platform supervision accidentally.

## Directory and size rules

- Every production file belongs to a declared package/capability in the repository's location manifest. A root-level source file or new catch-all directory fails verification until its responsibility and allowed dependencies are declared.
- Keep files, functions and complexity within the mandatory README limits. Split by cohesive responsibility; moving pieces to an unrelated `utils`, `common`, `misc` or `helpers` package merely to satisfy a line limit is not acceptable.
- Do not create empty placeholder packages for future features. For an agreed milestone, create and review the required public interfaces before their implementation; incomplete operations must fail explicitly.
- Runtime code cannot import test/example/tooling modules or development-only dependencies. Build output, local stores, credentials and downloaded environments do not belong in source packages.
- Generated code and integration adapters have no automatic exemption from the engineering rules. Generation must produce conforming units; a necessary exception requires the existing reviewed-ADR procedure.

## Module documents and implementation workflow

The current approved process is [M06](../continuous-improvement/methods/006-delivery-preparation.md).
It adds precise dependency handoffs, acceptance evidence for review and shared test
readiness to the phases below. Apply those requirements in the existing module
documents and tickets; no additional documentation hierarchy is required.

Each module owns its documents in its directory. A module is a declared capability,
frontend feature or independently packaged component, not every organizational
folder. Keep one set at its ownership boundary, alongside its public entry point
or at the component package root.

| File | Responsibility |
| --- | --- |
| `readme.md` | Brief purpose, boundaries and how to use the module. An existing `README.md` fulfils this role; do not create a second copy. |
| `specification.md` | Responsibilities, public interfaces and types, dependencies, inputs/outputs, state, errors and acceptance criteria. Link shared contracts rather than copying them. |
| `todo.md` | Current implementation ticket: concrete pending changes, constraints, affected interfaces and completion criteria. No completed tasks or work diary. |

Define the complete sprint through delivery before launching development. Cover
the agreed delivery objective end to end: affected modules, contracts, tasks,
dependencies, owners, testing scope and acceptance criteria. Keep the final project
objectives in view without extending the agreed sprint scope. Prepare documents
across all affected modules, not one complete module at a time:

1. Write or update all brief `readme.md` files to establish responsibilities.
2. Write or update all `specification.md` files and reconcile their contracts.
3. Write all needed `todo.md` tickets with concrete work and completion criteria.
4. Review new public interface skeletons before launching their implementation.

Distinguish intended behavior from implemented behavior. The local
specification cannot silently override an accepted shared contract; resolve any
disagreement in the owning contract before continuing dependent implementation.

Keep the phases distinct:

1. **Analysis, specification and tasks:** the coordinator resolves the complete
   sprint's design and feasibility questions and prepares the documents above.
   Specify observable behavior and public contracts; leave internal implementation
   choices open where they do not affect those contracts. Include test ownership
   and acceptance criteria before development starts.
2. **Development and delivery:** assign one or more complete components or packages
   to each implementer, grouping by cohesion, dependencies and workload. Delegate
   independent assignments in parallel with exclusive ownership. Implementers work
   against the prepared contracts
   and report deliveries and unresolved issues. Do not repeatedly reopen the
   architecture or alternate development with functional test implementation and
   execution. Keep delivery receipts brief rather than reviewing the whole system
   again for every completed module.
3. **Review and corrections:** after the deliveries, review each implementation
   against its specification, ticket and engineering rules, and review the whole
   result's interactions and failure paths. Group necessary corrections into module
   tickets, implement them in parallel where independent, and review the corrected
   result. Repeat until the complete sprint appears ready for testing.
4. **Testing:** finalize test tickets from the planned scope and implement module,
   integration and end-to-end tests, in parallel where independent. Run verification,
   analyze results together, write correction tickets, apply corrections and add
   missing tests, then repeat relevant verification. Finish only when acceptance
   criteria and all mandatory checks pass. Apparent coherence permits entering
   this phase; it does not establish correctness or completion.

The coordinator owns architecture, shared-contract decisions and whole-system
review. Each implementer receives the common engineering rules, local module
documents, relevant code, dependency contracts, and brief context about purpose
and failure consequences. The full conversation history is unnecessary. Use whole
components or packages as assignment units; their file boundaries record exclusive
ownership. Give shared files an explicit owner. Non-overlapping deliveries require
no separate merge phase. Whole-system review and subsequent
integration tests must still verify that modules work together.

Report ambiguities to the coordinator rather than inventing cross-module decisions.
Resolve blocking contract issues before affected work continues. Update only the
affected specifications and tickets; a local correction does not automatically
reopen the whole sprint. Do not weaken verification gates or repeat broad
verification without a relevant change or unresolved concern.

Evaluate the method per sprint using elapsed time to verified functionality,
rework, integration defects and available resource usage. Distinguish measurements
from estimates; code volume and worker count do not demonstrate efficiency.

Update `todo.md` as work advances. Remove an item only when its completion criteria
are met; keep outstanding verification as pending work. Delete the file when no
items remain. Its absence means no recorded pending ticket, not proof that the
module implements every future capability. Keep `readme.md` and `specification.md`
current; code, tests and affected documentation belong in the same completed change.

## Verification obligations

| Deliberate violation | Required rejection |
| --- | --- |
| Accounting imports FastAPI, SQLite or a provider SDK | Backend dependency contract fails. |
| Execution imports an accounting implementation directly | Sibling domain-boundary check fails; coordination belongs to application. |
| Application constructs a concrete adapter | Dependency-direction check fails. |
| A caller imports a private module of LLMCall or a frontend feature | Public-entry-point check fails. |
| Two frontend features import one another | Cycle/feature-boundary check fails. |
| Production imports a fixture or development-only dependency | Dependency classification check fails. |
| A source file appears outside an approved capability | Location-manifest check fails. |
| A generated or handwritten unit exceeds the size/complexity limits | The applicable existing gate fails; no path-based blanket exemption. |

Use Import Linter for Python dependency contracts and dependency-cruiser for TypeScript boundaries, with a separate location-manifest check for file placement. Tool configuration must demonstrate these failures; naming tools in this document is not enforcement. Remaining type, lint, dead-code, test, security and process gates retain the full [README baseline](../../README.md#engineering-standards).

Q14 must approve this layout and the single verification entry point before implementation setup. Q17/Q20 retain package/environment locking and inheritance compatibility; this proposal does not select a package manager or create a generic framework. QA16 and QA28 define the acceptance evidence.
