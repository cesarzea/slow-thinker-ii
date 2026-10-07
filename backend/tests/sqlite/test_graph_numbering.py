"""Change and version numbers stay unique and gap-free per graph under concurrent writers."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteGraphStore

from .stores import AT, initialized, later


def test_concurrent_writers_on_several_branches_get_consecutive_numbers(tmp_path: Path) -> None:
    store = SqliteGraphStore(initialized(tmp_path))
    store.create("g", "Name 0", {"id": "g", "name": "Name 0"}, AT)
    store.create_branch("g", "other", "Name 0", {"id": "g", "name": "Name 0"}, None, 1, AT)

    def change(index: int) -> int:
        name = f"Name {index + 1}"
        branch = "main" if index % 2 else "other"
        return store.add_change("g", branch, name, {"id": "g", "name": name}, later(index))

    with ThreadPoolExecutor(max_workers=8) as pool:
        changes = list(pool.map(change, range(40)))
    assert sorted(changes) == list(range(3, 43))

    def activate(change: int) -> int:
        return store.add_version("g", change, None, later(100))

    with ThreadPoolExecutor(max_workers=8) as pool:
        versions = list(pool.map(activate, range(1, 25)))
    assert sorted(versions) == list(range(1, 25))
    record = store.graph("g")
    assert record is not None and (record.active_version, record.latest_change) == (24, 42)
    assert [item.change for item in store.changes("g", None, None, 100)] == list(range(42, 0, -1))
    per_branch = {item.name: item.latest_change for item in record.branches}
    assert per_branch == {"main": max(changes[1::2]), "other": max(changes[::2])}
