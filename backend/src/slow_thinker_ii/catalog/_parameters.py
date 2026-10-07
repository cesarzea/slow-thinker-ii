"""Parameters of an LLM entry: plain sentences for problems, and schema defaults."""

from slow_thinker_ii.contracts import JsonObject, json_object, json_value

from ._problems import schema_problems
from ._values import mapping

PARAMETERS = "Parameters"


def parameter_sentences(schema: JsonObject, parameters: JsonObject) -> tuple[str, ...]:
    """Distinct sentences, sorted, such as `Max output tokens must be at most 128000.`"""
    problems = schema_problems(schema, parameters, fallback=PARAMETERS)
    return tuple(sorted({problem.sentence for problem in problems}))


def defaults_added(schema: JsonObject, parameters: JsonObject) -> JsonObject:
    """A copy with each missing top-level default added unless it adds a problem."""
    result = json_object(parameters)
    for name, property_schema in mapping(schema.get("properties")).items():
        declared = mapping(property_schema)
        if name in result or "default" not in declared:
            continue
        candidate = result | {name: json_value(declared["default"])}
        if _problems(schema, candidate) <= _problems(schema, result):
            result = candidate
    return result


def _problems(schema: JsonObject, parameters: JsonObject) -> set[tuple[tuple[str, ...], str]]:
    return {(problem.path, problem.keyword) for problem in schema_problems(schema, parameters)}
