# SDK feasibility review

**Recorded: 2026-09-28. Status: limited executable evidence, not platform conformance.** Q04, Q06, Q17; CP01–CP07. Tests ran in a temporary environment with synthetic inputs and no model-provider requests. The repository still contains no application implementation or installed project dependencies. [Captured results and environment versions](../evidence/sdk-review-20260928.json).

## Tested environment

| Package/runtime | Observed version |
| --- | --- |
| Python | 3.13.0 |
| MCP Python SDK | 2.2.0 |
| OpenAI Python SDK | 3.19.2 |
| langchain-openai | 1.6.6 |
| langchain-core | 1.6.5 |
| langgraph | 1.2.12 |
| httpx2 | 2.13.1 |

These are tested candidates, not an approved production lock or a promise about every Python version. The captured environment includes transitive package versions and probe-script digests. `pip check` found no broken requirements after excluding the incompatible package below. The temporary harness must be converted into reproducible repository checks during approved implementation setup.

## Findings that change the integration proposal

### Pinned mode still needs a real discovery request

The [documented pinned mode](https://py.sdk.modelcontextprotocol.io/protocol-versions/) avoids automatic negotiation. The stdio probe confirmed zero outbound requests when entering a pinned client. It also found that `client.session.discover_result` was already populated with a local placeholder, and `await client.session.discover()` returned without sending `server/discover`.

Therefore, checking that the discovery object exists is insufficient. In this tested version, send an explicit typed request and validate its actual response:

```python
from mcp import Client, types

async def discover_peer(client: Client) -> types.DiscoverResult:
    result = await client.session.send_request(
        types.DiscoverRequest(), types.DiscoverResult
    )
    if "2026-07-28" not in result.supported_versions:
        raise ValueError("Required MCP version is unavailable")
    return result
```

This snippet checks only the version. Platform readiness must also validate identity, effective capabilities and discovered operation schemas. Save the verified response explicitly; do not assume a low-level request updates every cached high-level client property. Any cached discovery reused on reconnect needs the correct peer and authority scope.

The wire trace contained `server/discover`, tool listing and tool calls, with no `initialize` fallback. The same explicit discovery path worked over real loopback Streamable HTTP. This is positive-path evidence; incompatible-peer rejection and full readiness logic are still pending.

### The standard LangChain MCP adapter conflicts with MCP 2

Installed metadata for `langchain-mcp-adapters==0.3.2` requires `mcp>=1.24.0,<2.0.0`. A joint exact-version resolution with `mcp==2.2.0` failed with `ResolutionImpossible`. Installing the adapter without protecting the MCP pin replaced MCP 2.2.0 with 1.30.0 in the temporary environment. The adapter was then removed and MCP 2.2.0 restored; no such change affected the project.

Do not solve this by downgrading the platform protocol or ignoring dependency constraints. Recommend a narrow adapter exposing ordinary LangChain `StructuredTool` instances backed by the supported MCP 2 client. A probe used `StructuredTool.ainvoke(...)` to call a separately hosted MCP tool successfully. The production adapter must still map discovered schemas, structured errors, cancellation, identity and filtering; the probe does not implement these platform rules.

LangChain model calls and LangGraph nodes do not require that incompatible MCP adapter package. The tested OpenAI/LangChain/LangGraph candidates coexist with MCP 2.2.0. A future official adapter version must be evaluated through a new pinned matrix, not adopted through an unconstrained upgrade.

### Capabilities and protocol traffic need explicit handling

The test server registered only tools, but `MCPServer` discovery also advertised prompts and resources/subscriptions. The platform must publish only its reviewed effective capabilities; forwarding a high-level server's default declaration is not enough. Verify the concrete low-level server or capability-filtering mechanism before claiming a tools-only profile.

The client also issued a `tools/list` request around a tool invocation. Protocol traffic must remain observable without becoming another graph activation or billable model attempt. A per-invocation HTTP credential must authorize the necessary discovery/listing path as well as the business call, within the same filtered scope.

## What the probes established

| Area | Observed result | Remaining boundary |
| --- | --- | --- |
| MCP stdio | Independent subprocess, current protocol, real discovery, structured output, invalid-argument error and supplied request metadata | Effective instance schemas, failed-output envelopes and hostile/mismatched peers |
| MCP HTTP | Real `127.0.0.1` server; current protocol; metadata survived; missing/revoked synthetic bearer access returned 401; disallowed Origin returned 403 | Probe authentication was a minimal wrapper, not platform grants, OAuth compliance or permission filtering |
| OpenAI call shape | Standard synchronous/asynchronous Chat Completions calls accepted synthetic responses through configured clients | Actual provider/model support, usage categories and error mapping |
| LangChain model shape | `invoke`/`ainvoke` used the configured Chat Completions route; `max_tokens=16` became `max_completion_tokens=16` in the captured request | Full supported-option matrix and unsupported-option rejection |
| LangGraph | An async graph node used the configured LangChain model and returned its result | Internal graph telemetry and outer-platform correlation |
| LangChain tool shape | `StructuredTool.ainvoke` reached a tool over MCP 2 stdio through a small wrapper | Generic adapter publication, structured failure/cancellation and authority semantics |
| Retry setting | An OpenAI async call receiving synthetic HTTP 500 made one request with `max_retries=0` and raised the normal SDK exception | Every failure class and hidden retries in other adapters |

OpenAI and LangChain model calls used an in-memory HTTP mock with a synthetic model ID; they did not contact OpenAI or establish account access. The explicit HTTP server existed only for the MCP transport probe and was shut down. The [standard Chat Completions API](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) remains the intended model-facing call boundary.

CP01/CP02/CP04/CP06 now have partial feasibility evidence. CP03's complete two-direction orchestrator path, CP05 cancellation and CP07 capability filtering remain unproven. None of the probes exercises the graph executor, spending ledger, restart recovery or UI. These limitations must remain visible when reviewing [ADR 0007](../adr/0007-mcp-profile.md).
