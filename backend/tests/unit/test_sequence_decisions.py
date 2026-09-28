"""A component's proposal cannot bypass the admitted finite control profile."""

import pytest
from slow_thinker_ii.contracts import JsonObject
from slow_thinker_ii.execution import require_sequence_decision


@pytest.mark.parametrize(
    "decision,expected",
    [
        ({"action": "complete", "nodes": []}, "draft"),
        ({"action": "schedule", "nodes": ["review"]}, "draft"),
        ({"action": "schedule", "nodes": ["draft", "review"]}, "draft"),
        ({"action": "schedule", "nodes": ["draft"]}, None),
        ({"action": "schedule", "nodes": ["draft"], "mutation": {}}, "draft"),
        ({"action": "schedule"}, "draft"),
    ],
)
def test_invalid_controller_choice_is_rejected(decision: JsonObject, expected: str | None) -> None:
    with pytest.raises(ValueError):
        require_sequence_decision(decision, expected)
