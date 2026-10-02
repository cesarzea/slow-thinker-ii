"""Real LLMCall SDK requests enter the public managed gateway through an in-memory transport."""

import httpx2
from openai import AsyncOpenAI
from slow_thinker_ii.application import NativeModelGateway, OperationReply, PreparedOperation
from slow_thinker_ii.contracts import (
    JsonObject,
    OperationResult,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_llm_call import LLMCall, parse_config

from ..native_model import response
from ..openai_calls import ModelStub


class NativeSDKTransport:
    def __init__(self) -> None:
        self.stub = ModelStub(response())
        self.gateway: NativeModelGateway | None = None

    async def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.stub.handle(request)
        assert self.gateway is not None
        grant = request.headers["Authorization"].removeprefix("Bearer ")
        reply = await self.gateway.complete(grant, request.content.decode())
        return httpx2.Response(
            reply.status, content=reply.payload_json, headers={"content-type": "application/json"}
        )

    def client(self, grant: str) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=grant,
            base_url="http://127.0.0.1/v1/",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(self.handle)),
        )


class PreparedLLMOperation:
    def __init__(self, config: JsonObject, alias: str, transport: NativeSDKTransport) -> None:
        self.config, self.alias, self.transport = config, alias, transport
        parse_config(config)

    def prepare(self, arguments_json: str) -> PreparedOperation:
        return PreparedOperation(arguments_json, None)

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        del deadline
        async with self.transport.client(grant) as client:
            agent = LLMCall(parse_config(self.config), client, self.alias)
            result = await agent.generate(json_object(decode_json(arguments_json)))
        payload = json_object(result)
        return OperationReply(OperationResult(encode_json(payload), payload["status"] != "ok"))
