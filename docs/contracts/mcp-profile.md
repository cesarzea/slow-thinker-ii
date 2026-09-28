# MCP integration profile

**Status: Proposed profile, not implemented.** Requirement R07 selects current stable MCP; the concrete transport and optional-feature profile requires approval. The official versioning page identifies **2026-07-28** as current, rechecked on 2026-09-28. [Source](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning).

## Protocol basis

Current MCP uses per-request protocol/capability metadata. Servers implement `server/discover`; transport reuse does not establish application state. Follow the required base semantics, including message patterns and validation, rather than recreating an older initialization-only handshake. [Discovery](https://modelcontextprotocol.io/specification/2026-07-28/server/discover) and [base protocol](https://modelcontextprotocol.io/specification/2026-07-28/basic/index).

MCP tools expose input and optional output schemas. The platform filters discovery and checks invocation independently; naming an unavailable operation must not bypass policy. The proposed platform contract requires declared output schemas for its managed operations. [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

## Proposed transport directions

| Direction | Initial proposal | Identity boundary |
| --- | --- | --- |
| Platform client → component server | stdio for local processes | Trusted launch profile and assigned component identity |
| Component MCP client → platform server | Separate authenticated loopback Streamable HTTP | Scoped credentials bound to component/run authority |
| Component compatible model client → platform | OpenAI-compatible loopback HTTP entry translated to a managed model operation | Scoped component/run authority and parent-activation correlation |
| External compatible client → platform | Explicit MCP or OpenAI-compatible endpoint | Authenticated caller and permitted target mapping |

The current transport model does not allow servers to issue arbitrary reverse JSON-RPC requests on the same connection. A component consuming other managed capabilities uses a separate client path. [Transport specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports).

For HTTP, support the required request metadata and response forms, validate origin, bind locally, and authenticate access. Application session identity remains explicit. [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http).

## Proposed capability scope

Required base protocol compliance is not optional. The first platform-facing business surface is tool-oriented: discovery, filtered tool listing, schema-checked invocation, progress/log evidence and cancellation. Support for resources, prompts, elicitation, subscriptions, tasks and other extensions must be recorded feature by feature before a compatibility claim.

This proposal does not redefine optional MCP capabilities or claim that a basic tools implementation is the whole protocol. Mandatory message-pattern behavior must be verified against the selected revision even when no corresponding business feature is advertised. Undeclared or unsupported behavior is rejected explicitly.

The stable specification and optional feature states are authoritative. Do not silently select a draft revision, downgrade protocols, or advertise an extension solely because its SDK exposes a method. Specific SDK releases and legacy interoperability remain Q04.

## Cancellation and accounting

Use the transport's cancellation mechanism: stdio cancellation notification or closing the relevant HTTP response stream. A cancellation request does not prove external billing ended. The platform must keep control-state finalization separate from charge reconciliation. [Cancellation](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/cancellation).

Late accounting observations must not be accepted as successful output that advances a stopped graph. The details of out-of-band usage reconciliation remain part of Q08–Q09.

## Familiar client interfaces

**Accepted requirement:** component processes must call LLMs and other managed capabilities through the orchestrator with familiar client interfaces from the first cycle. Compatibility applies to outgoing calls while a component handles an activation, as well as to external clients.

**Proposed integration:** configure standard model clients to use the platform's compatible endpoint and expose authorized component operations as MCP tools or compatible LangChain tools. LangGraph nodes consume those configured clients and tools. The following call shapes illustrate the required developer experience; they are not an implemented API or a complete compatibility matrix.

| Consumer interface | Familiar call shape | Proposed platform routing |
| --- | --- | --- |
| OpenAI Python client | `client.chat.completions.create(model=..., messages=...)` | Platform endpoint resolves the permitted model resource and invokes it through MCP after admission. |
| LangChain model client | `model.invoke(messages)` or `await model.ainvoke(messages)` | Configured compatible client reaches the same managed model route. |
| MCP or LangChain tool client | Standard MCP tool invocation or the compatible tool's invocation interface | Client connects to the platform; authorized agent, tool and resource operations retain their declared argument schemas. |
| LangGraph node | Calls the configured model or tool using its usual interface | Each managed outgoing call reaches the orchestrator, with the originating activation preserved. |

The [OpenAI Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) documents the model call shape. LangChain documents [model invocation and configurable endpoints](https://docs.langchain.com/oss/python/integrations/chat/openai) and [MCP tool integration](https://docs.langchain.com/oss/python/langchain/mcp). These establish integration patterns, not conformance to this platform's MCP profile. The [SDK review](sdk-compatibility.md) found that `langchain-mcp-adapters==0.3.2` conflicts with MCP 2.2.0; the proposed initial tool binding uses a narrow standard-StructuredTool adapter instead of that package.

MCP remains the component exposure and dispatch contract. An OpenAI-compatible HTTP request is translated by a platform adapter; it is not itself an MCP message. Compatibility adapters must enter the shared admission path before dispatch. Only the authorized provider adapter performs external provider I/O.

Client setup may change endpoints, scoped credentials or adapters; supported invocation signatures must not require a platform-specific replacement method. The exact request/response/error matrix, SDK versions, retry behavior, timeout propagation and correlation mechanism require review under Q04 and Q06. Unsupported options must fail explicitly, never disappear silently. Internal LangGraph state is observable only when exposed by instrumentation.

The same authorization, routing, deadline, accounting and observation pipeline must serve all entry points. Responses API support, generated-token streaming and broader compatibility are later capabilities; this does not remove protocol-required transport behavior from the initial profile.

## SDK candidate and conformance work

The official Python SDK release page identifies **`mcp==2.2.0`** as the latest release on 2026-09-28. Propose it as the first candidate, pending complete integration checks and a reproducible dependency lock. The release documents current-protocol behavior and lists gaps for the tasks extension, DPoP and the jwt-bearer grant; do not advertise those through this candidate. Subsequent [temporary SDK probes](sdk-compatibility.md) installed and exercised it without changing project dependencies or making model-provider requests. [Release evidence](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.2.0).

The SDK's default automatic mode can fall back to an older handshake. Its explicit `mode="2026-07-28"` pins the version but skips wire discovery. The probe also found a locally populated discovery placeholder: `session.discover()` did not send a request. Propose a pinned client plus an explicit typed `DiscoverRequest` through `session.send_request`, validating and retaining the actual response for readiness. This mechanism worked over stdio and loopback HTTP; full platform readiness is still unimplemented. [Protocol-mode documentation](https://py.sdk.modelcontextprotocol.io/protocol-versions/), [measured distinction](sdk-compatibility.md#pinned-mode-still-needs-a-real-discovery-request).

| Check | Required evidence before a compatibility claim |
| --- | --- |
| CP01: version and discovery | Both local stdio and authenticated loopback HTTP use 2026-07-28; discovery mismatch/unsupported versions fail readiness without fallback. |
| CP02: operation schemas | Per-instance input/output schemas survive publication and validation. Bundle trusted URN references into self-contained schemas; test success and structured error results. |
| CP03: nested calls | An agent awaiting an OpenAI-compatible or MCP subcall completes without blocking the orchestrator; originating activation and immediate parent call remain identifiable. |
| CP04: authority | Filtered discovery, denied direct invocation, revoked grants and client reuse match the [authority proposal](call-authority.md). |
| CP05: cancellation | stdio notification and HTTP stream closure follow the selected protocol; late results cannot advance a stopped graph or erase cost obligations. |
| CP06: familiar clients | Pin and exercise the selected OpenAI/LangChain/LangGraph versions and supported requests, responses, errors and retry settings against the chosen provider profile. |
| CP07: optional capabilities | Match every advertised feature to its adapter and executable evidence; unsupported optional features stay unadvertised. |

The [SDK review matrix](sdk-compatibility.md#what-the-probes-established) records partial CP01/CP02/CP04/CP06 evidence and the limits of each test. It does not establish platform/proxy conformance; CP03, CP05 and CP07 still require their complete scenarios. The owner selected inexpensive OpenAI access; the [initial model profile](openai-initial-profile.md) supplies a GPT-6 Luna candidate and tariff evidence for CP06. Live provider request/error mapping and cost bounds remain to be verified.

## Approval checks

Resolve Q04 and Q06: transports, caller authentication, operation namespacing, capability filtering/cache scope, unsupported-version handling, SDK evidence and the exact first interoperability matrix. Review the two-direction nested-call scenario before accepting [ADR 0007](../adr/0007-mcp-profile.md).
