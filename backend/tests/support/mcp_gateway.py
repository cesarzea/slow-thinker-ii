"""Real MCP HTTP service with an authenticated persisted parent and a deterministic child."""

from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI
from slow_thinker_host import Invocation, McpEndpoint
from slow_thinker_ii.adapters.http import mcp_router, openai_router
from slow_thinker_ii.application import GatewayOperation
from slow_thinker_ii.application._managed_gateway import ManagedGateway
from slow_thinker_ii.application._run_evidence import RunEvidence
from slow_thinker_ii.contracts import OperationContract

from .authority import MODEL
from .native_gateway import NativeCase, native_case


@dataclass(frozen=True)
class McpCase:
    native: NativeCase
    service: ManagedGateway
    app: FastAPI

    def endpoint(self, port: int) -> McpEndpoint:
        return McpEndpoint(f"http://127.0.0.1:{port}/mcp", 5, 1, ())

    def invocation(self) -> Invocation:
        return Invocation(self.native.parent.token, self.native.parent.context.deadline)


def mcp_case(directory: Path) -> McpCase:
    native = native_case(directory)
    evidence = RunEvidence(native.run.authority, native.run.store, 1_048_576)
    contract = OperationContract(
        "complete",
        '{"type":"object","properties":{"request":{"type":"object"}},"required":["request"]}',
        '{"type":"object"}',
    )
    service = ManagedGateway(
        native.run.authority, native.calls, (GatewayOperation(MODEL, contract),), evidence
    )
    app = FastAPI()
    app.include_router(mcp_router(service))
    app.include_router(openai_router(native.gateway))
    return McpCase(native, service, app)
