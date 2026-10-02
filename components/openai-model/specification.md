# OpenAI model resource: specification

Performs the supported provider HTTP request as an independently hosted managed resource.

## Public boundary

The [public entry point](src/slow_thinker_openai_model/__init__.py) is authoritative for exported names and signatures.

- ModelConfig and parse_config define the configured provider model and output bounds.
- ProviderEndpoint separates trusted provider endpoint/secret binding from graph data.
- ProviderTransport.complete performs the bounded provider request.
- OpenAIModelHost exposes the effective complete operation.

## Required behavior

- Only this provider resource performs external OpenAI I/O for its managed operation.
- Keep provider credentials out of graph snapshots, operation arguments and retained responses.
- Make one bounded request without hidden retries or redirects; preserve native response and usage.
- Accounting policy belongs to the platform adapter, not the component transport.

## Dependencies and ownership

Public host SDK and provider HTTP dependencies; no backend implementation imports.

## Acceptance criteria

- Successful and failed native provider responses retain the information needed for functional interpretation and accounting.
- Timeout or transport uncertainty is not misreported as proof of zero provider charge.

## Shared contracts

- [openai-initial-profile](../../docs/contracts/openai-initial-profile.md)
- [components](../../docs/contracts/components.md)

## S04–S06 active delivery

Follow [the shared contract](../../docs/contracts/model-resources.md). Implementation owner: A.

Retain public OpenAIModelHost/ProviderTransport and existing installations unchanged; this is a legacy provider-specific resource. Provider-neutral new graphs use model-provider while historical runs remain reproducible.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## S04–S06 development compatibility review

Public configuration, endpoint, host and transport source remain unchanged.
Historical installations retain their original launch contract and OpenAI-only
request/response behavior. The independent new `model-provider` distribution
handles provider-neutral graphs. A07 installation/transport/evidence regression
verification remains pending in M06 testing.

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
