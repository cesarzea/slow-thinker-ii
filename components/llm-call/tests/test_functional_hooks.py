"""Subclasses change messages, parsing and validation through the three public hooks."""

import pytest
from llm_call_fakes import FakeContext, completion, config
from slow_thinker_host import Emission, HandlerError, JsonValue
from slow_thinker_llm_call import LLMCall, Message, parse_config


class Numbered(LLMCall):
    """Asks for a number in its own words and accepts only even ones."""

    def build_messages(self, message: JsonValue) -> list[Message]:
        return [*super().build_messages(message), Message("assistant", "Answer with a number.")]

    def parse_response(self, reply: str) -> JsonValue:
        return {"number": int(reply)}

    def validate_result(self, value: JsonValue, reply: str) -> None:
        if not isinstance(value, dict) or value["number"] != 8:
            raise HandlerError("not_eight", f"Expected 8, got {reply}.")


async def test_hooks_shape_the_request_and_the_emitted_value() -> None:
    context = FakeContext(completion("8"))
    emissions = await Numbered(parse_config(config())).activate("story", context)
    assert emissions == [Emission("out", {"number": 8})]
    assert context.requests[0]["messages"] == [
        {
            "role": "system",
            "content": "Rewrite this story so that it is funny. Keep it under 80 words.",
        },
        {"role": "user", "content": "story"},
        {"role": "assistant", "content": "Answer with a number."},
    ]
    assert context.steps()[0] == "messages built: 3 messages"


async def test_hook_failures_fail_the_activation_and_are_reported() -> None:
    context = FakeContext(completion("7"))
    with pytest.raises(HandlerError, match="Expected 8, got 7."):
        await Numbered(parse_config(config())).activate("story", context)
    assert context.steps()[-1] == "reply failed validation: not_eight"
