"""Ordinary RoutedCall composition receives its own filtered managed invocation grant."""

from slow_thinker_host import Invocation, McpEndpoint, McpResource
from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.application import OperationReply, PreparedOperation
from slow_thinker_ii.contracts import OperationResult, decode_json, encode_json, json_object
from slow_thinker_routed_call import RoutedCall, parse_config
from support.authority import alias
from support.run_admission import RunCase

ENGINE = OperationAddress("engine", "work")
ROUTER = OperationAddress("router", "route")


class RoutedPort:
    def __init__(self) -> None:
        self.case: RunCase | None = None
        self.port = 0

    def prepare(self, arguments_json: str) -> PreparedOperation:
        return PreparedOperation(arguments_json, None)

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        assert self.case is not None
        config = parse_config(
            {
                "input_schema": {"type": "object"},
                "worker_operation": "work",
                "worker_output_schema": {"type": "object"},
                "router_input_pointer": "/value",
                "outputs": ["done"],
            }
        )
        endpoint = McpEndpoint(
            f"http://127.0.0.1:{self.port}/mcp",
            5,
            1,
            (
                McpResource("worker", "work", alias(self.case.authority, grant, ENGINE)),
                McpResource("router", "route", alias(self.case.authority, grant, ROUTER)),
            ),
        )
        reply = await RoutedCall(config, endpoint).invoke(
            json_object(decode_json(arguments_json)), Invocation(grant, deadline)
        )
        return OperationReply(OperationResult(encode_json(reply.value), reply.is_error))
