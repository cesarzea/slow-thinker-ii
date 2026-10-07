# access: specification

Implements invocation grants for [derived authorization](../../../../docs/adr/0018-derived-authorization.md).
A grant identifies one call of one activation. Pure domain code.

## Public interface (`slow_thinker_ii.access`)

```python
@dataclass(frozen=True)
class Caller:
    run_id: str
    node_id: str
    position: Literal["node", "output", "memory"]
    activation_id: str

class Grants:
    def __init__(self, clock: Callable[[], float]) -> None     # monotonic seconds
    def issue(self, caller: Caller, ttl_seconds: float) -> str  # ttl > 0
    def resolve(self, token: str) -> Caller | None              # None when unknown, revoked or expired
    def revoke(self, token: str) -> None                        # idempotent
    def revoke_run(self, run_id: str) -> None
    def active(self, run_id: str) -> int
```

## Behaviour

- Tokens are `secrets.token_urlsafe(32)`. Only SHA-256 digests are stored; a token is
  never logged or returned twice.
- Operations are safe under concurrent use from the event loop and from worker
  threads (one `threading.Lock`).
- `issue` rejects a time to live that is not greater than zero (including NaN) with
  `ValueError`. A grant expires when the clock reaches its issue time plus the time to
  live: at that exact boundary it no longer resolves.
- Expired grants are removed lazily on `resolve` and on `issue`; `active` counts the
  unexpired grants of a run.
- The package exposes only `Caller` and `Grants`: authorization decisions come from the
  run plan in the application layer.

## Acceptance

Tests cover issue and resolve, revocation, run-wide revocation, expiry at the exact
boundary, unknown tokens, digest-only storage and concurrent issue and revoke.
Branch coverage 100%.
