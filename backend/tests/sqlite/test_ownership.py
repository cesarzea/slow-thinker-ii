"""One backend owns a database file; the lock follows its canonical path and its process."""

import subprocess
import sys
from contextlib import ExitStack
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase

CHILD = (
    "import os, sys\nfrom pathlib import Path\n"
    "from slow_thinker_ii.adapters.sqlite import SqliteDatabase\n"
    "with SqliteDatabase(Path(sys.argv[1])).ownership():\n"
    "    print('owned', flush=True)\n    sys.stdin.readline()\n    os._exit(7)\n"
)


def owned(*paths: Path) -> None:
    """Takes the owner lock of each path in order, then releases them; a refusal raises."""
    with ExitStack() as locks:
        for path in paths:
            locks.enter_context(SqliteDatabase(path).ownership())


def test_a_second_owner_is_refused_until_the_first_releases(tmp_path: Path) -> None:
    path = tmp_path / "data" / "state.sqlite3"
    with pytest.raises(RuntimeError, match="Another backend owns this store"):
        owned(path, path)
    with SqliteDatabase(path).ownership():
        assert path.with_name("state.sqlite3.owner").exists()


def test_process_exit_releases_the_lock_without_deleting_its_file(tmp_path: Path) -> None:
    path = tmp_path / "state.sqlite3"
    with subprocess.Popen(
        [sys.executable, "-c", CHILD, str(path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    ) as child:
        assert child.stdout is not None and child.stdout.readline() == "owned\n"
        with pytest.raises(RuntimeError, match="Another backend"):
            owned(path)
        child.communicate("exit\n", timeout=5)
        assert child.returncode == 7
    assert path.with_name("state.sqlite3.owner").exists()
    owned(path)


def test_aliases_of_one_file_share_its_lock(tmp_path: Path) -> None:
    directory = tmp_path / "data"
    directory.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(directory, target_is_directory=True)
    with pytest.raises(RuntimeError, match="Another backend"):
        owned(directory / "state.sqlite3", alias / "state.sqlite3")
