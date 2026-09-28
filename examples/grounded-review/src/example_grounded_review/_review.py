"""Citations must belong to the supplied sources; claim support is not assessed."""

from slow_thinker_llm_call import JsonObject, JsonValue, LLMCall, OutputIssue, OutputValidationError


def _strings(value: JsonValue) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("Expected a validated string array")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise TypeError("Expected a validated string array")
        result.append(item)
    return result


class GroundedReview(LLMCall):
    def validate_result(self, value: JsonValue, arguments: JsonObject) -> None:
        super().validate_result(value, arguments)
        if not isinstance(value, dict):
            raise TypeError("Expected a validated review object")
        allowed = set(_strings(arguments["available_sources"]))
        cited = set(_strings(value["citations"]))
        unknown = cited - allowed
        if unknown:
            issue = OutputIssue("/citations", f"Unknown sources: {', '.join(sorted(unknown))}")
            raise OutputValidationError((issue,))
