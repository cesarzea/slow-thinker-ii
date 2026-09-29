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
