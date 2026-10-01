"""Complete route histories determine acceptance, exhaustion or one next activation."""

import pytest
from slow_thinker_bounded_flow import BoundedFlow, CompletedStep, FlowDecision, parse_config
from slow_thinker_host import JsonObject, JsonValue

CONFIG: JsonObject = {
    "entry": "draft",
    "routes": {"draft": {"next": "check"}, "check": {"accept": None, "revise": "draft"}},
    "max_activations": 4,
}
DRAFT = CompletedStep("draft", "next")
REVISE = CompletedStep("check", "revise")
ACCEPT = CompletedStep("check", "accept")


@pytest.mark.parametrize(
    "history,expected",
    [
        ((), FlowDecision("activate", "draft")),
        ((DRAFT,), FlowDecision("activate", "check")),
        ((DRAFT, ACCEPT), FlowDecision("complete")),
        ((DRAFT, REVISE), FlowDecision("activate", "draft")),
        ((DRAFT, REVISE, DRAFT, ACCEPT), FlowDecision("complete")),
        (
            (DRAFT, REVISE, DRAFT, REVISE),
            FlowDecision("exhausted", reason="activation_limit_reached"),
        ),
    ],
)
def test_history_selects_exact_decision(
    history: tuple[CompletedStep, ...], expected: FlowDecision
) -> None:
    controller = BoundedFlow(parse_config(CONFIG))
    assert controller.next(history) == expected
    assert controller.next(()) == FlowDecision("activate", "draft")


@pytest.mark.parametrize(
    "history",
    [
        (ACCEPT,),
        (CompletedStep("draft", "absent"),),
        (DRAFT, DRAFT),
        (DRAFT, ACCEPT, DRAFT),
        (DRAFT, REVISE, DRAFT, REVISE, DRAFT),
    ],
)
def test_invalid_history_is_an_error_not_exhaustion(history: tuple[CompletedStep, ...]) -> None:
    with pytest.raises(ValueError):
        BoundedFlow(parse_config(CONFIG)).next(history)


@pytest.mark.parametrize(
    "field,value",
    [
        ("entry", "absent"),
        ("entry", ""),
        ("routes", {}),
        ("routes", {"draft": {}}),
        ("routes", {"draft": {"": None}}),
        ("routes", {"draft": {"go": "absent"}}),
        ("routes", {"draft": {"go": 1}}),
        ("max_activations", 0),
        ("max_activations", True),
        ("max_activations", 1.5),
        ("extra", None),
    ],
)
def test_invalid_topology_or_bound_is_rejected(field: str, value: JsonValue) -> None:
    with pytest.raises(ValueError):
        parse_config({**CONFIG, field: value})


def test_single_terminal_activation_at_configured_bound() -> None:
    config = parse_config(
        {"entry": "only", "routes": {"only": {"done": None}}, "max_activations": 1}
    )
    assert BoundedFlow(config).next((CompletedStep("only", "done"),)) == FlowDecision("complete")
