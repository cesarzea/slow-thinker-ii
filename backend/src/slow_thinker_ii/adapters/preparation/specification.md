# Workflow runtime preparation: specification

Resolves a start intent into verified component hosts, resource bindings and a frozen workflow.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- InstalledWorkflowPreparer implements the application WorkflowPreparer port.
- HostAdapter, HostProfile and HostRequest define launch-specific binding contracts.
- PlainHostAdapter, OpenAIClientAdapter and OpenAIResourceAdapter provide the current host profiles.
- ResourceSettings and SecretSource separate configuration from credential delivery.

## Required behavior

- Resolve exact graph, component, limits and tariff identities before admission.
- Keep credentials in trusted launch bindings, outside saved graph configuration.
- Respect preparation deadlines and clean up work that outlives a withdrawn intent.

## Dependencies and ownership

Public catalog, installation, process and application contracts; bootstrap selects concrete adapters.

## Acceptance criteria

- Unusable installation or configuration fails before graph execution.
- Prepared workflows contain enough immutable evidence to identify the runtime used.

## Shared contracts

- [component-installation](../../../../../docs/contracts/component-installation.md)
- [component-lifecycle](../../../../../docs/contracts/component-lifecycle.md)

## Verification

Preparation tests verify frozen snapshots, effective installed contracts, bootstrap bindings, integrity checks and withdrawal/deadline cleanup.

## Sprint additions

- [managed-gateway](../../../../../docs/contracts/managed-gateway.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [conditional-routing](../../../../../docs/contracts/conditional-routing.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

Preparation publishes outgoing MCP clients for instances with configured resource
bindings or discoverable outgoing grants, using aliases from the same frozen
access policy used at execution. Other host profiles remain unchanged. Conditional
and Sequence workflows share installation, limits, tariff and host ownership
preparation; graph resource bindings do not grant permission.

## S03 personal experiment library

Follow the [shared contract](../../../../../docs/contracts/personal-experiments.md) for wire values, data origins,
public interfaces, validation scope, errors, immutable identity, paging and failure
handling. Implementation owner: A.

Change InstalledWorkflowPreparer's concrete BundledDefinitionStore annotation
to library.DefinitionReader from the public application namespace. Freeze/read the
exact raw definition through this port. Keep installed effective schema checks,
configuration, provider/limit validation, mediated dispatch, costs and run snapshots
unchanged. Existing bundled-reader callers remain structurally compatible.

Acceptance follows the shared S03 scenarios. Development delivery does not claim
testing is complete. Keep module-private choices within these public contracts.

## S03 development implementation

`InstalledWorkflowPreparer` consumes the public raw-definition reader and freezes
the exact selected text through the existing installed compiler. Host preparation,
effective contracts, provider and limit checks, mediated dispatch and saved run
evidence retain their existing path. Bundled stores remain structurally compatible.
Focused S03 acceptance prepares saved revisions and executes their production
program/policy using an explicit fixture environment, real Sequence and LLMCall
and an in-memory native SDK transport. Exact prompt/input, frozen configuration,
mediated call evidence and earlier run preservation pass. Synthetic description
installations are not claimed to execute inference. Complete coordinator
verification remains pending.

## S04–S06 active delivery

Follow [the shared contract](../../../../../docs/contracts/model-resources.md). Implementation owner: A.

Add optional model_tariffs reader, ModelResourceAdapter and model_capabilities. Add HostRequest.runtime_id and HostProfile.model_tariff with compatible defaults; pass runtime_id from prepare to HostPlanner. Freeze each resource tariff in instance evidence; legacy snapshot and adapters remain supported. Register model-resource; bootstrap separately composes B's MemoryResourceAdapter.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## S04–S06 development implementation

`InstalledWorkflowPreparer` appends optional `model_tariffs` after existing
arguments. `HostPlanner` passes the supplied runtime identity to compatible
`HostRequest.runtime_id`; `HostProfile.model_tariff` freezes the immutable public
selection. Standard adapters retain legacy names and add `plain`,
`openai-resource` and `model-resource`.

`ModelResourceAdapter` resolves the settings profile's billing identity through
`workspace.ModelTariffReader.selected`, independently of its dictionary key.
It rejects unavailable, stale, mismatched or unreviewed resources before launch,
binds one policy to `complete`, and supplies launch-only authentication and the
trusted native configuration. Old callers without a scoped reader may select
new OpenAI resources from the compatible global tariff; DeepSeek requires a
matching scoped selection. Legacy OpenAI resources retain their original path.

ResourceSettings remains schema version 1; missing provider/billing fields retain
OpenAI defaults. `ServiceEndpoints` appends the reviewed DeepSeek origin with
explicit loopback fixture support. `model_capabilities(settings)` publishes the
shared fields in stable profile order and omits credential references and secrets.
Temperature support indicates the provider capability; DeepSeek still restricts
its use to `none` reasoning during request validation.

Snapshots retain the global OpenAI tariff and add each model instance's frozen
selection. DeepSeek instances include normalized rates/schedule/calendar and the
captured HTML digest without duplicating raw source into every snapshot. These
changes implement A01–A03, A05–A07 and B's runtime identity handoff. Installed
preparation, mediation and historical compatibility tests remain pending in the
assigned M06 testing phase.

## S04–S06 scoped testing evidence

The assigned A acceptance/regression suite passes 532 tests using recorded official
prices, isolated SQLite state and simulated native provider transport. Ordinary
OpenAI SDK, LangChain and unchanged LLMCall requests cross actual loopback gateway,
managed authority, real model host/transport and pricing boundaries. Separate
caller grants select independent providers; cross-agent binding requests fail
before native dispatch. Exact cache/timing/calendar charges, source retention,
quanta rounding and historical quote/snapshot preservation pass.

Preparation evidence uses production InstalledWorkflowPreparer with explicitly
description-only installations; it does not claim installed inference. No paid
provider calls occurred. Scoped static checks pass. Coordinator review and full
unchanged verification remain pending; the complete S04–S06 delivery is not yet
claimed verified.

## Installed startup composition correction

Actual installed startup failed before any paid call because preparation added an
MCP client to a calculator that has no outgoing access. This was a production
composition defect; description-only admission tests did not detect the host's
bootstrap rejection.

The corrected binding step retains the original HostProfile when both configured
resource bindings and discoverable outgoing grants are empty. Either condition
still permits gateway binding; explicit caller grants without resource slots need
gateway discovery. Existing client records survive when MCP is added.

Three public InstalledWorkflowPreparer regressions verify calculator clients are
empty, memory retains exactly memory_store, both model generations retain provider
only, legacy OpenAI clients survive, and an explicitly granted caller without
slots receives MCP. Missing required grants still fail admission. The focused
preparation acceptance/regression suite passes 74 tests; the changed binding
helper has 100% line and branch coverage. Installation fixtures remain explicitly
description-only. Coordinator validation of actual installed startup and full
unchanged verification remain pending.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
