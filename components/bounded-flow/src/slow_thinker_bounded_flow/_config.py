"""Freeze a complete declared route table with a configured activation bound."""

from slow_thinker_host import JsonObject, json_object

from ._types import BoundedFlowConfig, FlowRoute


def _routes(value: JsonObject) -> tuple[FlowRoute, ...]:
    if not value or any(not node.strip() for node in value):
        raise ValueError("BoundedFlow requires nonempty declared nodes")
    routes: list[FlowRoute] = []
    for node, ports in value.items():
        declared = json_object(ports)
        if not declared or any(not port.strip() for port in declared):
            raise ValueError("Each node requires nonempty declared ports")
        for port, target in declared.items():
            if target is not None and (not isinstance(target, str) or target not in value):
                raise ValueError("Route target is not a declared node")
            routes.append(FlowRoute(node, port, target))
    return tuple(routes)


def parse_config(value: JsonObject) -> BoundedFlowConfig:
    if set(value) != {"entry", "routes", "max_activations"}:
        raise ValueError("Unsupported BoundedFlow configuration fields")
    entry, maximum = value["entry"], value["max_activations"]
    topology = json_object(value["routes"])
    if not isinstance(entry, str) or entry not in topology or not entry.strip():
        raise ValueError("Entry must name a declared node")
    if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum <= 0:
        raise ValueError("max_activations must be a positive integer")
    return BoundedFlowConfig(entry, _routes(topology), maximum)


def validated_config(config: BoundedFlowConfig) -> BoundedFlowConfig:
    routes: JsonObject = {}
    seen: set[tuple[str, str]] = set()
    for route in config.routes:
        key = (route.node, route.port)
        if key in seen:
            raise ValueError("Duplicate BoundedFlow route")
        seen.add(key)
        ports = json_object(routes.get(route.node, {}))
        ports[route.port] = route.target
        routes[route.node] = ports
    return parse_config(
        {
            "entry": config.entry,
            "routes": routes,
            "max_activations": config.max_activations,
        }
    )
