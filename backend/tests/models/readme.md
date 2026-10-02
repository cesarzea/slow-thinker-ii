# Provider-neutral acceptance fixtures and tests

These tests exercise public request/pricing policies, official recorded source
imports, production preparation and real SDK/LangChain gateway mediation. Native
provider traffic uses injectable simulated transports and synthetic credentials.
Preparation installations are explicitly description-only; they do not execute
inference. The mediation cases execute the real ModelProviderHost and transport
behind public OperationPort/ManagedCalls contracts.

See [specification.md](specification.md) for the acceptance boundary.
