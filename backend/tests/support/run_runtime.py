"""Two controlled real hosts and a small program exercise the complete runtime owner."""

import json
from pathlib import Path

from slow_thinker_ii.access import AccessPolicy, OperationAddress
from slow_thinker_ii.adapters.process import ProcessFleet, ProcessHost
from slow_thinker_ii.application import ManagedCalls, ManagedRun, RunFinalization

from .managed_calls import RealClock
from .process_fixture import fixture_process
from .run_admission import RunCase, run_case

FIRST = OperationAddress("first", "wait")
SECOND = OperationAddress("second", "wait")


class FixtureProgram:
    def __init__(self, arguments: str = "{}") -> None:
        self.arguments = arguments
        self.called = False

    async def execute(self, calls: ManagedCalls) -> str:
        self.called = True
        results: list[str] = []
        for target in (FIRST, SECOND):
            result = await calls.schedule(target, self.arguments)
            if not result.outcome.publish:
                raise RuntimeError("The program cannot publish a rejected result")
            results.append(result.result.payload_json)
        return json.dumps(results)


def runtime_case(
    directory: Path, *, mode: str = "normal", seconds: float = 20
) -> tuple[RunCase, ManagedRun, tuple[ProcessHost, ...]]:
    case = run_case(
        directory / "run.sqlite",
        clock=RealClock(),
        start=False,
        seconds=seconds,
        policy=AccessPolicy((FIRST, SECOND), (), (FIRST, SECOND)),
    )
    hosts: list[ProcessHost] = []
    for name, behavior in (("first", "normal"), ("second", mode)):
        workspace = directory / name
        workspace.mkdir()
        process = fixture_process(workspace, behavior)
        hosts.append(ProcessHost(name, process, (("wait", None),)))
    finalization = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    with case.store.begin() as transaction:
        deadline = transaction.run("run").deadline
    runtime = ManagedRun(
        case.authority, case.service, finalization, ProcessFleet(hosts), deadline, 1
    )
    return case, runtime, tuple(hosts)
