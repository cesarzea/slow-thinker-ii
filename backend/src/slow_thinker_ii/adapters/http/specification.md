# adapters.http: specification

HTTP adapters for the [operator API](../../../../../docs/contracts/operator-api.md), the
model endpoint of the [LLM service](../../../../../docs/contracts/llm-service.md) and the
report tool of the [component protocol](../../../../../docs/contracts/component-protocol.md).

## Public interface (`slow_thinker_ii.adapters.http`)

```python
@dataclass(frozen=True)
class HttpServices:
    catalog: Callable[[], Catalog]
    graphs: GraphLibrary
    runs: RunService
    gateway: LlmGateway
    reports: ReportService
    usage: UsageService

@dataclass(frozen=True)
class HttpSettings:                   # raises ValueError; the token is never shown, not even in repr
    operator_token: str | None        # 32–128 visible ASCII characters, no spaces;
                                      # None: no operator authentication (opt-in, loopback)
    allowed_hosts: tuple[str, ...]    # at least one, e.g. ("127.0.0.1:8000", "localhost:8000")
    allowed_origins: tuple[str, ...]  # exact scheme://host[:port], may be empty
    max_body_bytes: int = 1_048_576   # positive; bounds every request body
    static_directory: Path | None = None   # compiled interface, served at "/"

def create_http_app(services: HttpServices, settings: HttpSettings,
                    lifespan: Lifespan[FastAPI] | None = None) -> FastAPI
    # raises ValueError when static_directory is not a directory
```

## Behaviour

- All handlers are `async` and call the use cases on the event-loop thread, never in a
  thread pool. No OpenAPI document or docs pages are served.
- `/api/v2` and `/api/v2/*` (any method, known or not) are checked before routing and
  before any body is read: exactly one `Host` equal to an allowed host (`403
  operator_host_denied`); an `Origin`, when present, exactly one allowed origin, and no
  `Sec-Fetch-Site: cross-site` (`403 operator_origin_denied`); then, with a token,
  exactly one `Authorization: Bearer <token>`, compared in constant time (`401
  operator_authentication_required`). Every reply, refusals and failures included,
  carries `Cache-Control: no-store`.
- Without a token (`operator_token=None`) there is no bearer check and any
  `Authorization` header is ignored; instead the peer (`scope["client"]`) must be in
  `127.0.0.0/8` or `::1`, IPv4-mapped forms included, and a connection without a client
  address is refused (`403 operator_client_denied`, `Requests without an operator token
  are accepted only from this machine.`). Host and origin checks, `no-store` and body
  bounds are unchanged, and the token mode never checks the peer. `/v1/chat/completions`
  and `/mcp` need the invocation grant in both modes.
- `GET /api/v2/access` answers `200 {"authentication": "token" | "none"}` without an
  `Authorization` header in both modes; host, origin and (without a token) peer checks
  and `no-store` still apply. Any other method, or the path with a trailing slash,
  answers like an unknown route.
- Operator errors are exactly `{"error": {"code", "message", "diagnostics"?}}` with
  English messages of at most 2,000 characters (longer ones end in `…`); internals,
  paths and exception texts of unexpected failures never appear.
- Request bodies: an empty body counts as `{}`; otherwise the body must be
  uncompressed `application/json`, within `max_body_bytes`, UTF-8 JSON without
  duplicate keys or non-finite numbers, and an object with exactly the documented fields
  (`input` of `POST /runs` is optional; absent or `null` runs the Trigger's message).
  `version` and `change` are integers from 1 to 999,999,999. Every route refuses unknown
  or repeated query parameters; integers are decimal. `GET /runs` defaults `limit` to
  100, `GET /runs/{id}/events` defaults `limit` to 500 and `after` to 0, and
  `GET /graphs/{id}/changes` defaults `limit` to 50 and takes an optional non-negative
  `before` (exclusive); the use cases clamp `limit` to 1–100, 1–500 and 1–100. An empty
  `graph_id` filter means all graphs. A version or change path segment that is not such
  a number is `404 version_not_found` or `404 change_not_found`.
- Graphs follow [ADR 0024](../../../../../docs/adr/0024-working-copy-and-activated-versions.md):
  `POST /graphs` creates a graph from a draft (`201 {"id", "branch": "main", "change":
  1}`); `GET /graphs/{id}/branches` lists branches; `POST /graphs/{id}/branches`
  `{"name", "from": {"version"} or {"change"}}` starts one (`201 {"name", "change"}`;
  `from` must name exactly one number, otherwise `422 invalid_request`);
  `POST /graphs/{id}/changes` `{"branch", "document"}` answers `201 {"change", "at"}`, or
  `200` with the branch's latest change when `GraphLibrary.record_change` reports the
  document unchanged; `GET /graphs/{id}/changes` takes an optional `branch` filter (empty
  means every branch); `POST /graphs/{id}/versions` `{"change"}` activates it (`201
  {"version", "branch", "change"}`). Lists and records are the library's `to_json()`
  shapes, unchanged. The library's `InvalidBranch` (a name breaking the naming rule)
  answers `422 invalid_request` with its message.
- `GET /catalog` serves each declaration document as validated plus its `origin`
  (`platform` for `trigger@1.0.0` and `output@1.0.0`, otherwise `package`) and each
  `LlmEntry.document()`; the catalog is read on every request.
- `/v1/chat/completions` (POST) refuses, in order, any `Origin` (`403
  browser_origin_denied`), query parameters, `Content-Encoding` and the
  `OpenAI-Organization`, `OpenAI-Project` and `OpenAI-Beta` headers (`400
  invalid_request`), a missing or malformed bearer grant (`401 invalid_grant`), a media
  type other than `application/json` (`415 unsupported_media_type`), a body beyond the
  bound (`413 request_too_large`) and non-UTF-8 text (`400 invalid_request`). Refusals
  use the LLM service body `{"error": {"code", "message", "type"}}`. Otherwise the raw
  text goes to `LlmGateway.complete` and its status and body are returned unchanged
  (re-encoded with sorted keys).
- `/mcp` (POST) applies the same origin, query, header and bearer checks, then requires
  the grant to name an active call (`RunService.active_call`; otherwise `401
  invalid_grant`) and `MCP-Protocol-Version: 2026-07-28` (`400 unsupported_protocol`),
  before the MCP SDK sees the request. Each request then gets its own stateless SDK
  session manager with JSON responses and the body bound; the SDK's DNS-rebinding
  check is off because browsers are refused and nothing may assume loopback
  ([ADR 0023](../../../../../docs/adr/0023-container-ready-component-boundary.md)). The
  only tool is `platform.report` with input schema `{"kind": enum of the five kinds,
  "content": {}}`, both required, no other properties, and output `{"recorded": true}`.
  Tool refusals are tool errors whose text is `{"code", "message"}`: `unknown_tool`,
  `invalid_arguments` (not exactly `kind` string and `content`, or non-finite numbers),
  `invalid_report` (`InvalidReport`) and `invalid_grant` (the call ended after the
  request was admitted).
- Unexpected failures answer `500 internal_error`: the operator envelope under
  `/api/v2`, otherwise `{"error": {"code", "message", "type": "api_error"}}`; the
  exception still reaches the server log.

| Operator status and code                  | Cause                                                  |
| ----------------------------------------- | ------------------------------------------------------ |
| `400 invalid_json`                        | Body not UTF-8 JSON, duplicate keys, `NaN`, too deep    |
| `404 not_found`                           | No operator route for this path and method              |
| `413 request_too_large`                   | Body beyond `max_body_bytes`                            |
| `415 json_content_required`               | Non-empty body not `application/json`, or encoded       |
| `422 invalid_request`                     | Body not an object, unknown, missing or mistyped fields |
| `422 invalid_query`                       | Unknown, repeated or malformed query parameter          |
| `404 run_not_found`                       | `RunNotFound`                                           |
| `graph_exists`, `graph_not_found`, `version_not_found`, `change_not_found`, `branch_not_found`, `branch_exists`, `too_many_runs`, `invalid_document` | As in the operator API contract; `invalid_document` carries `diagnostics` |

## Porting

Start from `origin/main` (`backend/src/slow_thinker_ii/adapters/http/`):
`_operator_auth.py` and `_operator_boundary.py` (prefix `/api/v2/`),
`_native_input.py`, `_native_errors.py`, `_mcp_gateway.py` and `_mcp_tools.py` (keep
only `platform.report`). Carry and adapt the guard tests from
`backend/tests/integration/operator_http/test_http_guards.py`,
`test_gateway_boundary.py` and `test_managed_mcp_gateway.py`. Not ported: the checks
that operator origins are loopback and that each origin's authority is an allowed host
(the reference configuration serves the interface on another port), and the loopback
host patterns of the MCP endpoint (ADR 0023).

## Acceptance

Route tests with fake services cover every endpoint, status code and error code of the
operator API, authentication and origin checks, body bounds, the model endpoint's
pass-through and the report tool. Branch coverage at least 90%. The tests are the
package `backend/tests/http_adapter`; a test package named `http` on the test path would
shadow the standard library.
