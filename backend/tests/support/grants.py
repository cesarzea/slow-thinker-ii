"""An `engine.GrantIssuer` over the real `access.Grants` that keeps what it issued and revoked."""

from dataclasses import dataclass, field

from slow_thinker_ii.access import Caller, Grants

from .clock import FakeClock


@dataclass(frozen=True)
class Issued:
    caller: Caller
    ttl_seconds: float
    token: str = field(repr=False)


class RecordingGrants:
    """Issues real grants (resolvable through `grants`) and records every issue and revocation."""

    def __init__(self, clock: FakeClock) -> None:
        self.grants = Grants(clock.monotonic)
        self.issued: list[Issued] = []
        self.revoked: list[str] = []

    def issue(self, caller: Caller, ttl_seconds: float) -> str:
        token = self.grants.issue(caller, ttl_seconds)
        self.issued.append(Issued(caller, ttl_seconds, token))
        return token

    def revoke(self, token: str) -> None:
        self.revoked.append(token)
        self.grants.revoke(token)
