"""Trusted first-cycle preparation recipes; graphs cannot supply build or launch code."""

from dataclasses import dataclass

from slow_thinker_ii.adapters.installations import ComponentRegistration, ImplementationBase

TARGETS = (
    "sequence",
    "llm-call",
    "openai-model",
    "grounded-review",
    "redirector",
    "routed-call",
    "bounded-flow",
)


@dataclass(frozen=True)
class PreparationTarget:
    projects: tuple[str, ...]
    registration: ComponentRegistration
    additional_requirements: tuple[str, ...] = ()


_IDENTITIES = {
    "redirector": (
        "redirector",
        "slow-thinker-redirector",
        "slow_thinker_redirector:RedirectorHost",
    ),
    "routed-call": (
        "routed-call",
        "slow-thinker-routed-call",
        "slow_thinker_routed_call:RoutedCallHost",
    ),
    "bounded-flow": (
        "bounded-flow",
        "slow-thinker-bounded-flow",
        "slow_thinker_bounded_flow:BoundedFlowHost",
    ),
    "sequence": (
        "example.sequence",
        "slow-thinker-sequence",
        "slow_thinker_sequence:SequenceHost",
    ),
    "llm-call": ("llm-call", "slow-thinker-llm-call", "slow_thinker_llm_call:LLMCall"),
    "openai-model": (
        "example.model-resource",
        "slow-thinker-openai-model",
        "slow_thinker_openai_model:OpenAIModelHost",
    ),
    "grounded-review": (
        "example.grounded-review",
        "example-grounded-review",
        "example_grounded_review:GroundedReview",
    ),
}


def registration_identity(name: str) -> tuple[str, str, str]:
    if name not in _IDENTITIES:
        raise ValueError("Unknown component preparation target")
    return _IDENTITIES[name]


def _projects(name: str) -> tuple[str, ...]:
    if name == "redirector":
        return (
            "components/host",
            "components/llm-call",
            "examples/grounded-review",
            "components/redirector",
        )
    if name == "grounded-review":
        return ("components/host", "components/llm-call", "examples/grounded-review")
    return ("components/host", f"components/{name}")


def _registration(name: str) -> ComponentRegistration:
    type_id, distribution, entry_point = registration_identity(name)
    base = None
    if name == "grounded-review":
        base = ImplementationBase(
            distribution="slow-thinker-llm-call",
            version="0.1.0.dev1",
            entry_point="slow_thinker_llm_call:LLMCall",
            requirement="slow-thinker-llm-call==0.1.0.dev1",
        )
    stable = name in {"redirector", "routed-call", "bounded-flow"}
    return ComponentRegistration(
        type_id=type_id,
        type_version="0.1.0" if stable else "0.1.0-example",
        distribution=distribution,
        version="0.1.0" if stable else "0.1.0.dev1",
        entry_point=entry_point,
        base=base,
    )


def target(name: str) -> PreparationTarget:
    registration = _registration(name)
    additions = ("example-grounded-review==0.1.0.dev1",) if name == "redirector" else ()
    return PreparationTarget(_projects(name), registration, additions)
