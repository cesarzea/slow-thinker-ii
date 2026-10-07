# Managed component gateway

Implementation contract for the already approved first-cycle mediated-call scope.
The implementation preserves the pinned MCP profile in
[mcp-profile.md](mcp-profile.md) and the authority rules in
[call-authority.md](call-authority.md).

## Wire surface

Expose the component-facing MCP server at `/mcp` on the same explicit loopback
origin as the configured `/v1` model gateway. Authenticate every request with the
current invocation grant in `Authorization: Bearer ...`. The grant is supplied
to a component in invocation metadata, never in the saved graph or arguments.
Keep operator credentials separate. Reject forbidden origins and unsupported
protocol versions; no automatic downgrade or model retry is introduced.

`server/discover` and `tools/list` publish only reviewed protocol capabilities and
the current caller's permitted operations, retaining effective input/output schemas.
Reuse the existing generated operation aliases from AccessPolicy. A named tool
call is authorized independently of whether discovery was previously performed.

`tools/call` arguments are the target operation's declared JSON object. Resolve
the alias under the authenticated grant and invoke ManagedCalls. Return the
preserved structured result and error flag; do not convert target failures into
successful output. Propagate the remaining deadline and cancellation through the
same managed path as native model calls. Protocol bookkeeping is diagnostic
evidence, never an additional graph activation or provider attempt.

## Application boundary

Add public application records and protocols for the following operations; all
JSON crosses these ports as the existing validated JSON types or canonical strings:

| Operation | Contract |
| --- | --- |
| `deadline(grant)` | Return the authenticated invocation deadline; revoked/unknown grants fail. |
| `tools(grant)` | Return permitted alias, target identity and exact OperationContract records. |
| `invoke(grant, alias, arguments_json)` | Await the ordinary ManagedResult from the shared managed-call path. |
| `report(grant, report)` | Validate and durably record optional component evidence, with platform-assigned identity. |
| `reject(grant, requested_operation, reason)` | Record a rejection only when the grant supplies authenticatable run context. Dispatch nothing. |

The coordinator routes these operations to the active run-owned service. Components
cannot select a run by placing an identifier in the request. NativeModelGateway
uses the same rejection recorder for a missing or forbidden model binding.
If authority cannot establish a run, record only bounded local diagnostics.

## Host bootstrap and normal clients

Add this optional entry to the existing trusted bootstrap `clients` object:

```json
{
  "mcp": {
    "url": "http://127.0.0.1:8000/mcp",
    "timeout_seconds": 30,
    "close_seconds": 5,
    "resources": {
      "worker": {"generate": "generated-authorized-worker-alias"},
      "router": {"route": "generated-authorized-router-alias"}
    }
  }
}
```

The operation keys match the resource's declared operation names. Timeout values
come from the effective limits profile, not these illustrative numbers. Resolve aliases from
the same frozen policy used by the gateway, and verify required bindings during
preparation. Resource bindings alone do not grant invocation permission.

The host SDK supplies public `McpEndpoint`, `mcp_endpoint_from_record` and an
async context-managed `managed_mcp_client(endpoint, invocation)` returning the
ordinary pinned MCP Client. Components use its normal tool-call interface.
Scoped credentials and client state are fresh per invocation. The helper does
not dispatch, retry or invent a tool selection on the caller's behalf.

Expose a separate optional `report_component(endpoint, invocation, report)` helper.
Keep OpenAI client setup and its ordinary call signatures unchanged. A narrow
LangChain StructuredTool binding wraps the same supported MCP client, as required
by the existing compatibility contract; do not install an incompatible adapter or
change the pinned protocol to accommodate it.

## Optional component reports

Reserve the tool alias `platform.report`, available only with active invocation
authority. Generated component aliases must not collide with that name. Its input:

```json
{
  "kind": "state",
  "schema_version": "1",
  "value": {"stage": "reviewing"},
  "source_occurred_at": 1790000000.0
}
```

Supported initial kinds are `progress`, `state`, `explanation` and `reasoning`.
`value` is JSON; the finite numeric source timestamp is optional. Reject unknown
fields/kinds/versions and excessive payloads through bounded recorded diagnostics.
Future namespaced kinds require explicit schema registration rather than silently
accepting arbitrary extensions.

Return `{"recorded": true}` only after durable storage succeeds. This platform
instrumentation operation emits `component.reported` evidence, not another scheduled
graph activation or billable attempt. Identity and receipt timestamp come from the
platform; provenance is `reported`. Preserve explicit missing content and apply
redaction before persistence. Do not expose another component's trace to the caller.
Reports received after authority closes fail; only trusted late settlement may
follow a closed paid attempt. Recording failure closes further admission.

## Acceptance

Exercise nested non-model and model calls, filtered discovery, direct guessed
aliases, stale/forged grants, normal native client signatures, cancellation,
reported/unavailable evidence, bounded capture and zero hidden retries. Complete
the existing SDK conformance matrix with simulated providers in the testing phase.
