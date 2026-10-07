"""The LLM client targets the platform with the call's grant, no retries and its budget."""

from collections.abc import Sequence
from dataclasses import replace

from host_fixtures import bootstrap, connect, meta
from host_platform import fake_platform
from openai import AsyncOpenAI
from slow_thinker_host import Context, Emission, JsonValue, create_server


class Caller:
    def __init__(self) -> None:
        self.clients: list[AsyncOpenAI] = []
        self.remaining: list[float] = []

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        self.remaining.append(context.remaining_seconds())
        client = context.llm_client()
        self.clients.append(client)
        completion = await client.chat.completions.create(
            model="openai/gpt-6-luna",
            messages=[{"role": "user", "content": str(message)}],
            max_completion_tokens=20,
        )
        return [Emission("out", completion.choices[0].message.content)]


async def test_client_calls_the_platform_with_the_grant_and_is_closed_afterwards() -> None:
    caller = Caller()
    async with fake_platform() as platform:
        host = replace(bootstrap(), llm_base_url=platform.llm_base_url)
        async with connect(create_server(host, node=caller)) as client:
            result = await client.call_tool("activate", {"message": "hi"}, meta=meta(grant="g-9"))
    assert result.structured_content == {"emissions": [{"port": "out", "payload": "A reply."}]}
    assert platform.chats == [
        (
            {
                "model": "openai/gpt-6-luna",
                "messages": [{"role": "user", "content": "hi"}],
                "max_completion_tokens": 20,
            },
            "Bearer g-9",
        )
    ]
    (used,) = caller.clients
    assert used.api_key == "g-9" and used.max_retries == 0
    assert str(used.base_url) == f"{platform.llm_base_url}/"
    assert isinstance(used.timeout, float) and 0 < used.timeout <= caller.remaining[0] <= 2
    assert used.is_closed()


async def test_each_call_gets_its_own_client() -> None:
    caller = Caller()
    async with fake_platform() as platform:
        host = replace(bootstrap(), llm_base_url=platform.llm_base_url)
        async with connect(create_server(host, node=caller)) as client:
            for grant in ("first", "second"):
                await client.call_tool("activate", {"message": grant}, meta=meta(grant=grant))
    assert [authorization for _, authorization in platform.chats] == [
        "Bearer first",
        "Bearer second",
    ]
    assert caller.clients[0] is not caller.clients[1]
