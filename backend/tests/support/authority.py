"""A deterministic clock and explicit graph permissions for authority tests."""

from slow_thinker_ii.access import (
    AccessPolicy,
    CallAuthority,
    CallLimits,
    OperationAddress,
    Permission,
)

PROPOSER = OperationAddress("proposer", "generate")
REVIEWER = OperationAddress("reviewer", "generate")
MODEL = OperationAddress("model", "complete")
MEMORY = OperationAddress("memory", "read")


class Clock:
    def __init__(self) -> None:
        self.now = 10.0

    def __call__(self) -> float:
        return self.now


def authority(
    clock: Clock,
    *,
    calls: int = 10,
    depth: int = 3,
    seconds: float = 20,
    deadline: float = 100,
    policy: AccessPolicy | None = None,
    revision: str = "revision",
) -> CallAuthority:
    policy = policy or AccessPolicy(
        (PROPOSER, REVIEWER, MODEL, MEMORY),
        (
            Permission("proposer", REVIEWER),
            Permission("reviewer", MODEL),
            Permission("reviewer", PROPOSER),
        ),
        (PROPOSER, REVIEWER),
    )
    return CallAuthority(
        "run", revision, policy, CallLimits(calls, depth, seconds), deadline, clock
    )


def alias(service: CallAuthority, token: str, address: OperationAddress) -> str:
    return next(item.alias for item in service.discover(token) if item.address == address)
