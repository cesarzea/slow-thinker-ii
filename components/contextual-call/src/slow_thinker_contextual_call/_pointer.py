"""Strict JSON Pointer selection and isolated context insertion."""

import re

from slow_thinker_host import JsonObject, JsonValue, json_value


def extract(value: JsonValue, pointer: str) -> JsonValue:
    current = value
    for encoded in pointer.split("/")[1:] if pointer else ():
        key = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and re.fullmatch(r"0|[1-9][0-9]*", key):
            index = int(key)
            if index >= len(current):
                raise ValueError("Composition pointer array index does not exist")
            current = current[index]
        else:
            raise ValueError("Composition pointer does not exist")
    return json_value(current)


def insert(arguments: JsonObject, field: str, value: JsonValue) -> None:
    if field in arguments:
        raise ValueError("Configured context field already exists in worker inputs")
    arguments[field] = json_value(value)
