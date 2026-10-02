"""Independent subclass preserves inherited generation and explicit resource context."""

import runpy
from pathlib import Path

import pytest
from example_resource_agent import ResourceAgent
from slow_thinker_host import JsonObject, json_object
from slow_thinker_llm_call import effective_operation
from support.openai_calls import ModelStub, completion, config

from tooling.tests.test_external_entry_support import invalid_argv, invoke_entry


async def test_inherited_generation_has_context_and_native_request() -> None:
    model = ModelStub(completion("answer"))
    async with model.client() as client:
        agent = ResourceAgent(config(), client, "bound-model")
        result = await agent.generate({"memory": {"n": 9007199254740993}, "calculation": "96"})
    assert result == {"status": "ok", "format": "text", "value": "answer"}
    messages = model.requests[0]["messages"]
    assert isinstance(messages, list) and len(messages) == 3
    assert "9007199254740993" in str(messages[-1])
    assert "explicitly supplied memory" in str(messages[1])
    assert len(model.requests) == 1


def test_external_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    invalid_argv("example_resource_agent", monkeypatch)
    settings = config()
    clients: JsonObject = {
        "openai": {
            "base_url": "http://127.0.0.1:8000/v1",
            "model": "bound-model",
            "timeout_seconds": 3,
            "close_seconds": 1,
        }
    }
    assert invoke_entry(
        "example_resource_agent",
        json_object(settings),
        (effective_operation(settings),),
        clients,
        tmp_path,
        monkeypatch,
    ) == ["resource-agent"]
    for bindings in ({}, {**clients, "unknown": {}}):
        with pytest.raises(ValueError):
            invoke_entry(
                "example_resource_agent",
                json_object(settings),
                (effective_operation(settings),),
                bindings,
                tmp_path,
                monkeypatch,
            )


def test_entrypoint_definition_does_not_launch() -> None:
    module = runpy.run_module("example_resource_agent.__main__", run_name="description_only")
    assert callable(module["main"])
