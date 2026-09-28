"""Public functional values for message construction and output validation."""

import re
from dataclasses import dataclass
from typing import Literal, TypedDict

from slow_thinker_host import JsonObject, JsonValue


@dataclass(frozen=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ModelResponse:
    text: str


@dataclass(frozen=True)
class OutputIssue:
    path: str
    message: str

    def __post_init__(self) -> None:
        if not self.message or re.fullmatch(r"(?:/(?:[^~/]|~[01])*)*", self.path) is None:
            raise ValueError("Output issues require a JSON Pointer and a non-empty message")


class TextOutput(TypedDict):
    format: Literal["text"]


class JsonOutput(TypedDict):
    format: Literal["json"]
    schema: JsonObject


class LLMCallConfig(TypedDict):
    instructions: str
    input_schema: JsonObject
    parameters: JsonObject
    output: TextOutput | JsonOutput


class TextSuccess(TypedDict):
    status: Literal["ok"]
    format: Literal["text"]
    value: str


class JsonSuccess(TypedDict):
    status: Literal["ok"]
    format: Literal["json"]
    value: JsonValue


class SerializedIssue(TypedDict):
    path: str
    message: str


type OutputFailureCode = Literal[
    "invalid_json", "output_schema_mismatch", "output_validation_failed"
]


class OutputError(TypedDict):
    code: OutputFailureCode
    message: str
    raw_output: str
    issues: list[SerializedIssue]


class FailedOutput(TypedDict):
    status: Literal["error"]
    error: OutputError


type CallResult = TextSuccess | JsonSuccess | FailedOutput


class OutputValidationError(ValueError):
    def __init__(self, issues: tuple[OutputIssue, ...]) -> None:
        if not issues or any(not issue.message for issue in issues):
            raise ValueError("Output validation requires non-empty issues")
        self.issues = issues
        super().__init__("Output validation failed")


class ModelOperationError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)
