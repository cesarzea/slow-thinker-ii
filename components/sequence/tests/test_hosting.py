"""The controller binding rejects unsupported state and exposes deterministic decisions."""

import pytest
from slow_thinker_host import Invocation, JsonObject, Operation
from slow_thinker_sequence import SequenceHost

OPERATION = Operation("next", {}, {})
INVALID_CONFIGS: list[JsonObject] = [{}, {"steps": "draft"}, {"steps": [1]}, {"steps": []}]


async def test_host_calls_use_explicit_completion_state() -> None:
    host = SequenceHost({"steps": ["draft"]}, OPERATION)
    assert host.operations() == (OPERATION,)
    first = await host.invoke("next", {"completed_nodes": []}, Invocation("first"))
    last = await host.invoke("next", {"completed_nodes": ["draft"]}, Invocation("second"))
    assert first.value == {"action": "schedule", "nodes": ["draft"]}
    assert last.value == {"action": "complete", "nodes": []}


@pytest.mark.parametrize("config", INVALID_CONFIGS)
def test_host_rejects_unsupported_configuration(config: JsonObject) -> None:
    with pytest.raises(ValueError):
        SequenceHost(config, OPERATION)


def test_host_rejects_an_unexpected_operation() -> None:
    with pytest.raises(ValueError):
        SequenceHost({"steps": ["draft"]}, Operation("other", {}, {}))


async def test_host_rejects_unsupported_invocation() -> None:
    host = SequenceHost({"steps": ["draft"]}, OPERATION)
    with pytest.raises(ValueError):
        await host.invoke("other", {"completed_nodes": []}, Invocation("first"))
    with pytest.raises(ValueError):
        await host.invoke("next", {"unknown": []}, Invocation("first"))
