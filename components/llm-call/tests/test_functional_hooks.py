"""Code extensions cannot mutate supplied inputs or replace schema enforcement."""

import pytest
from slow_thinker_llm_call import JsonObject, JsonValue, LLMCall, Message, ModelResponse
from support.openai_calls import ModelStub, completion, config


class Transforming(LLMCall):
    def build_messages(self, arguments: JsonObject) -> list[Message]:
        arguments.clear()
        return [Message("user", "custom")]

    def parse_response(self, response: ModelResponse) -> JsonValue:
        return {"number": int(response.text)}

    def validate_result(self, value: JsonValue, arguments: JsonObject) -> None:
        assert arguments == {"original": True}
        assert isinstance(value, dict)
        value.clear()
        arguments.clear()


async def test_hooks_receive_copies_and_cannot_change_the_validated_result() -> None:
    stub = ModelStub(completion("7"))
    arguments: JsonObject = {"original": True}
    async with stub.client() as client:
        result = await Transforming(config({"type": "object"}), client, "model").generate(arguments)
    assert arguments == {"original": True}
    assert result == {"status": "ok", "format": "json", "value": {"number": 7}}
    assert stub.requests[0]["messages"] == [{"role": "user", "content": "custom"}]


async def test_text_hook_cannot_replace_text_with_an_object() -> None:
    stub = ModelStub(completion("7"))
    async with stub.client() as client:
        with pytest.raises(TypeError, match="Text parsing"):
            await Transforming(config(), client, "model").generate({"original": True})
