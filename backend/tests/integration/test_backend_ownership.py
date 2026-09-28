"""Kernel ownership precedes recovery and ends automatically when its process exits."""

import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from slow_thinker_ii.adapters.sqlite import SqliteDatabase
from slow_thinker_ii.bootstrap import create_app
from support.authority import PROPOSER, REVIEWER
from support.catalog import RecordedCatalog
from support.run_admission import CHARGE, outstanding, run_case


def test_second_backend_cannot_recover_an_active_owner(tmp_path: Path) -> None:
    path = tmp_path / "app.sqlite"
    with (
        TestClient(create_app(path, RecordedCatalog())),
        pytest.raises(RuntimeError, match="Another backend"),
        TestClient(create_app(path, RecordedCatalog())),
    ):
        pytest.fail("Two executors cannot share this store")
    with TestClient(create_app(path, RecordedCatalog())) as client:
        assert client.get("/api/v1/graphs", headers={"host": "127.0.0.1"}).status_code == 200


def test_startup_recovers_unsent_work_but_keeps_uncertain_spending(tmp_path: Path) -> None:
    path = tmp_path / "app.sqlite"
    case = run_case(path)
    sent = case.authority.schedule(PROPOSER)
    unsent = case.authority.schedule(REVIEWER)
    case.service.reserve(sent.token, "{}", CHARGE)
    case.service.reserve(unsent.token, "{}", CHARGE)
    case.service.authorize(sent.token)
    with TestClient(create_app(path, RecordedCatalog())):
        with case.store.begin() as transaction:
            assert transaction.run("run").state == "interrupted"
            assert transaction.call(sent.context.call_id).state == "interrupted"
        assert outstanding(case) == (100, 100, 100)


def test_process_exit_releases_lease_without_deleting_its_file(tmp_path: Path) -> None:
    path = tmp_path / "app.sqlite"
    code = (
        "import os, sys\nfrom pathlib import Path\n"
        "from slow_thinker_ii.adapters.sqlite import SqliteDatabase\n"
        "with SqliteDatabase(Path(sys.argv[1])).ownership():\n"
        "    print('owned', flush=True)\n    sys.stdin.readline()\n    os._exit(7)\n"
    )
    with subprocess.Popen(
        [sys.executable, "-c", code, str(path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    ) as child:
        assert child.stdout is not None and child.stdout.readline() == "owned\n"
        with pytest.raises(RuntimeError, match="Another backend"), SqliteDatabase(path).ownership():
            pytest.fail("The child still owns the lease")
        child.communicate("exit\n", timeout=5)
        assert child.returncode == 7
    assert path.with_name("app.sqlite.owner").exists()
    with SqliteDatabase(path).ownership():
        pass


def test_canonical_paths_share_one_lease(tmp_path: Path) -> None:
    directory = tmp_path / "data"
    directory.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(directory, target_is_directory=True)
    with (
        SqliteDatabase(directory / "app.sqlite").ownership(),
        pytest.raises(RuntimeError, match="Another backend"),
        SqliteDatabase(alias / "app.sqlite").ownership(),
    ):
        pytest.fail("An alias cannot bypass ownership")
