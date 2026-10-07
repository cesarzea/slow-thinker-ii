"""Invocation grants: one bearer token per call of an activation, stored only as a digest."""

import hashlib
import secrets
import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Caller:
    run_id: str
    node_id: str
    position: Literal["node", "output", "memory"]
    activation_id: str


@dataclass(frozen=True)
class _Grant:
    caller: Caller
    deadline: float


def _digest(token: str) -> bytes:
    return hashlib.sha256(token.encode()).digest()


class Grants:
    """Issue, resolve and revoke grants; safe from the event loop and worker threads."""

    def __init__(self, clock: Callable[[], float]) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._grants: dict[bytes, _Grant] = {}

    def issue(self, caller: Caller, ttl_seconds: float) -> str:
        if not ttl_seconds > 0:
            raise ValueError("A grant requires a positive time to live")
        token = secrets.token_urlsafe(32)
        with self._lock:
            now = self._clock()
            self._remove_expired(now)
            self._grants[_digest(token)] = _Grant(caller, now + ttl_seconds)
        return token

    def resolve(self, token: str) -> Caller | None:
        digest = _digest(token)
        with self._lock:
            self._remove_expired(self._clock())
            grant = self._grants.get(digest)
        return None if grant is None else grant.caller

    def revoke(self, token: str) -> None:
        digest = _digest(token)
        with self._lock:
            self._grants.pop(digest, None)

    def revoke_run(self, run_id: str) -> None:
        with self._lock:
            self._remove(lambda grant: grant.caller.run_id == run_id)

    def active(self, run_id: str) -> int:
        with self._lock:
            now = self._clock()
            grants = [grant for grant in self._grants.values() if grant.caller.run_id == run_id]
            return sum(1 for grant in grants if grant.deadline > now)

    def _remove_expired(self, now: float) -> None:
        self._remove(lambda grant: grant.deadline <= now)

    def _remove(self, condition: Callable[[_Grant], bool]) -> None:
        for digest in [key for key, grant in self._grants.items() if condition(grant)]:
            del self._grants[digest]
