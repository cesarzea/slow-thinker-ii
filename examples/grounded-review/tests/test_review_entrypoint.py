"""The derived package is independently executable through the managed host contract."""

import runpy
import sys
from pathlib import Path

import pytest
import slow_thinker_host
from slow_thinker_host import HostedComponent, encode_json
from support.openai_calls import bootstrap_record


def test_derived_host_requires_a_bootstrap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["review"])
    with pytest.raises(ValueError, match="one trusted bootstrap"):
        runpy.run_module("example_grounded_review", run_name="__main__")


@pytest.mark.parametrize("binding", [False, True])
def test_derived_host_validates_its_managed_client_before_serving(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, binding: bool
) -> None:
    record = bootstrap_record("http://127.0.0.1:123/v1")
    if not binding:
        record["clients"] = {}
    path = tmp_path / "bootstrap.json"
    path.write_text(encode_json(record))
    monkeypatch.setattr(sys, "argv", ["review", str(path)])
    served: list[str] = []

    def serve(component: HostedComponent, name: str, version: str) -> None:
        assert component.operations()[0].name == "generate" and version == "0.1.0.dev1"
        served.append(name)

    monkeypatch.setattr(slow_thinker_host, "run_stdio", serve)
    if binding:
        runpy.run_module("example_grounded_review", run_name="__main__")
        assert served == ["grounded-review"]
    else:
        with pytest.raises(ValueError, match="managed OpenAI binding"):
            runpy.run_module("example_grounded_review", run_name="__main__")
        assert not served
