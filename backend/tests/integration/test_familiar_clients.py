"""Pinned LangChain and LangGraph keep familiar invocation signatures over managed routes."""

from pathlib import Path

import pytest
from langchain_openai import ChatOpenAI
from openai import APIStatusError
from pydantic import SecretStr
from slow_thinker_host import managed_langchain_tools
from slow_thinker_ii.contracts import OperationResult, encode_json
from support.langgraph_sdk import GraphState, graph_module
from support.mcp_gateway import mcp_case
from support.native_gateway import assert_recorded, native_case
from support.native_server import gateway_app, serve


@pytest.mark.parametrize("fails", [False, True])
async def test_langchain_model_signatures_and_error_without_retry(
    tmp_path: Path, *, fails: bool
) -> None:
    case = native_case(tmp_path)
    if fails:
        case.model.result = provider_error()
    async with serve(gateway_app(case.gateway)) as port:
        model = language_model(port, case.parent.token)
        try:
            if fails:
                with pytest.raises(APIStatusError) as caught:
                    await model.ainvoke("hello")
                assert caught.value.status_code == 429
            else:
                assert (await model.ainvoke("hello")).content == "success"
                assert_recorded(case)
        finally:
            await model.root_async_client.close()
            model.root_client.close()
    assert len(case.model.calls) == 1
    await case.calls.close(1)


async def test_langgraph_node_calls_a_normal_structured_tool(tmp_path: Path) -> None:
    case = mcp_case(tmp_path)
    async with serve(case.app) as port:
        tools = await managed_langchain_tools(case.endpoint(port), case.invocation())
        tool = next(tool for tool in tools if tool.name != "platform.report")

        async def invoke(state: GraphState) -> GraphState:
            reply = await tool.ainvoke(
                {
                    "request": {
                        "model": "bound-model",
                        "messages": [{"role": "user", "content": state["content"]}],
                    }
                }
            )
            assert isinstance(reply, dict) and "response" in reply
            return {"content": "completed"}

        graphs = graph_module()
        builder = graphs.StateGraph(GraphState)
        builder.add_node("worker", invoke)
        builder.add_edge(graphs.START, "worker")
        builder.add_edge("worker", graphs.END)
        assert await builder.compile().ainvoke({"content": "hello"}) == {"content": "completed"}
    assert len(case.native.model.calls) == 1
    assert_recorded(case.native)
    await case.native.calls.close(1)


def provider_error() -> OperationResult:
    return OperationResult(
        encode_json(
            {
                "error": {
                    "origin": "provider",
                    "status": 429,
                    "body": {
                        "error": {"message": "limited", "type": "rate_limit", "code": "limited"}
                    },
                }
            }
        ),
        True,
    )


def language_model(port: int, token: str) -> ChatOpenAI:
    return ChatOpenAI(
        model="bound-model",
        api_key=SecretStr(token),
        base_url=f"http://127.0.0.1:{port}/v1",
        max_retries=0,
        timeout=5,
        use_responses_api=False,
        stream_usage=False,
    )
