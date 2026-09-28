"""Prepared identities and transient native grants cannot escape their runtime owner."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import ModelBinding
from support.coordinator import TARGET, Environment, coordinator_case, eventually


async def test_mismatched_prepared_runtime_cannot_be_admitted(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.wrong_identity = True
    result = await case.coordinator.start("start", case.base.prepared().intent)
    assert result.receipt.reason == "preparation_identity_mismatch"
    assert not case.preparer.operation.calls
    await case.coordinator.close()


async def test_runtime_construction_failure_is_recorded_without_launch(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    binding = ModelBinding("worker", "alias", TARGET)
    case.preparer.models = (binding, binding)
    result = await case.coordinator.start("start", case.base.prepared().intent)
    assert result.receipt.target_id is not None
    await eventually(lambda: not case.coordinator.pending().runs)
    with case.runs.begin() as transaction:
        run = transaction.run(result.receipt.target_id)
        assert run.state == "failed" and run.reason == "startup_failure"
        assert transaction.events(run.run_id)[-1].event == "run.cleanup"
    assert case.coordinator.failures() == ((result.receipt.target_id, "ValueError"),)
    assert (
        isinstance(case.preparer.environment, Environment) and case.preparer.environment.opened == 0
    )
    await case.coordinator.close()


async def test_native_gateway_uses_only_current_runtime_authority(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    with pytest.raises(AccessDenied):
        case.coordinator.gateway.deadline("forged")
    case.preparer.operation.release.clear()
    result = await case.coordinator.start("start", case.base.prepared().intent)
    await case.preparer.operation.started.wait()
    _, grant, deadline = case.preparer.operation.calls[0]
    assert case.coordinator.gateway.deadline(grant) == deadline
    with pytest.raises(AccessDenied):
        case.coordinator.gateway.deadline("another-run-grant")
    with pytest.raises(AccessDenied):
        await case.coordinator.gateway.complete(grant, '{"model":"unbound"}')
    assert result.receipt.target_id is not None
    await case.coordinator.stop("stop", result.receipt.target_id)
    await eventually(lambda: not case.coordinator.pending().runs)
    with pytest.raises(AccessDenied):
        case.coordinator.gateway.deadline(grant)
    await case.coordinator.close()
