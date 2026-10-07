"""Handler failures and protocol-violating results become `{code, message}` tool errors."""

from collections.abc import Sequence
from typing import cast

import pytest
from host_fixtures import Recorder, bootstrap, connect, error_of, meta
from slow_thinker_host import Context, Emission, HandlerError, JsonValue, create_server


class Returning:
    """Returns a configured value, whatever it is, from either operation."""

    def __init__(self, value: object) -> None:
        self.value = value

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        del message, context
        return cast(Sequence[Emission], self.value)

    async def select_output(
        self, received: JsonValue, node_input: JsonValue, context: Context
    ) -> Emission:
        del received, node_input, context
        return cast(Emission, self.value)


@pytest.mark.parametrize(
    ("failure", "code", "message"),
    [
        (HandlerError("script_error", "The script failed."), "script_error", "The script failed."),
        (KeyError("score"), "component_error", "The component raised KeyError: 'score'"),
        (RuntimeError(), "component_error", "The component raised RuntimeError."),
        (
            ValueError("x" * 400),
            "component_error",
            "The component raised ValueError: " + "x" * 300 + "…",
        ),
    ],
)
async def test_failures_map_to_tool_errors(failure: Exception, code: str, message: str) -> None:
    handler = Recorder()
    handler.failure = failure
    async with connect(create_server(bootstrap("node"), node=handler)) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=meta())
    assert error_of(result) == {"code": code, "message": message}


@pytest.mark.parametrize(
    "value",
    [
        "out",
        [("out", 1)],
        [Emission("out", float("nan"))],
        [Emission("out", cast(JsonValue, (1, 2)))],
        [Emission(cast(str, 1), "text")],
    ],
)
async def test_activate_results_must_be_emissions_of_json(value: object) -> None:
    async with connect(create_server(bootstrap("node"), node=Returning(value))) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=meta())
    assert error_of(result)["code"] == "invalid_result"


@pytest.mark.parametrize("value", [None, [Emission("a", 1)], Emission("a", cast(JsonValue, {1}))])
async def test_select_output_results_must_be_one_emission(value: object) -> None:
    async with connect(create_server(bootstrap("output"), output=Returning(value))) as client:
        result = await client.call_tool(
            "select_output", {"received": 1, "node_input": 2}, meta=meta()
        )
    assert error_of(result)["code"] == "invalid_result"


async def test_a_failed_call_does_not_affect_the_next_one() -> None:
    handler = Recorder()
    handler.failure = HandlerError("invalid_json", "The reply is not JSON.")
    async with connect(create_server(bootstrap("node"), node=handler)) as client:
        failed = await client.call_tool("activate", {"message": 1}, meta=meta())
        handler.failure = None
        result = await client.call_tool("activate", {"message": 2}, meta=meta(grant="grant-2"))
    assert error_of(failed)["code"] == "invalid_json"
    assert result.structured_content == {"emissions": [{"port": "out", "payload": 2}]}


@pytest.mark.parametrize(
    ("code", "message"), [("Invalid", "message"), ("", "message"), ("a" * 65, "x"), ("ok", "")]
)
def test_handler_errors_require_a_code_and_a_message(code: str, message: str) -> None:
    with pytest.raises(ValueError):
        raise HandlerError(code, message)


async def test_unexpected_exceptions_keep_their_traceback_on_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    handler = Recorder()
    handler.failure = KeyError("score")
    async with connect(create_server(bootstrap("node"), node=handler)) as client:
        await client.call_tool("activate", {"message": 1}, meta=meta())
    error = capsys.readouterr().err
    assert "Node echo: activate raised an unexpected exception" in error
    assert "Traceback (most recent call last)" in error and "KeyError: 'score'" in error
