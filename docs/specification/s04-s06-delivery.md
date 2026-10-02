# S04–S06 delivery block

| Document control | Value |
| --- | --- |
| Document ID | SPRINT-S04-S06-001 |
| Owner | Cesar Zea |
| Activated | 2026-10-02, Europe/Lisbon |
| Status | Locally verified; owner review and hosted verification pending |
| Authorization | Owner goal: complete S04, S05 and S06 |
| Method | [M06](../continuous-improvement/methods/006-delivery-preparation.md) |

## Objective and boundaries

Deliver all three [roadmap](sprint-roadmap.md) scopes through the product interface.
Prepare the whole block before assigning implementation, retain the S04 → S05 →
S06 acceptance checkpoints, and record evidence separately for each sprint.
The owner selected DeepSeek Flash as the second provider, a deterministic calculator
and simple persistent key/value memory configurable as private or shared resources.
The existing remaining USD 3 authorization covers all actual model demonstrations.

Configuration, composition and resources remain extensible. A component may include
managed children or bind private/shared resources. Calls still pass through the
orchestrator. Current Redirector selects one declared port; simultaneous emissions
with different payloads remain future control/communication work. mem0 and graph
memory adapters are later implementations of the resource contracts.

## Architecture and shared contracts

- [Model resources](../contracts/model-resources.md): one provider-neutral resource,
  familiar clients, OpenAI/DeepSeek adapters, explicit reasoning capabilities,
  independent daily tariffs, reservations and preserved native evidence.
- [Tools and memory](../contracts/tools-memory.md): calculator, scoped durable memory,
  configurable composition, external trusted package preparation and MCP calls.
- [Product workspace](../contracts/product-workspace.md): discovery, source-preserving
  structured graph editing, configuration commands, forms, navigation and recovery.
- Retain the existing component, graph, installation, authority, lifecycle,
  observation and accounting contracts. Preserve existing saved runs and APIs.

## Ownership and dependency handoffs

| Owner | Complete package assignments | Consumed public contracts |
| --- | --- | --- |
| A | `components/model-provider`; backend adapters `models`, `openai`, `tariffs`, `preparation` | Model resource contract; application `workspace.ModelTariffReader`; existing pricing/host ports |
| B | `components/calculator`, `components/key-value-memory`, `components/contextual-call`; backend adapter `resources`; `tooling/components`; external resource-agent example | Tools/memory contract; public host SDK; preparation `HostRequest.runtime_id` and `HostProfile` |
| C | All frontend production packages | Product workspace wire contract; existing validated operator/definition APIs; graph and evidence contracts |
| Coordinator | Backend application, catalog, HTTP, SQLite and bootstrap; shared quality/package configuration; public contract fixtures and delivery records | All shared contracts and delivered public package APIs |

Shared files have the coordinator as sole owner. A and B coordinate only through
specified public contracts, never by editing each other's assigned packages.
B owns all preparation recipes, including A's `model-provider` recipe. Testing is
assigned separately after development and whole-system review. No implementer owns
a cross-package architecture decision.

## Required public handoffs

- Application `workspace.ModelTariffSelection(revision, validated_at)` is immutable;
  `ModelTariffReader.selected(profile_id)` returns that value or `None`.
- Preparation retains legacy signatures and adds an optional model tariff reader.
  `HostRequest.runtime_id` identifies run-owned state; `HostProfile.model_tariff`
  freezes the selected model-specific tariff. Old OpenAI callers remain valid.
- Model preparation exports `model_capabilities(settings)` and registers
  `model-resource`; resource preparation exports `MemoryResourceAdapter(root)`.
- Resource settings retain schema version 1 and old OpenAI defaults. DeepSeek
  profiles explicitly select provider and billing profile; no keys or endpoint
  strings enter graph definitions.
- Workspace discovery and source-patch HTTP payloads are defined verbatim in the
  product workspace contract. Frontend packages consume their public validated API.
- Graph definitions retain their existing execution profiles and immutable identity.
  Forms and JSON editing share one source; no separate UI-only graph representation.

## Acceptance matrix

| ID | Sprint | Required evidence |
| --- | --- | --- |
| A01 | S04 | Configure two graph agents with OpenAI and DeepSeek independently; actual managed calls identify both providers/models. |
| A02 | S04 | Familiar OpenAI and LangChain model invocations enter the same mediation, authority, deadline and accounting path. |
| A03 | S04 | Supported reasoning modes reach the provider; unsupported options fail before paid dispatch. |
| A04 | S04 | Preserve native response, reasoning if supplied, usage, provider errors and request identity; no hidden retry/fallback. |
| A05 | S04 | Daily automatic refresh for both reviewed tariff sources; malformed source preserves last valid version; historical charges remain frozen. |
| A06 | S04 | Quote conservative bounds; cache categories and UTC peak/off-peak accounting are independently checked; ambiguous timing/usage retains exposure. |
| A07 | S04 | Existing OpenAI installations, definition imports and saved execution evidence remain compatible. |
| A08 | S05 | Build/prepare/install an external authored component with explicit registration, descriptor and exact dependency closure; execute it through MCP. |
| A09 | S05 | Calculator accepts bounded arithmetic and rejects executable, excessive or invalid expressions; actual nested call is recorded. |
| A10 | S05 | Private resource instances are isolated; explicitly shared bindings observe the same key/value state. |
| A11 | S05 | Run-local memory is fresh in the next run; persistent memory survives host restart and later runs without accidental cross-namespace reuse. |
| A12 | S05 | Version-checked memory updates, bounded values and explicit failures preserve durable state and evidence. |
| A13 | S05 | ContextualCall can use calculator and memory around an ordinary worker, including composition with RoutedCall; all child calls are mediated. |
| A14 | S05 | Permission rejection, nested failure, cancellation and budget stop do not bypass mediation or silently repeat paid work. |
| A15 | S06 | Configure known and external components from discovered schemas, including inputs/outputs, prompt/model/reasoning and child/resource bindings. |
| A16 | S06 | Create/edit supported graph nodes, sequence order or conditional routes, input bindings, permissions and activation limits through forms. |
| A17 | S06 | Form edits preserve unrelated configuration, extensions and large integer values; JSON import/edit remains available. |
| A18 | S06 | Validate, save exact immutable revisions/variants and execute them; earlier run definition/results remain unchanged. |
| A19 | S06 | Configure deadlines and run/session/month budgets within server ceilings; stale revisions and below-commitment limits are rejected; uncertain commands replay safely. |
| A20 | S06 | Navigate experiments/configuration, resources, runs/results/history and settings; coherent loading/error/empty states and keyboard access. |
| A21 | S06 | Agent-centric graph and optional technical evidence retain exact selected run/activation/call identities, English labels and recovery behavior. |
| A22 | All | Full unchanged local/CI verification gates, independent coverage, actual browser journeys and actual provider/resource demonstration within remaining USD 3. |

## Testing and delivery sequence

Finish individual and whole-system code review before functional test implementation.
The coordinator prepares shared catalogue, tariff, graph and memory fixtures and
runs one representative composition/browser readiness case before parallel test
assignments. Classify failures as production, contract, fixture or environment
issues; make grouped corrections and resume the same configured verification entry
point. Do not weaken source-size, type, boundary, security or coverage gates.

Capture timed phase boundaries and rework separately in the private activity record.
Create the formal process-cycle evaluation on closure without treating parallel
activity as elapsed time or claiming a method improvement without comparable evidence.
Keep sprint reports and the central version register distinct from package releases.

## Preparation review

The coordinator reviewed the public producer/consumer boundaries on 2026-10-02.
Model discovery exposes profiles rather than secrets; form changes preserve source
numbers; runtime identity scopes memory; per-model tariff snapshots preserve old
OpenAI evidence; source patching and configuration receipts remain coordinator-owned.
Package-local algorithms and presentation details are implementer decisions.
Functional test implementation begins after individual and whole-system review.

## Delivery checkpoint — 2026-10-02

All A01–A22 outcomes have local evidence. S04's model/tariff cases cover A01–A07;
S05's packaging/resource/composition cases cover A08–A14; workspace API, storage,
frontend and browser cases cover A15–A21. A22 is supported by the complete unchanged
runner and the separate installed actual-provider/resource demonstration.

| Scope | Delivery evidence |
| --- | --- |
| S04 | [Status report 0.0.4.1](../progress/sprint-04-status-report.md); model/provider/tariff/preparation tests; actual OpenAI and DeepSeek calls |
| S05 | [Status report 0.0.5.1](../progress/sprint-05-status-report.md); external installed MCP workers, calculator and scoped memory/composition tests |
| S06 | [Status report 0.0.6.1](../progress/sprint-06-status-report.md); structured authoring/settings tests and production browser journeys |
| Shared assurance | [Verification](../verification.md#provider-resource-and-workspace-delivery--2026-10-02); [sanitized verification summary](../evidence/s04-s06-verification-20261002.json) |
| Actual execution | [Live validation](../progress/s04-s06-live-validation.md); [native usage/provenance summary](../evidence/s04-s06-live-execution-20261002.json) |
| Process evaluation | [C06](../continuous-improvement/cycles/006-provider-resource-workspace/report.md); M06 remains approved |

The complete local runner passed 2,204 Python tests, 340 frontend tests and 20
browser journeys, with the original static/security/build, mutation and independent
coverage gates. Two actual revisions completed with no unresolved charge, costing
USD 0.000520600 together within the original USD 3 total authorization.

Manual live-session inspection remains pending credential authorization; automated
browser journeys and actual production execution evidence are complete. This is a
locally verified delivery checkpoint, not owner acceptance, merge approval or a
stable release. No later sprint is activated.
