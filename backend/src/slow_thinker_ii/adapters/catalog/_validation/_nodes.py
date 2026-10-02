"""Validate finite and repeated-activation graph binding semantics without run inputs."""

from slow_thinker_ii.contracts import decode_json, json_object
from slow_thinker_ii.definitions import ResolvedInstance, pointer_tokens

from .._models import BindingRecord, ConditionalConfig, GraphRecord, SequenceConfig
from ._diagnostics import pointer, reject, require
from ._literals import literals
from ._references import operation
from ._schemas import LocalSchemas


def nodes(
    graph: GraphRecord, instances: dict[str, ResolvedInstance], schemas: LocalSchemas
) -> tuple[str, ...]:
    config = graph.components[graph.controller.component].config
    if graph.execution_profile == "sequence":
        steps = tuple(SequenceConfig.model_validate(config).steps)
        require(
            len(set(steps)) == len(steps) and set(steps) == set(graph.nodes),
            "/controller",
            "The finite sequence must include every node exactly once.",
        )
    else:
        steps = tuple(graph.nodes)
        conditional_routes(graph, ConditionalConfig.model_validate(config))
    earlier: set[str] = set()
    for identity in steps:
        validate_node(identity, graph, instances, schemas, earlier)
        earlier.add(identity)
    final_binding(graph, earlier)
    return steps


def validate_node(
    identity: str,
    graph: GraphRecord,
    instances: dict[str, ResolvedInstance],
    schemas: LocalSchemas,
    earlier: set[str],
) -> None:
    node = graph.nodes[identity]
    parts = ("nodes", identity)
    contract = operation(instances, node.component, node.operation, pointer(parts))
    if graph.execution_profile == "sequence":
        require(
            node.output is None,
            pointer((*parts, "output")),
            "Sequence nodes cannot declare output selectors.",
        )
    for name, value in node.inputs.items():
        binding(graph, value, earlier, (*parts, "inputs", name))
    literals(
        node.inputs,
        json_object(decode_json(contract.input_schema_json)),
        schemas,
        (*parts, "inputs"),
    )


def binding(
    graph: GraphRecord, value: BindingRecord, earlier: set[str], parts: tuple[str, ...]
) -> None:
    path = pointer(parts)
    if value.source != "literal":
        valid_pointer(value.pointer, pointer((*parts, "pointer")))
    if graph.execution_profile == "sequence":
        require(
            value.activation is None and value.missing is None,
            path,
            "Sequence bindings cannot select repeated activations.",
        )
        if value.source == "node_output":
            require(value.node in earlier, path, "Sequence outputs must reference an earlier node.")
    elif value.source == "node_output":
        require(
            value.node in graph.nodes and value.activation == "latest_completed",
            path,
            "Conditional outputs must select the latest completed activation of a declared node.",
        )


def conditional_routes(graph: GraphRecord, config: ConditionalConfig) -> None:
    require(
        config.entry in graph.nodes and set(config.routes) == set(graph.nodes),
        "/controller",
        "Conditional routes must include the entry and cover every declared node.",
    )
    for identity, routes in config.routes.items():
        path = pointer(("nodes", identity, "output"))
        require(bool(routes) and all(routes), path, "Each node must declare nonempty output ports.")
        require(
            all(target is None or target in graph.nodes for target in routes.values()),
            path,
            "Route destinations must identify declared nodes or completion.",
        )
        selector = graph.nodes[identity].output
        require(selector is not None, path, "Conditional nodes require an output selector.")
        assert selector is not None
        if selector.constant is not None:
            require(
                selector.constant in routes,
                path,
                "Constant output selector must identify a declared port.",
            )
        else:
            assert selector.pointer is not None
            valid_pointer(selector.pointer, path)


def final_binding(graph: GraphRecord, earlier: set[str]) -> None:
    if graph.result is None:
        require(
            graph.execution_profile == "sequence",
            "/result",
            "Conditional graphs require a final output binding.",
        )
        return
    binding(graph, graph.result, earlier, ("result",))
    if graph.execution_profile == "bounded-conditional":
        require(
            graph.result.source == "node_output" and graph.result.missing is None,
            "/result",
            "Final output must select a required completed node activation.",
        )


def valid_pointer(value: str, path: str) -> None:
    try:
        pointer_tokens(value)
    except ValueError:
        reject(path, "Value must be a valid JSON Pointer.")
