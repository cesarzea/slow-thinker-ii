"""Validate finding rule references and their effective severity."""

from ._descriptors import referenced_descriptor
from ._shapes import array_value, object_value
from ._types import CodeQLFailure

LEVELS = frozenset({"none", "note", "warning", "error"})


def severity(value: object, context: str) -> str:
    if not isinstance(value, str) or value not in LEVELS:
        raise CodeQLFailure(f"{context} severity is absent or unknown: {value!r}")
    return value


def result_severity(result: dict[str, object], rules: list[dict[str, object]]) -> str:
    if array_value(result.get("suppressions", []), "Result suppressions"):
        raise CodeQLFailure("SARIF contains suppressed source findings")
    reference = _rule_reference(result)
    rule = referenced_descriptor(reference, rules, "Result rule")
    if "level" in result:
        return severity(result["level"], "Result")
    configuration = object_value(rule.get("defaultConfiguration"), "Rule defaultConfiguration")
    return severity(configuration.get("level"), "Rule default")


def _rule_reference(result: dict[str, object]) -> dict[str, object]:
    reference = dict(object_value(result["rule"], "Result rule") if "rule" in result else {})
    if "toolComponent" in reference:
        raise CodeQLFailure("Result rule must belong to the CodeQL driver")
    for source, target in (("ruleId", "id"), ("ruleIndex", "index")):
        if source not in result:
            continue
        if target in reference and reference[target] != result[source]:
            raise CodeQLFailure("Result contains contradictory rule references")
        reference[target] = result[source]
    return reference
