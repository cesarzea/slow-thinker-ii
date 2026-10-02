"""Evidence assertions cover native bodies, headers and component transport intervals."""

import time

from model_provider_fixture import config, response
from slow_thinker_host import ToolReply, json_object, validate_value
from slow_thinker_model_provider import effective_operation


def assert_native_evidence(result: ToolReply, status: int, started: float) -> None:
    validate_value(result.value, effective_operation(config()).output_schema)
    assert result.is_error == (status != 200)
    timing = json_object(result.value["transport"])
    assert (
        started
        <= float(str(timing["request_started_at"]))
        <= float(str(timing["response_finished_at"]))
        <= time.time()
    )
    assert json_object(result.value["response_headers"])["x-extra"] == "kept"
    evidence = result.value if status == 200 else json_object(result.value["error"])
    assert evidence["request_id"] == "req-native"
    if status == 200:
        assert result.value["response"] == response()
    else:
        assert evidence["status"] == status and evidence["origin"] == "provider"
        assert evidence["retry_after"] == "10"
