"""The packaged boolean selector is independent of inherited reviewer reasoning."""

import pytest
from example_grounded_review import choose
from example_grounded_review.review_rules import choose as module_choose
from slow_thinker_host import JsonValue


@pytest.mark.parametrize("accepted,expected", [(True, "accept"), (False, "revise")])
def test_public_selector_uses_only_validated_acceptance(accepted: bool, expected: str) -> None:
    assert choose is module_choose
    assert choose({"accepted": accepted, "findings": ["Concrete revision"]}) == expected


@pytest.mark.parametrize("value", [None, [], {}, {"accepted": 1}, {"accepted": "true"}])
def test_selector_rejects_missing_boolean(value: JsonValue) -> None:
    with pytest.raises(ValueError, match="validated review"):
        choose(value)
