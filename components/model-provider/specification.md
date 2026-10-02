# Provider-neutral model resource: specification

Follow the [model resource contract](../../docs/contracts/model-resources.md) and
[delivery acceptance matrix](../../docs/specification/s04-s06-delivery.md).
Owner: Cesar Zea. Implementation owner: A.

## Public boundary and dependencies

The [public entry point](src/slow_thinker_model_provider/__init__.py) exports the
immutable `ModelProviderConfig`, its `parse_config`, pure `normalized_request`,
`effective_operation`, `ProviderEndpoint`, `endpoint_from_record`,
`ProviderTransport` and `ModelProviderHost`. The package depends on the public host
SDK and HTTP transport; it imports no backend or other component implementation.
Imports and constructors perform no external business I/O.

Graph configuration contains `provider_profile` and `model`; installed effective
configuration contains `provider`, `model`, `model_alias`, `reasoning_efforts`,
`default_output_tokens` and `maximum_output_tokens`. The complete operation uses
`{"request": {...}}`. Configuration is fixed for the host lifetime.

The executable accepts one trusted bootstrap path and one `complete` operation.
Its `provider` client record contains `base_url`, `timeout_seconds`,
`close_seconds` and `max_response_bytes`; an optional managed MCP binding is
accepted. The launch credential is consumed from `SLOW_THINKER_SECRET_MODEL` and
removed from the environment before bootstrap processing.

## Implemented behavior

Request normalization rejects unknown options, model mismatches and unsupported
message shapes or modes without dropping values. OpenAI retains its reviewed
fixed settings and developer role. DeepSeek accepts system/user/assistant text
roles, maps output caps and thinking explicitly, and accepts temperature only in
`none` mode. Omitted reasoning explicitly selects `none`. Effective schemas
advertise these restrictions; accounting independently validates the same profile
before authorization.

The transport requires a managed grant and absolute monotonic deadline. It makes
one bounded HTTP attempt with explicit authentication, disabled redirects/proxy
inheritance, bounded body/header capture and bounded cleanup. Only exact reviewed
origins or explicit loopback `/v1` fixtures are accepted. Native bodies and headers
are recursively redacted before retention; UTC start/finish timestamps describe
the component's capture interval. Transport failures retain explicit uncertainty.
No hidden retry, repair, fallback, reasoning synthesis or cost calculation exists.

## Acceptance and verification

A01–A04 are implemented by the provider configuration, pure request boundary,
host and bounded transport. A07 preserves the separate legacy OpenAI package.
Scoped static checks are permitted during development. Native request, failure,
cancellation, response evidence and gateway integration tests remain pending until
the coordinator completes whole-system review and authorizes M06 testing.

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
