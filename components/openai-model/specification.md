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
