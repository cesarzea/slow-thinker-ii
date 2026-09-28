"""Final-result reads cannot publish partial output as a completed result."""

from support.coordinator import eventually
from support.operator_http import HttpCase, payload


async def test_result_retains_final_output_and_requires_existing_run(api: HttpCase) -> None:
    identity = payload(await api.client.post("/api/v1/runs", json=api.start()))["target_id"]
    await eventually(lambda: not api.case.coordinator.pending().runs)
    result = payload(await api.client.get(f"/api/v1/runs/{identity}/result"))
    assert result["status"] == "recorded" and result["content"] == {"done": True}
    assert (await api.client.get("/api/v1/runs/missing/result")).status_code == 404


async def test_unfinished_and_cancelled_runs_have_no_final_result(api: HttpCase) -> None:
    api.case.preparer.operation.release.clear()
    identity = payload(await api.client.post("/api/v1/runs", json=api.start()))["target_id"]
    url = f"/api/v1/runs/{identity}/result"
    assert payload(await api.client.get(url))["status"] == "unavailable"
    await api.client.post(
        f"/api/v1/runs/{identity}/stop", json={"schema_version": "0.1-draft", "command_id": "stop"}
    )
    await eventually(lambda: not api.case.coordinator.pending().runs)
    result = payload(await api.client.get(url))
    assert result["status"] == "unavailable" and result["content"] is None
