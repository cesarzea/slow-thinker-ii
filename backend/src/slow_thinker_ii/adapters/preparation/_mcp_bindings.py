"""Attach outgoing MCP aliases from the same frozen policy used for invocation."""

from dataclasses import replace

from slow_thinker_ii.adapters.catalog import GraphRecord, InstalledPlan
from slow_thinker_ii.application import LimitsProfile, sequence_access
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from ._host_profiles import HostProfile


def bind_mcp(
    installed: InstalledPlan, hosts: dict[str, HostProfile], gateway: str, limits: LimitsProfile
) -> dict[str, HostProfile]:
    graph = GraphRecord.model_validate_json(installed.plan.graph_json)
    policy = sequence_access(installed.plan)
    result: dict[str, HostProfile] = {}
    for identity, profile in hosts.items():
        permitted = policy.discover(identity)
        resources: JsonObject = {}
        for slot, target in graph.components[identity].resources.items():
            resources[slot] = {
                item.address.operation: item.alias
                for item in permitted
                if item.address.instance == target
            }
        clients = json_object(decode_json(profile.binding.clients_json))
        clients["mcp"] = {
            "url": gateway.removesuffix("/v1") + "/mcp",
            "timeout_seconds": limits.call_seconds,
            "close_seconds": limits.shutdown_seconds,
            "resources": resources,
        }
        result[identity] = replace(
            profile, binding=replace(profile.binding, clients_json=encode_json(clients))
        )
    return result
