"""A real coordinator supplies evidence recording to the conditional fixture environment."""

from pathlib import Path

from slow_thinker_ii.application import ConditionalProgram, sequence_access
from slow_thinker_ii.contracts import decode_json, encode_json

from .conditional import ConditionalEnvironment, conditional_plan
from .coordinator import CoordinatorCase, coordinator_case


def conditional_case(
    directory: Path, mode: str = "accept"
) -> tuple[CoordinatorCase, ConditionalEnvironment]:
    case = coordinator_case(directory)
    plan = conditional_plan(mode)
    environment = ConditionalEnvironment(plan, mode)
    case.preparer.environment = environment
    case.preparer.program = ConditionalProgram(plan)
    case.preparer.policy = sequence_access(plan)
    case.preparer.snapshot_json = encode_json({"definition": decode_json(plan.graph_json)})
    return case, environment
