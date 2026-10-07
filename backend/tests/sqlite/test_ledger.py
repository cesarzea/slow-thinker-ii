"""Budget reservations, charges and recovery in integer quanta."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from slow_thinker_ii.accounting import Scope
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteLedger

from .stores import AT, initialized, later

DAY, MONTH = "2026-10-05", "2026-10"


def scopes(
    run_id: str = "r1", run: int = 100, day: int = 1_000, month: int = 10_000
) -> list[Scope]:
    """The application's scopes in admission order, with `used=0` as it passes them."""
    return [
        Scope("run", run_id, run, 0),
        Scope("day", DAY, day, 0),
        Scope("month", MONTH, month, 0),
    ]


def row(database: SqliteDatabase, call_id: str) -> tuple[object, ...]:
    with database.transaction() as connection:
        found = connection.execute(
            "SELECT run_id, day_key, month_key, reserved, charge, estimated, settled_at "
            "FROM ledger WHERE call_id = ?",
            (call_id,),
        ).fetchone()
    return tuple(found)


def test_reservations_count_until_their_charge_replaces_them(tmp_path: Path) -> None:
    database = initialized(tmp_path)
    ledger = SqliteLedger(database)
    assert ledger.reserve("c1", "r1", scopes(), 40, AT) is None
    assert ledger.reserve("c2", "r1", scopes(), 30, AT) is None
    assert row(database, "c1") == ("r1", DAY, MONTH, 40, None, 0, None)
    assert (ledger.used("run", "r1"), ledger.used("day", DAY), ledger.used("month", MONTH)) == (
        70,
        70,
        70,
    )
    ledger.settle("c1", 12, False, later(1))
    ledger.settle("c2", 30, True, later(2))
    assert ledger.used("run", "r1") == 42
    assert row(database, "c2")[4:] == (30, 1, "2026-10-05T12:00:02.123456Z")
    assert ledger.used("run", "other") == 0 and ledger.used("day", "2026-10-06") == 0


@pytest.mark.parametrize(
    "limits,kind",
    [((50, 1_000, 10_000), "run"), ((100, 50, 10_000), "day"), ((100, 1_000, 50), "month")],
)
def test_the_first_exhausted_scope_is_returned_with_its_use(
    tmp_path: Path, limits: tuple[int, int, int], kind: str
) -> None:
    ledger = SqliteLedger(initialized(tmp_path))
    assert ledger.reserve("c1", "r1", scopes("r1", *limits), 30, AT) is None
    exhausted = ledger.reserve("c2", "r1", scopes("r1", *limits), 30, AT)
    assert exhausted is not None and (exhausted.kind, exhausted.used) == (kind, 30)
    assert exhausted.limit == 50
    assert ledger.used("run", "r1") == 30


def test_other_runs_share_the_day_and_month(tmp_path: Path) -> None:
    ledger = SqliteLedger(initialized(tmp_path))
    assert ledger.reserve("c1", "r1", scopes(day=100), 60, AT) is None
    exhausted = ledger.reserve("c2", "r2", scopes("r2", day=100), 60, AT)
    assert exhausted == Scope("day", DAY, 100, 60)


def test_concurrent_reservations_never_exceed_a_limit_together(tmp_path: Path) -> None:
    ledger = SqliteLedger(initialized(tmp_path))

    def reserve(index: int) -> Scope | None:
        return ledger.reserve(f"c{index}", "r1", scopes(run=100), 30, AT)

    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(reserve, range(16)))
    assert sum(outcome is None for outcome in outcomes) == 3
    assert ledger.used("run", "r1") == 90


def test_recovery_settles_open_reservations_as_estimated(tmp_path: Path) -> None:
    database = initialized(tmp_path)
    ledger = SqliteLedger(database)
    for call_id, run_id in (("open", "r1"), ("settled", "r1"), ("other", "r2")):
        assert ledger.reserve(call_id, run_id, scopes(run_id), 25, AT) is None
    ledger.settle("settled", 5, False, later(1))
    ledger.settle_open("r1", later(9))
    assert row(database, "open")[4:] == (25, 1, "2026-10-05T12:00:09.123456Z")
    assert row(database, "settled")[4:] == (5, 0, "2026-10-05T12:00:01.123456Z")
    assert row(database, "other")[4:] == (None, 0, None)
    assert ledger.used("day", DAY) == 55


def test_a_call_settles_once_and_must_have_reserved(tmp_path: Path) -> None:
    ledger = SqliteLedger(initialized(tmp_path))
    with pytest.raises(LookupError, match="no open reservation"):
        ledger.settle("missing", 1, False, AT)
    assert ledger.reserve("c1", "r1", scopes(), 10, AT) is None
    ledger.settle("c1", 4, False, AT)
    with pytest.raises(LookupError):
        ledger.settle("c1", 9, False, AT)
    assert ledger.used("run", "r1") == 4


def test_scope_keys_default_to_the_reservation_time(tmp_path: Path) -> None:
    database = initialized(tmp_path)
    ledger = SqliteLedger(database)
    assert ledger.reserve("c1", "r1", [Scope("run", "r1", 100, 0)], 10, later(86_400)) is None
    assert row(database, "c1")[:3] == ("r1", "2026-10-06", "2026-10")
    with pytest.raises(ValueError, match="Unknown budget scope kind"):
        ledger.used("week", "2026-41")
