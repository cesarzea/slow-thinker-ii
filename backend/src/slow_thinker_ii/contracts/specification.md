# Shared value contracts: specification

Defines JSON values and JSON Pointers shared across backend boundaries.

## Public boundary

The [public entry point](__init__.py) is authoritative for exported names and signatures.

- JsonValue and JsonObject describe transport-neutral JSON.
- decode_json, encode_json, json_value and json_object validate and serialize values;
  json_value and json_object return validated deep copies.
- parse_pointer, format_pointer and value_at_pointer implement JSON Pointers (RFC 6901):
  `parse_pointer(text) -> tuple[str, ...]`, `format_pointer(tokens) -> str` (tokens may be
  array indices as `int`) and `value_at_pointer(value, tokens) -> JsonValue`, which returns
  None when the tokens do not resolve (indistinguishable from a JSON `null`).

## Required behavior

- Reject malformed JSON, duplicate object keys, non-string keys and non-finite numbers.
- Reject pointers that are neither empty nor start with `/`, and `~` escapes other than `~0`
  and `~1`. Array indices resolve only in canonical decimal form and within bounds.
- Produce deterministic compact JSON; do not perform I/O or import application services.

## Dependencies and ownership

Python standard library only; other modules consume the public package entry point.

## Acceptance criteria

- Valid values round-trip without changing their meaning.
- Invalid or ambiguous JSON fails explicitly instead of being silently normalized.
- Pointers round-trip between text and tokens, including escaped `~` and `/`.

## Shared contracts

- [Contracts index](../../../../docs/contracts/README.md)
