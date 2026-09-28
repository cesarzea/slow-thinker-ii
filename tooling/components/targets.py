"""Trusted first-cycle preparation recipes; graphs cannot supply build or launch code."""

from dataclasses import dataclass

from slow_thinker_ii.adapters.installations import ComponentRegistration, ImplementationBase

TARGETS = ("sequence", "llm-call", "openai-model", "grounded-review")


@dataclass(frozen=True)
class PreparationTarget:
    projects: tuple[str, ...]
    registration: ComponentRegistration


def registration_identity(name: str) -> tuple[str, str, str]:
    recipes = {
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
    if name not in recipes:
        raise ValueError("Unknown component preparation target")
    return recipes[name]


def target(name: str) -> PreparationTarget:
    type_id, distribution, entry_point = registration_identity(name)
    projects = ("components/host", f"components/{name}")
    base = None
    if name == "grounded-review":
        projects = ("components/host", "components/llm-call", "examples/grounded-review")
        base = ImplementationBase(
            distribution="slow-thinker-llm-call",
            version="0.1.0.dev1",
            entry_point="slow_thinker_llm_call:LLMCall",
            requirement="slow-thinker-llm-call==0.1.0.dev1",
        )
    return PreparationTarget(
        projects,
        ComponentRegistration(
            type_id=type_id,
            type_version="0.1.0-example",
            distribution=distribution,
            version="0.1.0.dev1",
            entry_point=entry_point,
            base=base,
        ),
    )
