"""Bind exactly the arguments declared for this node from retained successful outputs."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json

from ._plans import PlanNode, StaticArgument
from ._pointers import read_pointer


def node_arguments(node: PlanNode, outputs: Mapping[str, str]) -> str:
    values: JsonObject = {}
    for binding in node.inputs:
        if binding.name in values:
            raise ValueError("Repeated node argument")
        if isinstance(binding, StaticArgument):
            value = decode_json(binding.value_json)
        else:
            if binding.node not in outputs:
                raise ValueError("Required node output is unavailable")
            value = read_pointer(decode_json(outputs[binding.node]), binding.pointer)
        values[binding.name] = value
    return encode_json(values)
