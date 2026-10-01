"""Recovery cannot signal an unrelated PID and retains every unproven launch."""

import os
import sys
from dataclasses import replace
from pathlib import Path

import psutil
from slow_thinker_ii.adapters.process import recover_processes
from slow_thinker_ii.adapters.sqlite import SqliteProcessJournal
from slow_thinker_ii.application import OwnedLaunch, ProcessIdentity, recover_runs
from support.run_admission import run_case


def current_identity(directory: Path) -> ProcessIdentity:
    process = psutil.Process()
    return ProcessIdentity(
        process.pid,
        process.create_time(),
        process.exe(),
        tuple(process.cmdline()),
        "not-the-owned-marker",
        str(directory),
        os.getpgid(process.pid),
        os.getsid(process.pid),
    )


async def test_reused_pid_remains_unconfirmed_without_signal(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    identity = replace(current_identity(tmp_path), created_at=1)
    journal.prepare(OwnedLaunch(identity.marker, "run", "runtime", "worker", str(tmp_path)))
    journal.started(identity)
    recover_runs(case.store)
    await recover_processes(journal, 0.1)
    assert len(journal.pending()) == 1 and psutil.pid_exists(os.getpid())
    with case.database.transaction() as db:
        assert db.execute("SELECT state FROM process_ownership").fetchone()[0] == "unconfirmed"


async def test_unrecorded_spawn_identity_blocks_recovered_cleanup(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    journal.prepare(OwnedLaunch("pending", "run", "runtime", "worker", str(tmp_path)))
    recover_runs(case.store)
    await recover_processes(journal, 0.1)
    assert journal.pending()[0].identity is None
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "interrupted"
        assert not any(event.event == "run.cleanup" for event in transaction.events("run"))


async def test_absent_owned_process_can_confirm_cleanup(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    identity = ProcessIdentity(
        2**30, 1, sys.executable, (sys.executable,), "absent", str(tmp_path), 2**30, 2**30
    )
    journal.prepare(OwnedLaunch("absent", "run", "runtime", "worker", str(tmp_path)))
    journal.started(identity)
    recover_runs(case.store)
    await recover_processes(journal, 0.1)
    assert not journal.pending()
    with case.store.begin() as transaction:
        assert any(event.event == "run.cleanup" for event in transaction.events("run"))
