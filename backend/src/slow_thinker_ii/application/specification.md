# Application coordination: specification

Coordinates execution, admission, costs and operator commands through transport-neutral ports.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- ExecutionCoordinator manages durable start, stop and withdrawal commands.
- RunAdmission, ManagedCalls and ManagedRun coordinate authority, dispatch and finalization.
- RunProgram and RunEnvironment separate scheduling from runtime resources; SequenceProgram implements finite sequences.
- NativeModelGateway translates familiar model requests into managed operation calls.
- BudgetLedger and TariffRefresh use persistence and tariff-source ports.
- OperatorQueries, RunStore and the other exported protocols define adapter contracts.

## Required behavior

- Persist dispatch intent before side effects; never hold a database transaction across an awaited network call.
- Every managed entry point must share authority, deadlines, admission, recording and settlement.
- Separate terminal execution state, cleanup progress and financial uncertainty.
- Do not automatically replay ambiguous paid calls after interruption.

## Dependencies and ownership

Public domain modules and adapter ports; concrete frameworks and provider clients are assembled by bootstrap.

## Acceptance criteria

- Nested calls retain their authenticated caller, parent call and activation.
- Budget refusal stops the run and preserves dispatched exposure.
- Cancellation and late responses cannot advance a terminal workflow.

## Shared contracts

- [call-authority](../../../../docs/contracts/call-authority.md)
- [execution](../../../../docs/contracts/execution.md)
- [observation](../../../../docs/contracts/observation.md)

## Verification

The backend suite verifies conditional acceptance, exhaustion, Stop, deadlines and monetary refusal, plus authenticated MCP, native OpenAI, LangChain and LangGraph calls with simulated providers. Browser fixtures retain exact definitions and deterministic feedback. Final repository and installed acceptance checks pass.

## Sprint additions

- [managed-gateway](../../../../docs/contracts/managed-gateway.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [conditional-routing](../../../../docs/contracts/conditional-routing.md) defines the implemented cross-package contract while preserving existing supported behavior.
- [inspection-projections](../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

ManagedGatewayService exposes deadline, filtered tools, invoke, report and rejection recording. ConditionalProgram validates each bounded controller decision and records activation sources before dispatch. RunEvidence accepts the closed report vocabulary with bounded redaction; reports are limited to 100 per activation (or non-activation call). ProcessJournal and OwnedRunEnvironment carry restart-safe ownership.
