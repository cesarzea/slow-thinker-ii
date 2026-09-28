"""Scheduling comes from supplied completion state, never hidden retained history."""

import pytest
from slow_thinker_sequence import Decision, Sequence


def test_sequence_can_repeat_independent_evaluations() -> None:
    sequence = Sequence(("draft", "review", "revise"))
    assert sequence.next(()) == Decision("schedule", ("draft",))
    assert sequence.next(("draft", "review")) == Decision("schedule", ("revise",))
    assert sequence.next(("draft", "review", "revise")) == Decision("complete", ())
    assert sequence.next(()) == Decision("schedule", ("draft",))


@pytest.mark.parametrize("steps", [(), ("",), ("draft", "draft")])
def test_invalid_definitions(steps: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        Sequence(steps)


@pytest.mark.parametrize("completed", [("unknown",), ("b",), ("a", "a"), ("a", "b", "c")])
def test_inconsistent_completion(completed: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        Sequence(("a", "b")).next(completed)
