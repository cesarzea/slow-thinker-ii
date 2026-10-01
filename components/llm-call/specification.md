# LLMCall component: specification

Implements one configurable model call with text or schema-validated JSON output and public extension hooks.

## Public boundary

The [public entry point](src/slow_thinker_llm_call/__init__.py) is authoritative for exported names and signatures.

- LLMCall generates a CallResult using a configured AsyncOpenAI client.
- build_messages, parse_response and validate_result are the documented specialization hooks.
- parse_config and effective_operation produce validated effective configuration and schemas.
- LLMCallHost and OpenAIEndpoint bind the component to the managed model gateway.

## Required behavior

- Create a fresh invocation object and client as required by the host lifecycle.
- Make exactly one configured model call; no hidden repair call or retry.
- Preserve raw received output and explicit validation issues when functional output is invalid.
- The prompt, effective inputs and output contract determine roles such as proposer and reviewer.

## Dependencies and ownership

Public host SDK and model-client dependencies; provider access is mediated by the platform.

## Acceptance criteria

- Text and valid structured results use the declared result envelope.
- Invalid JSON or schema output is retained as a failure without another paid call.
- Derived components use public extension points rather than private module imports.

## Shared contracts

- [llm-call](../../docs/contracts/llm-call.md)
- [python-component-api](../../docs/contracts/python-component-api.md)
