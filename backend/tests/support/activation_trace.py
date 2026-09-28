"""Repeated uses of one operation create separate activation identities and bound inputs."""

from slow_thinker_ii.application import ManagedCalls
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from .coordinator import TARGET
from .operator_http import HttpCase, payload
from .operator_trace import completed_trace, event_items


class RepeatedProgram:
    def __init__(self, repeat_first: bool = False) -> None:
        self.repeat_first = repeat_first

    async def execute(self, calls: ManagedCalls) -> str:
        first = await calls.schedule(TARGET, '{"p":"test"}', node_id="first")
        if self.repeat_first:
            first = await calls.schedule(TARGET, '{"p":"test"}', node_id="first")
        previous = json_object(decode_json(first.result.payload_json))["done"]
        result = await calls.schedule(TARGET, encode_json({"previous": previous}), node_id="second")
        return result.result.payload_json


async def repeated_trace(api: HttpCase, repeat_first: bool = False) -> tuple[str, list[JsonObject]]:
    api.case.preparer.program = RepeatedProgram(repeat_first)
    api.case.preparer.snapshot_json = encode_json(
        {
            "definition": {
                "nodes": {
                    "first": {"inputs": {"p": {"source": "run_input", "pointer": "/p"}}},
                    "second": {
                        "inputs": {
                            "previous": {
                                "source": "node_output",
                                "node": "first",
                                "pointer": "/done",
                            }
                        }
                    },
                }
            }
        }
    )
    run, _ = await completed_trace(api)
    calls = [
        item["call_id"] for item in await event_items(api, run) if item["event"] == "call.requested"
    ]
    return run, [
        payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}")) for call in calls
    ]
