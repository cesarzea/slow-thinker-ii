"""Real authority, durable admission and MCP gateway wrap standard public tool hosts."""

from pathlib import Path

from fastapi import FastAPI
from slow_thinker_calculator import CalculatorHost
from slow_thinker_host import HostedComponent, Invocation, McpEndpoint, McpResource
from slow_thinker_ii.access import AccessPolicy, OperationAddress, Permission
from slow_thinker_ii.adapters.http import mcp_router
from slow_thinker_ii.application import (
    GatewayOperation,
    ManagedCalls,
    OperationPort,
    OperationReply,
    PreparedOperation,
)
from slow_thinker_ii.application._managed_gateway import ManagedGateway
from slow_thinker_ii.application._run_evidence import RunEvidence
from slow_thinker_ii.contracts import (
    OperationContract,
    OperationResult,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_key_value_memory import KeyValueMemoryHost
from support.authority import alias
from support.managed_calls import FixtureOperation, RealClock
from support.run_admission import RunCase, run_case

TOP = OperationAddress("agent", "invoke")
WORKER = OperationAddress("worker", "work")
GET = OperationAddress("memory", "get")
PUT = OperationAddress("memory", "put")
CALCULATE = OperationAddress("calculator", "calculate")


class HostedPort:
    def __init__(self, host: HostedComponent, operation: str) -> None:
        self.host, self.operation = host, operation

    def prepare(self, arguments_json: str) -> PreparedOperation:
        return PreparedOperation(arguments_json, None)

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        reply = await self.host.invoke(
            self.operation, json_object(decode_json(arguments_json)), Invocation(grant, deadline)
        )
        return OperationReply(OperationResult(encode_json(reply.value), reply.is_error))


class MediatedCase:
    def __init__(
        self,
        directory: Path,
        *,
        denied: bool = False,
        worker: FixtureOperation | None = None,
        overrides: dict[OperationAddress, OperationPort] | None = None,
        permissions: tuple[Permission, ...] = (),
    ) -> None:
        addresses = (TOP, WORKER, GET, PUT, CALCULATE, *(overrides or {}))
        rules = tuple(
            Permission("agent", target)
            for target in (WORKER, GET, PUT, CALCULATE)
            if not denied or target != WORKER
        )
        policy = AccessPolicy(tuple(dict.fromkeys(addresses)), (*rules, *permissions), (TOP,))
        self.run = run_case(directory / "platform.sqlite3", clock=RealClock(), policy=policy)
        self.parent = self.run.authority.schedule(TOP, node_id="draft")
        self.run.service.reserve(self.parent.token, "{}", None)
        self.run.service.authorize(self.parent.token)
        self.worker = worker or FixtureOperation()
        self.worker.result = OperationResult('{"value":{"answer":96}}', False)
        operations = hosted_operations(directory, self.worker)
        operations.update(overrides or {})
        self.app = managed_app(self.run, operations)
        self.denied = denied

    def endpoint(self, port: int) -> McpEndpoint:
        resources = tuple(
            McpResource(
                slot,
                op,
                "blocked"
                if self.denied and target == WORKER
                else alias(self.run.authority, self.parent.token, target),
            )
            for slot, op, target in (
                ("worker", "work", WORKER),
                ("memory", "get", GET),
                ("memory", "put", PUT),
                ("calculator", "calculate", CALCULATE),
            )
        )
        return McpEndpoint(f"http://127.0.0.1:{port}/mcp", 5, 1, resources)


def hosted_operations(
    directory: Path, worker: FixtureOperation
) -> dict[OperationAddress, OperationPort]:
    memory = KeyValueMemoryHost(
        {"namespace": "shared"},
        KeyValueMemoryHost.describe({"namespace": "shared"}),
        directory / "memory.sqlite3",
        "shared",
    )
    calculator = CalculatorHost({}, CalculatorHost.describe({}))
    return {
        WORKER: worker,
        GET: HostedPort(memory, "get"),
        PUT: HostedPort(memory, "put"),
        CALCULATE: HostedPort(calculator, "calculate"),
    }


def managed_app(case: RunCase, operations: dict[OperationAddress, OperationPort]) -> FastAPI:
    calls = ManagedCalls(case.authority, case.service, operations)
    records = tuple(
        GatewayOperation(
            address, OperationContract(address.operation, '{"type":"object"}', '{"type":"object"}')
        )
        for address in operations
    )
    gateway = ManagedGateway(
        case.authority, calls, records, RunEvidence(case.authority, case.store, 65536)
    )
    app = FastAPI()
    app.include_router(mcp_router(gateway))
    return app
