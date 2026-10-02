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

Preparation publishes general MCP clients with aliases from the same frozen access policy used at execution. Conditional and Sequence workflows share installation, limits, tariff and host ownership preparation; graph resource bindings do not grant permission.

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
