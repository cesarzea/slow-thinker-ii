"""Restart termination is bounded and allowed only with every durable ownership fact present."""

import os
from dataclasses import replace
from pathlib import Path

import psutil
import pytest
from slow_thinker_ii.adapters.process import recover_processes
from slow_thinker_ii.adapters.sqlite import SqliteProcessJournal
from slow_thinker_ii.application import OwnedLaunch, recover_runs
from support.owned_process import owned_child
from support.run_admission import run_case


@pytest.mark.parametrize("stubborn", [False, True])
async def test_recovery_terminates_only_verified_owned_child(
    tmp_path: Path, *, stubborn: bool
) -> None:
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    async with owned_child(tmp_path, stubborn=stubborn) as identity:
        journal.prepare(OwnedLaunch(identity.marker, "run", "runtime", "worker", str(tmp_path)))
        journal.started(identity)
        recover_runs(case.store)
        await recover_processes(journal, 0.5)
        assert not journal.pending()
        with pytest.raises(ProcessLookupError):
            os.kill(identity.pid, 0)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "interrupted"
        assert any(event.event == "run.cleanup" for event in transaction.events("run"))


@pytest.mark.parametrize(
    "field", ["marker", "command", "workspace", "executable", "group", "session"]
)
async def test_changed_identity_never_terminates_child(tmp_path: Path, field: str) -> None:
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    async with owned_child(tmp_path) as identity:
        changed = {
            "marker": replace(identity, marker="wrong"),
            "command": replace(identity, command=("wrong",)),
            "workspace": replace(identity, workspace="/wrong"),
            "executable": replace(identity, executable="/wrong"),
            "group": replace(identity, group=identity.group + 1),
            "session": replace(identity, session=identity.session + 1),
        }[field]
        journal.prepare(OwnedLaunch(changed.marker, "run", "runtime", "worker", str(tmp_path)))
        journal.started(changed)
        recover_runs(case.store)
        await recover_processes(journal, 0.1)
        assert len(journal.pending()) == 1 and psutil.pid_exists(identity.pid)
