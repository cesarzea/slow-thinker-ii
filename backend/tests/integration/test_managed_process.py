"""The real subprocess transport runs only after durable authorization and stores its receipt."""

import json
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import ProcessOperation
from slow_thinker_ii.application import ChargeBasis, ChargeEvidence, ManagedCalls
from slow_thinker_ii.contracts import OperationResult
from support.authority import PROPOSER
from support.managed_calls import RealClock
from support.process_fixture import assert_reaped, fixture_process
from support.run_admission import CHARGE, outstanding, run_case


class FixturePricing:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def quote(self, arguments_json: str) -> ChargeBasis:
        del arguments_json
        return CHARGE

    def reconcile(self, result: OperationResult) -> ChargeEvidence:
        del result
        if self.fail:
            raise RuntimeError("private diagnostic")
        return ChargeEvidence('{"units":1}', 37, "fixture_usage")


@pytest.mark.parametrize("fail", [False, True])
async def test_real_process_response_and_usage_are_recorded(tmp_path: Path, *, fail: bool) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    process = fixture_process(tmp_path)
    async with process.connect() as connection:
        operation = ProcessOperation(connection, "wait", FixturePricing(fail=fail))
        runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
        result = await runner.schedule(PROPOSER, "{}")
        assert result.outcome.publish and result.result.payload_json == '{"done":true}'
        assert outstanding(case) == ((100, 100, 100) if fail else (0, 0, 0))
        with case.store.begin() as transaction:
            saved = transaction.receipt(result.receipt_id)
            assert saved is not None and saved.receipt.response_json == result.result.payload_json
            if fail:
                assert saved.receipt.amount is None
                assert "pricing_failed" in (saved.receipt.usage_json or "")
                assert "private" not in (saved.receipt.usage_json or "")
            else:
                assert saved.receipt.amount == 37
        pending = await runner.close(1)
        assert pending == ()
    assert_reaped(process, forced=False)


async def test_native_mcp_error_survives_the_managed_call(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    process = fixture_process(tmp_path)
    async with process.connect() as connection:
        runner = ManagedCalls(
            case.authority, case.service, {PROPOSER: ProcessOperation(connection, "wait", None)}
        )
        result = await runner.schedule(PROPOSER, '{"error":true}')
        assert result.result.is_error and not result.outcome.publish
        assert json.loads(result.result.payload_json) == {
            "error": {
                "origin": "component",
                "code": -32001,
                "message": "fixture failure",
                "data": {"origin": "fixture"},
            }
        }
        with case.store.begin() as transaction:
            assert transaction.call(result.context.call_id).state == "failed"
    assert_reaped(process, forced=False)


async def test_invalid_input_is_rejected_before_process_authorization(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    process = fixture_process(tmp_path)
    async with process.connect() as connection:
        runner = ManagedCalls(
            case.authority, case.service, {PROPOSER: ProcessOperation(connection, "wait", None)}
        )
        with pytest.raises(ValueError):
            await runner.schedule(PROPOSER, "[]")
        with case.store.begin() as transaction:
            assert all(
                event.event != "call.dispatch_authorized" for event in transaction.events("run")
            )
        assert (await runner.schedule(PROPOSER, "{}")).outcome.publish
    assert_reaped(process, forced=False)
