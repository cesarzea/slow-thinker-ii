"""Start carries schema-valid graph identities without widening command authority identities."""

import pytest
from support.operator_http import HttpCase


@pytest.mark.parametrize("revision", ["α / white space ? +", "x" * 129, "line\nbreak", "😀"])
async def test_start_preserves_unusual_graph_revision(api: HttpCase, revision: str) -> None:
    body = api.start()
    body["graph_id"], body["graph_revision"] = "a" * 160, revision
    response = await api.client.post("/api/v1/runs", json=body)
    assert response.status_code == 202
    assert api.case.preparer.calls[0].graph_id == "a" * 160
    assert api.case.preparer.calls[0].graph_revision == revision


@pytest.mark.parametrize(
    "field,value",
    [
        ("graph_id", "Invalid"),
        ("graph_revision", ""),
        ("command_id", "x" * 129),
        ("session_id", "session / α"),
        ("configuration_revision", "configuration / α"),
    ],
)
async def test_other_start_identities_keep_original_constraints(
    api: HttpCase, field: str, value: str
) -> None:
    body = api.start()
    body[field] = value
    assert (await api.client.post("/api/v1/runs", json=body)).status_code == 422
    assert not api.case.preparer.calls
