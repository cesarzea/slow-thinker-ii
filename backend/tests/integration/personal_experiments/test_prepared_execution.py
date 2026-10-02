"""Saved revisions prepare through production and execute with explicit simulated runtime ports."""

from dataclasses import replace
from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteOperatorStore, SqliteRunStore
from slow_thinker_ii.application import PreparedWorkflow
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.managed_calls import RealClock
from support.personal_experiments.definitions import set_field, variant
from support.personal_experiments.preparation import library_preparer
from support.personal_experiments.runtime import PreparedFixtureEnvironment, prepared_runtime
from support.personal_library import personal_library
from support.preparation import NOW, PreparationCase
from support.process_fixture import assert_reaped

INSTRUCTIONS = "Use this exact saved revision and preserve its requirements."
REVISION = "personal α / prepared " + "x" * 140


def saved_source() -> str:
    value = variant(REVISION, INSTRUCTIONS)
    set_field(value, "/components/proposer/config", "parameters", {"max_completion_tokens": 8})
    return encode_json(value)


async def prepare_saved(
    case: PreparationCase,
) -> tuple[PreparedWorkflow, SqliteOperatorStore, RealClock]:
    experiments = personal_library(case.database)
    experiments.save(saved_source())
    assert case.configuration is not None
    clock = RealClock()
    commands = SqliteOperatorStore(case.database, 1_048_576, clock, lambda: NOW)
    commands.configure(case.configuration)
    receipt = commands.create_session("session-command", "Personal preparation").receipt
    assert receipt.target_id is not None
    intent = replace(case.intent, session_id=receipt.target_id, graph_revision=REVISION)
    workflow = await library_preparer(case, experiments).prepare(intent, "personal-runtime")
    return workflow, commands, clock


async def test_production_preparer_selects_personal_revision_and_freezes_config(
    preparation: PreparationCase,
) -> None:
    workflow, _, _ = await prepare_saved(preparation)
    snapshot = json_object(decode_json(workflow.start.snapshot_json))
    assert snapshot["definition"] == decode_json(saved_source())
    config = json_object(json_object(json_object(snapshot["instances"])["proposer"])["config"])
    components = json_object(json_object(snapshot["definition"])["components"])
    assert config == json_object(components["proposer"])["config"]
    assert config["instructions"] == INSTRUCTIONS
    assert workflow.start.intent.graph_revision == REVISION
    assert workflow.environment.report() == "[]"
    assert not (preparation.directory / "runtime").exists()
    assert "synthetic-preparation-key" not in workflow.start.record_json()


async def test_prepared_program_executes_real_sequence_llm_and_preserves_old_run(
    preparation: PreparationCase, tmp_path: Path
) -> None:
    workflow, commands, clock = await prepare_saved(preparation)
    receipt = commands.admit("admit-personal", workflow.start).receipt
    assert receipt.disposition == "accepted" and receipt.target_id is not None
    store = SqliteRunStore(preparation.database, 1_048_576)
    with store.begin() as transaction:
        admitted = transaction.run(receipt.target_id)
    environment = PreparedFixtureEnvironment(tmp_path, workflow)
    result = await prepared_runtime(workflow, admitted, store, environment, clock).execute(
        workflow.program
    )
    assert result.state == "completed" and result.graph_revision == REVISION
    assert_reaped(environment.sequence.process, forced=False)
    assert_sdk_messages(environment)
    assert_retained_run(store, result.run_id, preparation)
    assert admitted.snapshot_json == workflow.start.record_json()


def assert_retained_run(store: SqliteRunStore, run_id: str, case: PreparationCase) -> None:
    with store.begin() as transaction:
        previous = transaction.run(run_id), transaction.events(run_id)
        finished = next(event for event in previous[1] if event.event == "run.finished")
        output = json_object(decode_json(finished.payload_json))["output_json"]
        assert isinstance(output, str) and '"value":"success"' in output
        calls = [
            transaction.call(event.call_id)
            for event in previous[1]
            if event.event == "call.requested" and event.call_id
        ]
        assert len(calls) == 4 and sum(call.prepared.charge is not None for call in calls) == 1
    newer = variant("newer revision", "A changed later instruction.")
    personal_library(case.database).save(encode_json(newer))
    with store.begin() as transaction:
        assert (transaction.run(run_id), transaction.events(run_id)) == previous
        assert [transaction.call(call.prepared.context.call_id) for call in calls] == calls


def assert_sdk_messages(environment: PreparedFixtureEnvironment) -> None:
    requests = environment.transport.stub.requests
    assert len(requests) == 1
    assert requests[0]["max_completion_tokens"] == 8
    assert requests[0]["model"] == environment.agent.alias
    messages = requests[0]["messages"]
    assert isinstance(messages, list)
    assert json_object(messages[0]) == {"role": "system", "content": INSTRUCTIONS}
    assert json_object(messages[-1]) == {
        "role": "user",
        "content": '{"problem":"Test preparation"}',
    }
    assert len(environment.model.calls) == 1
