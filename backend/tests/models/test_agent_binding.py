"""A caller grant cannot select the other graph agent's provider binding."""

from pathlib import Path

import pytest
from openai import APIStatusError
from support.native_gateway import sdk_client
from support.native_server import gateway_app, serve

from models.mediation_assertions import assert_managed
from models.mediation_fixture import model_case


async def test_two_agent_model_aliases_are_scoped_to_each_authenticated_caller(
    tmp_path: Path,
) -> None:
    case = model_case(tmp_path, separate_agents=True)
    async with serve(gateway_app(case.gateway)) as port:
        for grant, alias in (
            (case.parent.token, "deepseek"),
            (case.deepseek_parent.token, "openai"),
        ):
            async with sdk_client(port, grant) as sdk:
                with pytest.raises(APIStatusError) as caught:
                    await sdk.chat.completions.create(
                        model=alias, messages=[{"role": "user", "content": "x"}]
                    )
            assert caught.value.status_code == 403
    assert not case.openai.native_requests and not case.deepseek.native_requests
    assert_managed(case, 0, 0)
    await case.calls.close(1)
