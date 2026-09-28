"""Every applicable scope must cover the same attempt, including exact equality."""

import pytest
from slow_thinker_ii.accounting import MAX_QUANTA, BudgetExceeded, BudgetScope, ScopeKind, admit


def scopes() -> tuple[BudgetScope, BudgetScope, BudgetScope]:
    return (
        BudgetScope("run", "r", 100, 60, 30),
        BudgetScope("session", "s", 100, 60, 30),
        BudgetScope("month", "m", 100, 60, 30),
    )


def test_exact_equality_is_admitted_without_mutation() -> None:
    before = scopes()
    admit(before, 10)
    assert before == scopes()


@pytest.mark.parametrize("index", [0, 1, 2])
def test_each_scope_can_deny(index: int) -> None:
    original = scopes()
    changed = list(original)
    item = changed[index]
    changed[index] = BudgetScope(item.kind, item.key, 99, 60, 30)
    with pytest.raises(BudgetExceeded) as error:
        admit((changed[0], changed[1], changed[2]), 10)
    assert error.value.scope.kind == item.kind
    assert error.value.reservation == 10
    assert str(error.value) == f"Insufficient {item.kind} budget"


def test_missing_scope_cannot_pass() -> None:
    item = scopes()[0]
    with pytest.raises(ValueError, match="run, session and month"):
        admit((item, item, item), 0)


@pytest.mark.parametrize("reservation", [-1, MAX_QUANTA + 1])
def test_invalid_reservation(reservation: int) -> None:
    with pytest.raises(ValueError, match="reservation"):
        admit(scopes(), reservation)


@pytest.mark.parametrize("kind", ["run", "session", "month"])
def test_zero_budget_rejects_positive_cost(kind: ScopeKind) -> None:
    zero = BudgetScope(kind, "zero", 0, 0, 0)
    existing = scopes()
    chosen = tuple(zero if item.kind == kind else item for item in existing)
    with pytest.raises(BudgetExceeded):
        admit((chosen[0], chosen[1], chosen[2]), 1)


@pytest.mark.parametrize("field", ["cap", "settled", "outstanding"])
@pytest.mark.parametrize("value", [-1, MAX_QUANTA + 1])
def test_invalid_scope_amounts(field: str, value: int) -> None:
    values = {"cap": 1, "settled": 0, "outstanding": 0}
    values[field] = value
    with pytest.raises(ValueError, match="amount"):
        BudgetScope("run", "r", values["cap"], values["settled"], values["outstanding"])


def test_scope_key_is_required() -> None:
    with pytest.raises(ValueError, match="key"):
        BudgetScope("run", "", 0, 0, 0)
