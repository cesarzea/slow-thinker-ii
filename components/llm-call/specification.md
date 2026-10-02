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

## October 2026 maintenance: Generator typing compatibility

The decorated `OpenAIEndpoint.client` implementation uses
`AsyncGenerator[AsyncOpenAI]` for Pyright 1.1.414. It yields the same
`AsyncOpenAI` client; retain managed client/context behavior and no hidden provider calls.

## S04–S06 active delivery

Follow [the shared contract](../../docs/contracts/model-resources.md). Implementation owner: A.

Preserve one-call LLMCall semantics and public hooks. Reasoning options already supported by ordinary SDK parameters must reach provider-neutral resources without changing functional output envelopes or introducing tools/memory into plain LLMCall.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## S04–S06 development compatibility review

The existing public host/client/configuration and specialization APIs are retained
without source changes. Ordinary SDK parameters already forward reasoning effort
through the managed gateway; the bound resource validates provider support before
paid dispatch. Plain LLMCall continues to make one call and uses the same result
validation/envelopes. Tools and memory are implemented by separate components.
A02–A04/A07 compatibility verification remains pending in M06 testing.

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

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
