"""Freeze installed contracts without importing component code into the backend."""

import math
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema import Draft202012Validator, SchemaError

from slow_thinker_ii.contracts import OperationContract, decode_json, encode_json, json_object

from ._commands import run
from ._records import Resolution


@dataclass(frozen=True)
class InstalledDescription:
    installation_json: str
    config_json: str
    operations: tuple[OperationContract, ...]


def describe_installed(
    python: Path, resolution: Resolution, config_json: str, timeout_seconds: float
) -> InstalledDescription:
    if (
        isinstance(timeout_seconds, bool)
        or not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
    ):
        raise ValueError("Description timeout must be finite and positive")
    config = encode_json(json_object(decode_json(config_json)))
    with TemporaryDirectory(prefix="slow-thinker-description-") as temporary:
        directory = Path(temporary)
        path = directory / "config.json"
        path.write_text(config)
        output = run(
            [
                str(python),
                "-B",
                "-I",
                str(Path(__file__).with_name("_contract_probe.py")),
                resolution.registration.entry_point,
                str(path),
            ],
            directory,
            timeout_seconds,
        )
    return InstalledDescription(resolution.model_dump_json(), config, parse_operations(output))


def parse_operations(value: str) -> tuple[OperationContract, ...]:
    raw = decode_json(value)
    if not isinstance(raw, list) or not raw:
        raise ValueError("An installed description must contain operations")
    operations: list[OperationContract] = []
    for item in raw:
        record = json_object(item)
        if set(record) != {"name", "input_schema", "output_schema"}:
            raise ValueError("Invalid installed operation fields")
        name = record["name"]
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid installed operation identity")
        incoming, outgoing = (
            json_object(record["input_schema"]),
            json_object(record["output_schema"]),
        )
        try:
            Draft202012Validator.check_schema(incoming)
            Draft202012Validator.check_schema(outgoing)
        except SchemaError as error:
            raise ValueError("Invalid installed operation schema") from error
        operations.append(OperationContract(name, encode_json(incoming), encode_json(outgoing)))
    if len({item.name for item in operations}) != len(operations):
        raise ValueError("Installed operation names must be unique")
    return tuple(operations)
