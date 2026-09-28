"""Run only inside a verified component interpreter, without provider credentials or grants."""

import importlib
import json
import sys
from pathlib import Path
from typing import Protocol, cast, runtime_checkable


class Descriptor(Protocol):
    def describe(self, config: object) -> object: ...


@runtime_checkable
class OperationDescription(Protocol):
    @property
    def name(self) -> object: ...
    @property
    def input_schema(self) -> object: ...
    @property
    def output_schema(self) -> object: ...


def operation_record(value: object) -> dict[str, object]:
    if not isinstance(value, OperationDescription):
        raise ValueError("Invalid described operation")
    return {
        "name": value.name,
        "input_schema": value.input_schema,
        "output_schema": value.output_schema,
    }


def main() -> None:
    entry_point, config_path = sys.argv[1:]
    module, name = entry_point.split(":")
    component: object = getattr(importlib.import_module(module), name)
    if not isinstance(component, type) or not callable(getattr(component, "describe", None)):
        raise ValueError("The installed component must publish a describe(config) contract")
    config: object = json.loads(Path(config_path).read_text())
    described: object = cast(Descriptor, component).describe(config)
    if not isinstance(described, tuple) or not described:
        raise ValueError("The component must describe a nonempty tuple of operations")
    values = cast(tuple[object, ...], described)
    sys.stdout.write(json.dumps([operation_record(item) for item in values]))


if __name__ == "__main__":
    main()
