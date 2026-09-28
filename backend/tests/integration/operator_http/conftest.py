"""Every HTTP test has an independently owned coordinator and database."""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from support.operator_http import HttpCase, http_case


@pytest.fixture
async def api(tmp_path: Path) -> AsyncIterator[HttpCase]:
    case = http_case(tmp_path)
    try:
        yield case
    finally:
        await case.close()
