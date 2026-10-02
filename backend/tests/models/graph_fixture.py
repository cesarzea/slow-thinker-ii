"""A two-agent graph assigns independent model resources without altering shared fixtures."""

from slow_thinker_ii.adapters.preparation import HostProfile, HostRequest, PlainHostAdapter
from slow_thinker_ii.contracts import JsonValue, decode_json, encode_json, json_object

from .preparation_fixture import Definitions


class RuntimeRecorder:
    def __init__(self) -> None:
        self.requests: list[HostRequest] = []

    def configure(self, request: HostRequest) -> HostProfile:
        self.requests.append(request)
        return PlainHostAdapter().configure(request)


def two_agent_graph(definitions: Definitions) -> None:
    source = json_object(decode_json(definitions.source))
    components = json_object(source["components"])
    reviewer = json_object(components["proposer"])
    reviewer["resources"] = {"model": "openai-model"}
    openai = json_object(components["model"])
    openai["config"] = {"provider_profile": "openai-luna", "model": "openai-alias"}
    components.update(reviewer=reviewer, **{"openai-model": openai})
    controller = json_object(components["sequence"])
    controller["config"] = {"steps": ["draft", "review"]}
    components["sequence"] = controller
    source["components"] = components
    nodes = json_object(source["nodes"])
    review = json_object(nodes["draft"])
    review["component"] = "reviewer"
    source["nodes"] = {**nodes, "review": review}
    permissions: list[JsonValue] = [
        {"caller": "proposer", "target": "model", "operations": ["complete"]},
        {"caller": "reviewer", "target": "openai-model", "operations": ["complete"]},
    ]
    source["permissions"] = permissions
    definitions.source = encode_json(source)
