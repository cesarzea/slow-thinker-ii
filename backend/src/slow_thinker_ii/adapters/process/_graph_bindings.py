"""Trusted host transport and billing bindings are distinct from graph-authored data."""

import math
from dataclasses import dataclass, field

from slow_thinker_ii.application import PricingPolicy
from slow_thinker_ii.contracts import decode_json, json_object

from ._secrets import ProcessSecret


@dataclass(frozen=True)
class HostBinding:
    clients_json: str = "{}"
    pricing: tuple[tuple[str, PricingPolicy], ...] = ()
    secrets: tuple[ProcessSecret, ...] = field(default=(), repr=False)

    def __post_init__(self) -> None:
        json_object(decode_json(self.clients_json))
        if len({name for name, _ in self.pricing}) != len(self.pricing):
            raise ValueError("A host operation can have only one price policy")


@dataclass(frozen=True)
class HostLimits:
    startup_seconds: float
    shutdown_seconds: float
    max_message_bytes: int

    def __post_init__(self) -> None:
        for value in (self.startup_seconds, self.shutdown_seconds):
            if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                raise ValueError("Host time limits must be finite and positive")
        if type(self.max_message_bytes) is not int or self.max_message_bytes <= 0:
            raise ValueError("Host message limit must be a positive integer")
