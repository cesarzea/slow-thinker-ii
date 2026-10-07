"""One request per activation: prompt as system, the message as user, the reply emitted."""

import pytest
from llm_call_fakes import SCORE, FakeContext, completion, config
from slow_thinker_host import Emission, JsonValue
from slow_thinker_llm_call import LLMCall, parse_config

PROMPT = "Rewrite this story so that it is funny. Keep it under 80 words."


@pytest.mark.parametrize(
    ("message", "user"),
    [
        ("A cat tried to learn to fly.", "A cat tried to learn to fly."),
        ({"z": 1, "story": "ñ"}, '{"story":"ñ","z":1}'),
        ([1, None, True], "[1,null,true]"),
        (7, "7"),
    ],
)
async def test_text_output_sends_the_prompt_and_the_message(message: JsonValue, user: str) -> None:
    context = FakeContext(completion("Whiskers studied pigeons for a week."))
    emissions = await LLMCall(parse_config(config())).activate(message, context)
    assert emissions == [Emission("out", "Whiskers studied pigeons for a week.")]
    assert context.requests == [
        {
            "model": "openai/gpt-6-luna",
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": user},
            ],
            "max_completion_tokens": 300,
        }
    ]
    assert context.authorizations == ["Bearer grant-1"]
    assert all(client.is_closed() for client in context.clients)


async def test_every_configured_parameter_is_sent() -> None:
    parameters: JsonValue = {
        "max_completion_tokens": 50,
        "reasoning_effort": "none",
        "temperature": 0.2,
    }
    model: JsonValue = {"llm": "deepseek/deepseek-flash", "parameters": parameters}
    context = FakeContext()
    await LLMCall(parse_config(config(model=model))).activate("story", context)
    (request,) = context.requests
    assert request["model"] == "deepseek/deepseek-flash"
    assert {key: request[key] for key in ("max_completion_tokens", "reasoning_effort")} == {
        "max_completion_tokens": 50,
        "reasoning_effort": "none",
    }
    assert request["temperature"] == 0.2 and "response_format" not in request


async def test_json_output_requests_the_schema_and_emits_the_parsed_reply() -> None:
    context = FakeContext(completion(' {"score": 8} '))
    settings = parse_config(config(output_format={"type": "json", "schema": SCORE}))
    emissions = await LLMCall(settings).activate("Whiskers studied pigeons.", context)
    assert emissions == [Emission("out", {"score": 8})]
    assert context.requests[0]["response_format"] == {
        "type": "json_schema",
        "json_schema": {"name": "output", "schema": SCORE, "strict": False},
    }


async def test_reports_trace_the_steps_of_a_text_activation() -> None:
    context = FakeContext(completion("Twelve chars"))
    await LLMCall(parse_config(config())).activate("story", context)
    assert context.steps() == [
        "messages built: 2 messages",
        "model replied: 12 characters",
        "reply returned as text",
    ]


async def test_reports_trace_the_validation_of_a_json_activation() -> None:
    context = FakeContext(completion('{"score": 3}'))
    settings = parse_config(config(output_format={"type": "json", "schema": SCORE}))
    await LLMCall(settings).activate("story", context)
    assert context.steps() == [
        "messages built: 2 messages",
        "model replied: 12 characters",
        "reply validated",
    ]


async def test_a_matching_input_format_lets_the_call_proceed() -> None:
    context = FakeContext()
    settings = parse_config(config(input_format={"type": "object", "required": ["story"]}))
    await LLMCall(settings).activate({"story": "A cat."}, context)
    assert len(context.requests) == 1
