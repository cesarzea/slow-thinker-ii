"""Strict JSON Pointer extraction, including escaped names and array indices."""

import re

from slow_thinker_host import JsonValue


def extract(value: JsonValue, pointer: str) -> JsonValue:
    current = value
    for encoded in pointer.split("/")[1:] if pointer else ():
        key = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and re.fullmatch(r"0|[1-9][0-9]*", key):
            index = int(key)
            if index >= len(current):
                raise ValueError("Router input array index does not exist")
            current = current[index]
        else:
            raise ValueError("Router input pointer does not exist in worker output")
    return current
