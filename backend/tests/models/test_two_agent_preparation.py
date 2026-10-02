"""Both graph agents freeze independent native configuration, bindings and tariff evidence."""

from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteModelTariffReader
from slow_thinker_ii.contracts import decode_json, json_object

from models.graph_fixture import RuntimeRecorder, two_agent_graph
from models.preparation_fixture import ModelInstallations, model_preparer, preparation_case
from models.test_preparation import installed_models

__all__ = ["installed_models"]


async def test_same_graph_agents_select_independent_providers(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    case, definitions = await preparation_case(tmp_path, installed_models)
    two_agent_graph(definitions)
    recorder = RuntimeRecorder()
    case.adapters["mcp"] = recorder
    workflow = await model_preparer(
        case, definitions, SqliteModelTariffReader(case.database)
    ).prepare(case.intent, "shared-runtime-id")
    instances = json_object(json_object(decode_json(workflow.start.snapshot_json))["instances"])
    deepseek, openai = json_object(instances["model"]), json_object(instances["openai-model"])
    assert json_object(deepseek["config"])["model"] == "deepseek-flash"
    assert json_object(openai["config"])["model"] == "gpt-6-luna"
    assert (
        json_object(deepseek["model_tariff"])["digest"]
        != json_object(openai["model_tariff"])["digest"]
    )
    assert {
        (binding.caller, binding.model_alias, binding.target.instance)
        for binding in workflow.models
    } == {("proposer", "deepseek-alias", "model"), ("reviewer", "openai-alias", "openai-model")}
    assert len(recorder.requests) == 1 and recorder.requests[0].runtime_id == "shared-runtime-id"
