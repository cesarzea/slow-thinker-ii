"""Native SDK fixtures retain HTTP requests and never contact a provider."""

import httpx2
from openai import AsyncOpenAI
from slow_thinker_host import JsonObject, decode_json, json_object
from slow_thinker_llm_call import LLMCallConfig, effective_operation


def completion(content: str | None, reason: str = "stop") -> JsonObject:
    return {
        "id": "completion-fixture",
        "created": 1,
        "model": "fixture-model",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "finish_reason": reason,
                "message": {"role": "assistant", "content": content, "refusal": None},
            }
        ],
    }


def config(schema: JsonObject | None = None) -> LLMCallConfig:
    return LLMCallConfig(
        instructions="Review the supplied input.",
        input_schema={"type": "object"},
        parameters={},
        output={"format": "text"} if schema is None else {"format": "json", "schema": schema},
    )


class ModelStub:
    def __init__(self, response: JsonObject, status: int = 200) -> None:
        self.response, self.status = response, status
        self.requests: list[JsonObject] = []
        self.authority: list[str] = []
        self.timeout = False

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/v1/chat/completions"
        self.requests.append(json_object(decode_json(request.content.decode())))
        self.authority.append(request.headers["Authorization"])
        if self.timeout:
            raise httpx2.ReadTimeout("fixture timeout", request=request)
        return httpx2.Response(self.status, json=self.response)

    def client(self, grant: str = "fixture-grant") -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=grant,
            base_url="http://127.0.0.1/v1/",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(self.handle)),
        )


def bootstrap_record(base_url: str) -> JsonObject:
    settings = config()
    operation = effective_operation(settings)
    declared: JsonObject = {
        "name": operation.name,
        "input_schema": operation.input_schema,
        "output_schema": operation.output_schema,
    }
    binding: JsonObject = {
        "base_url": base_url,
        "model": "bound-model",
        "timeout_seconds": 5,
        "close_seconds": 1,
    }
    return {
        "config": json_object(settings),
        "operations": [declared],
        "clients": {"openai": binding},
    }
