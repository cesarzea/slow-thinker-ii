"""The server configuration document: bounded reading and its JSON shape.

Validation messages name the offending location and never repeat a configured value.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from slow_thinker_ii.contracts import JsonValue, decode_json, encode_json, format_pointer

MAX_BYTES = 1_048_576
REFUSED_NAME = "slow-thinker.keys.json"


class Section(BaseModel, extra="forbid", strict=True, frozen=True):
    """Unknown members are refused; JSON types are not coerced."""


class ServerDocument(Section, frozen=True):
    public_url: str
    allowed_hosts: tuple[str, ...] = Field(min_length=1)
    allowed_origins: tuple[str, ...] = ()
    static_directory: str | None = None
    operator_authentication: Literal["token", "none"] = "token"


class ComponentsDocument(Section, frozen=True):
    installation_root: str = Field(min_length=1)
    uv: str = Field(min_length=1)
    python: str = Field(min_length=1)
    resolutions: tuple[str, ...] = ()


class ProviderDocument(Section, frozen=True):
    base_url: str = Field(min_length=1)
    credential_env: str = Field(pattern=r"^[A-Z_][A-Z0-9_]*$")
    timeout_seconds: float = Field(default=120, gt=0, le=3600)


class SimulatedDocument(Section, frozen=True):
    """The simulated provider has no endpoint and no credential; replies are set per model."""


class ProvidersDocument(Section, frozen=True):
    openai: ProviderDocument | None = None
    deepseek: ProviderDocument | None = None
    simulated: SimulatedDocument | None = None


class ModelDocument(Section, frozen=True):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*/[a-z0-9][a-z0-9.-]*$")
    label: str = Field(min_length=1, max_length=60)
    provider: str
    model: str = Field(min_length=1)
    max_output_tokens: int = Field(gt=0)
    default_output_tokens: int = Field(gt=0)
    reasoning_efforts: tuple[str, ...]
    temperature: Literal["unsupported", "supported", "without_reasoning"]
    tariff: dict[str, JsonValue]
    replies: tuple[str, ...] | None = None  # scripted replies; provider `simulated` only


class LlmDocument(Section, frozen=True):
    providers: ProvidersDocument
    models: tuple[ModelDocument, ...] = Field(min_length=1)


class BudgetsDocument(Section, frozen=True):
    daily_usd: str
    monthly_usd: str


class RuntimeDocument(Section, frozen=True):
    max_active_runs: int = Field(default=4, ge=1, le=64)
    max_activation_seconds: int = Field(default=300, ge=1, le=86_400)
    host_startup_seconds: float = Field(default=20, gt=0, le=600)


class ConfigurationDocument(Section, frozen=True):
    database: str = Field(min_length=1)
    workspace: str = Field(min_length=1)
    server: ServerDocument
    components: ComponentsDocument
    llm: LlmDocument
    budgets: BudgetsDocument
    runtime: RuntimeDocument = RuntimeDocument()


def read_document(path: Path) -> ConfigurationDocument:
    """The validated document; `ValueError` names the file or each invalid location."""
    if path.name == REFUSED_NAME or path.resolve().name == REFUSED_NAME:
        raise ValueError(f"The file {REFUSED_NAME} cannot be used as server configuration.")
    try:
        with path.open("rb") as source:
            content = source.read(MAX_BYTES + 1)
    except OSError as error:
        raise ValueError(
            f"Cannot read the server configuration {path}: {error.strerror}."
        ) from None
    if len(content) > MAX_BYTES:
        raise ValueError("The server configuration must not exceed 1 MiB.")
    try:
        text = encode_json(decode_json(content.decode("utf-8")))
        return ConfigurationDocument.model_validate_json(text)
    except ValidationError as error:
        raise ValueError(f"Invalid server configuration: {problems(error)}.") from None
    except ValueError as error:
        raise ValueError(f"The server configuration is not valid JSON: {error}.") from None


def invalid(pointer: str, reason: str) -> ValueError:
    """The error of one invalid location; `reason` never repeats a configured secret."""
    return ValueError(f"Invalid server configuration: {pointer}: {reason}.")


def problems(error: ValidationError) -> str:
    """`<JSON Pointer>: <reason>` for each problem, without the input values."""
    details = error.errors(include_url=False, include_input=False, include_context=False)
    return "; ".join(f"{format_pointer(item['loc']) or '/'}: {item['msg']}" for item in details)
