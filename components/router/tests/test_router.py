"""Both operations call `route` and emit its choice; every other result fails the call."""

import asyncio

import pytest
from router_fakes import FakeContext, router
from slow_thinker_host import Emission, HandlerError, JsonObject


@pytest.mark.parametrize(("score", "output"), [(8, "accepted"), (5, "revise")])
async def test_select_output_emits_the_scripts_choice(score: int, output: str) -> None:
    context = FakeContext()
    emission = await router().select_output({"score": score}, "Whiskers studied…", context)
    assert emission == Emission(output, "Whiskers studied…")
    assert context.reports == [("step", f"route returned {output}")]


async def test_activate_routes_the_message_as_both_arguments() -> None:
    script = "def route(received, node_input):\n    return 'out', [received, node_input]\n"
    context = FakeContext()
    emissions = await router(script, ("out",)).activate({"story": "A cat."}, context)
    assert emissions == [Emission("out", [{"story": "A cat."}, {"story": "A cat."}])]
    assert context.reports == [("step", "route returned out")]


async def test_lists_are_accepted_as_pairs_and_received_values_are_copies() -> None:
    script = "def route(received, node_input):\n    received.clear()\n    return ['accepted', 1]\n"
    original: JsonObject = {"score": 9}
    emission = await router(script).select_output(original, None, FakeContext())
    assert emission == Emission("accepted", 1) and original == {"score": 9}


async def test_an_undeclared_output_is_named_exactly() -> None:
    script = "def route(received, node_input):\n    return 'maybe', received\n"
    with pytest.raises(HandlerError) as caught:
        await router(script).select_output({"score": 1}, "story", FakeContext())
    assert (caught.value.code, caught.value.message) == (
        "undeclared_output",
        'The script returned the undeclared output "maybe".',
    )


@pytest.mark.parametrize(
    ("returned", "code", "message"),
    [
        ('"accepted"', "invalid_result", "The script must return a pair"),
        ('"accepted", 1, 2', "invalid_result", "The script must return a pair"),
        ("None", "invalid_result", "The script must return a pair"),
        ("1, 'x'", "invalid_result", "returned an output name of type int"),
        ('"accepted", {1, 2}', "invalid_result", 'content for output "accepted" is not a JSON'),
        ('"accepted", ("a", "b")', "invalid_result", "is not a JSON value"),
        ('"accepted", float("nan")', "invalid_result", "is not a JSON value"),
    ],
)
async def test_invalid_results_fail_the_call(returned: str, code: str, message: str) -> None:
    context = FakeContext()
    script = f"def route(received, node_input):\n    return {returned}\n"
    with pytest.raises(HandlerError) as caught:
        await router(script).select_output({"score": 1}, "story", context)
    assert caught.value.code == code and message in caught.value.message
    assert not context.reports


async def test_script_exceptions_name_type_message_and_line() -> None:
    with pytest.raises(HandlerError) as caught:
        await router().select_output({"grade": 7}, "story", FakeContext())
    assert caught.value.code == "script_error"
    assert caught.value.message == "The script raised KeyError: 'score' at line 2."


async def test_exceptions_from_called_library_code_keep_the_scripts_line() -> None:
    script = "import json\n\ndef route(received, node_input):\n    return json.loads('{')\n"
    with pytest.raises(HandlerError) as caught:
        await router(script).select_output(1, 2, FakeContext())
    assert caught.value.message.startswith("The script raised JSONDecodeError: Expecting")
    assert caught.value.message.endswith(" at line 4.")


@pytest.mark.parametrize("statement", ["raise SystemExit(3)", "raise RuntimeError"])
async def test_even_exiting_scripts_only_fail_the_call(statement: str) -> None:
    script = f"def route(received, node_input):\n    {statement}\n"
    with pytest.raises(HandlerError) as caught:
        await router(script).select_output(1, 2, FakeContext())
    assert caught.value.code == "script_error" and caught.value.message.endswith("at line 2.")


async def test_a_slow_script_does_not_block_the_host() -> None:
    script = (
        "import time\n\n"
        "def route(received, node_input):\n"
        "    time.sleep(0.2)\n"
        "    return 'accepted', 1\n"
    )
    ticks = 0

    async def tick() -> None:
        nonlocal ticks
        while True:
            ticks += 1
            await asyncio.sleep(0.01)

    ticker = asyncio.create_task(tick())
    emission = await router(script).select_output(1, 2, FakeContext())
    ticker.cancel()
    assert emission == Emission("accepted", 1) and ticks >= 5


async def test_a_late_outcome_of_an_abandoned_call_is_dropped() -> None:
    script = "import time\n\ndef route(received, node_input):\n    time.sleep(0.1)\n    return 1\n"
    with pytest.raises(TimeoutError):
        async with asyncio.timeout(0.02):
            await router(script).select_output(1, 2, FakeContext())
    await asyncio.sleep(0.2)
