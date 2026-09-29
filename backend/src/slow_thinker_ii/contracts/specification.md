# Shared value contracts: specification

Defines JSON values and operation envelopes shared across backend boundaries.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- JsonValue and JsonObject describe transport-neutral JSON.
- decode_json, encode_json and json_object validate and serialize values.
- OperationContract declares operation schemas; OperationResult retains payload JSON and the error flag.

## Required behavior

- Reject malformed JSON, duplicate object keys, non-string keys and non-finite numbers.
- Produce deterministic compact JSON; do not perform I/O or import application services.

## Dependencies and ownership

Python standard library only; other modules consume the public package entry point.

## Acceptance criteria

- Valid values round-trip without changing their meaning.
- Invalid or ambiguous JSON fails explicitly instead of being silently normalized.

## Shared contracts

- [components](../../../../docs/contracts/components.md)
