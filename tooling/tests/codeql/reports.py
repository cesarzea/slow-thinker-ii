"""Build small SARIF fixtures matching the bundled CodeQL report structure."""

from typing import cast

JsonObject = dict[str, object]
FieldPath = tuple[str | int, ...]


def report(language: str, paths: tuple[str, ...]) -> JsonObject:
    prefix = {"python": "py", "javascript": "js"}[language]
    identifiers = (
        f"{prefix}/baseline/expected-extracted-files",
        f"{prefix}/diagnostics/successfully-extracted-files",
    )
    driver: JsonObject = {
        "name": "CodeQL",
        "semanticVersion": "2.27.1",
        "rules": [{"id": "owned/rule", "defaultConfiguration": {"level": "note"}}],
        "notifications": [{"id": identifier} for identifier in identifiers],
    }
    invocation: JsonObject = {
        "executionSuccessful": True,
        "toolExecutionNotifications": [
            notification(identifier, index, paths) for index, identifier in enumerate(identifiers)
        ],
    }
    run: JsonObject = {
        "tool": {"driver": driver},
        "invocations": [invocation],
        "artifacts": [{"location": {"uri": path}} for path in paths],
        "results": [{"ruleId": "owned/rule", "ruleIndex": 0, "level": "note"}],
    }
    return {"version": "2.1.0", "runs": [run]}


def notification(identifier: str, index: int, paths: tuple[str, ...]) -> JsonObject:
    return {
        "descriptor": {"id": identifier, "index": index},
        "level": "none",
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": path, "uriBaseId": "%SRCROOT%", "index": i}
                }
            }
            for i, path in enumerate(paths)
        ],
    }


def field(document: object, path: FieldPath) -> object:
    value = document
    for key in path:
        if isinstance(key, int):
            value = cast(list[object], value)[key]
        else:
            value = cast(JsonObject, value)[key]
    return value


def replace(document: object, path: FieldPath, value: object) -> None:
    parent = field(document, path[:-1])
    key = path[-1]
    if isinstance(key, int):
        cast(list[object], parent)[key] = value
    else:
        cast(JsonObject, parent)[key] = value


def remove(document: object, path: FieldPath) -> None:
    parent = field(document, path[:-1])
    key = path[-1]
    if isinstance(key, int):
        del cast(list[object], parent)[key]
    else:
        del cast(JsonObject, parent)[key]
