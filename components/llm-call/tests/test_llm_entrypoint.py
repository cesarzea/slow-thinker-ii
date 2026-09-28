"""Host entrypoint validates trusted data before serving operations."""

import runpy
import sys
from pathlib import Path

import pytest
import slow_thinker_host
from slow_thinker_host import HostedComponent, encode_json
from support.openai_calls import bootstrap_record


def bootstrap(path: Path, *, binding: bool) -> None:
    record = bootstrap_record("http://127.0.0.1/v1/")
    if not binding:
        record["clients"] = {}
    path.write_text(encode_json(record))


def test_entrypoint_requires_one_bootstrap_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["llm-call"])
    with pytest.raises(ValueError, match="one trusted bootstrap"):
        runpy.run_module("slow_thinker_llm_call", run_name="__main__")


@pytest.mark.parametrize("binding", [False, True])
def test_entrypoint_validates_binding_before_serving(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    binding: bool,
) -> None:
    path = tmp_path / "bootstrap.json"
    bootstrap(path, binding=binding)
    monkeypatch.setattr(sys, "argv", ["llm-call", str(path)])
    served: list[str] = []

    def serve(component: HostedComponent, name: str, version: str) -> None:
        assert component.operations()[0].name == "generate"
        assert version == "0.1.0.dev1"
        served.append(name)

    monkeypatch.setattr(slow_thinker_host, "run_stdio", serve)
    if binding:
        runpy.run_module("slow_thinker_llm_call", run_name="__main__")
        assert served == ["llm-call"]
    else:
        with pytest.raises(ValueError, match="managed OpenAI binding"):
            runpy.run_module("slow_thinker_llm_call", run_name="__main__")
        assert not served
