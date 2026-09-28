"""Frozen per-run routing maps do not infer permissions from resource bindings."""

from ._values import AccessDenied, OperationAddress, Permission, PublishedOperation


class AccessPolicy:
    def __init__(
        self,
        operations: tuple[OperationAddress, ...],
        permissions: tuple[Permission, ...],
        scheduled: tuple[OperationAddress, ...],
    ) -> None:
        declared = frozenset(operations)
        instances = {item.instance for item in declared}
        if not declared or len(declared) != len(operations):
            raise ValueError("Declare unique operations for the run")
        if any(item.caller not in instances or item.target not in declared for item in permissions):
            raise ValueError("Permissions must reference declared participants and operations")
        if not frozenset(scheduled) <= declared:
            raise ValueError("Scheduled operations must be declared")
        self._permissions = frozenset(permissions)
        self._scheduled = frozenset(scheduled)
        self._aliases = {
            f"op_{index:04d}": address for index, address in enumerate(sorted(declared), start=1)
        }

    def discover(self, caller: str) -> tuple[PublishedOperation, ...]:
        return tuple(
            PublishedOperation(alias, address)
            for alias, address in self._aliases.items()
            if Permission(caller, address) in self._permissions
        )

    def resolve(self, caller: str, alias: str) -> OperationAddress:
        address = self._aliases.get(alias)
        if address is None or Permission(caller, address) not in self._permissions:
            raise AccessDenied("operation_denied")
        return address

    def require_scheduled(self, address: OperationAddress) -> None:
        if address not in self._scheduled:
            raise AccessDenied("scheduler_operation_denied")
