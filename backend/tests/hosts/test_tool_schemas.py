"""The platform's expected tools are exactly the host SDK's (tests may import the SDK)."""

import pytest
from slow_thinker_host import position_tools, tool_schemas
from slow_thinker_ii.adapters.hosts import protocol_tool, protocol_tools
from slow_thinker_ii.engine import Position


@pytest.mark.parametrize("position", ["node", "output", "memory"])
def test_expected_tool_schemas_equal_the_sdks(position: Position) -> None:
    assert protocol_tool(position) == tool_schemas(position)
    assert protocol_tools(position) == position_tools(position)
