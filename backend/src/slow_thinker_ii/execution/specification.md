# Execution state rules: specification

Defines run outcomes and validates finite sequence decisions independently of runtime services.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- RunState and TerminalState define lifecycle states.
- stopped_outcome maps a recorded stop reason to a terminal outcome.
- require_sequence_decision validates the next or complete decision expected by a finite sequence.

## Required behavior

- Do not perform I/O or mutate persisted runs.
- Timeout, operator cancellation and other failures retain distinct outcomes.
- Do not reinterpret Sequence as a conditional or cyclic controller.

## Dependencies and ownership

Public JSON contracts; scheduling, persistence and component hosts remain outside this module.

## Acceptance criteria

- Invalid controller decisions fail before another activation is scheduled.
- A terminal outcome is not rewritten by later accounting observations.

## Shared contracts

- [execution](../../../../docs/contracts/execution.md)
- [graphs](../../../../docs/contracts/graphs.md)

## Verification

Bounded decision tests pass for acceptance on the final activation, exhaustion and invalid controller responses.

## Sprint additions

- [conditional-routing](../../../../docs/contracts/conditional-routing.md) defines the implemented cross-package contract while preserving existing supported behavior.

## Implemented behavior

require_conditional_decision independently verifies activate, complete and exhausted decisions; ActivationLimitReached retains the explicit activation_limit_reached failure reason.
