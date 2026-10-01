"""Resolve feedback from an ordered successful history before scheduling an activation."""

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json

from ._conditional import BoundArguments, CompletedActivation, ConditionalNode, LatestOutput
from ._plans import StaticArgument
from ._pointers import read_pointer


def latest_output(
    binding: LatestOutput, history: tuple[CompletedActivation, ...]
) -> CompletedActivation | None:
    found = next((item for item in reversed(history) if item.node == binding.node), None)
    if found is None and not binding.omit_missing:
        raise ValueError("Required completed activation is unavailable")
    return found


def conditional_arguments(
    node: ConditionalNode, history: tuple[CompletedActivation, ...]
) -> BoundArguments:
    values: JsonObject = {}
    sources: JsonObject = {}
    for binding in node.inputs:
        if binding.name in values:
            raise ValueError("Repeated conditional argument")
        if isinstance(binding, StaticArgument):
            values[binding.name] = decode_json(binding.value_json)
        else:
            source = latest_output(binding, history)
            if source is not None:
                values[binding.name] = read_pointer(
                    decode_json(source.output_json), binding.pointer
                )
                sources[binding.name] = {
                    "node": source.node,
                    "activation_id": source.activation_id,
                    "payload_id": source.payload_id,
                    "pointer": binding.pointer,
                }
    return BoundArguments(encode_json(values), encode_json(sources))


def selected_port(node: ConditionalNode, output_json: str) -> str:
    selector = node.output
    value: JsonValue = selector.constant
    if selector.pointer is not None:
        value = read_pointer(decode_json(output_json), selector.pointer)
    if not isinstance(value, str) or value not in dict(node.routes):
        raise ValueError("The activation did not select a declared output port")
    return value
