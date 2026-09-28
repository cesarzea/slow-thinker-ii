"""Schema issues retain exact text and use escaped JSON Pointer paths."""

from jsonschema import Draft202012Validator, ValidationError, validate
from referencing import Registry
from slow_thinker_host import JsonObject, JsonValue

from ._types import FailedOutput, OutputError, OutputFailureCode, OutputIssue, SerializedIssue


def schema_issue(value: JsonValue, schema: JsonObject) -> OutputIssue | None:
    try:
        validate(value, schema, cls=Draft202012Validator, registry=Registry[JsonValue]())
    except ValidationError as error:
        path = "".join(
            "/" + str(part).replace("~", "~0").replace("/", "~1") for part in error.absolute_path
        )
        return OutputIssue(path, error.message)
    return None


def failure(
    code: OutputFailureCode, raw_output: str, issues: tuple[OutputIssue, ...]
) -> FailedOutput:
    return FailedOutput(
        status="error",
        error=OutputError(
            code=code,
            message=code.replace("_", " "),
            raw_output=raw_output,
            issues=[SerializedIssue(path=issue.path, message=issue.message) for issue in issues],
        ),
    )
