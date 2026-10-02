"""Source edits preserve unrelated exact values and reject partial or ambiguous edits."""

import pytest
from slow_thinker_ii.application import workspace
from slow_thinker_ii.contracts import JsonObject, decode_json, json_object


@pytest.mark.parametrize(
    "operations, expected",
    [
        ([{"op": "add", "path": "/new", "value_json": "true"}], {"new": True}),
        ([{"op": "replace", "path": "/name", "value_json": '"new"'}], {"name": "new"}),
        ([{"op": "remove", "path": "/name"}], {}),
        ([{"op": "replace", "path": "", "value_json": '{"root":1}'}], {"root": 1}),
    ],
)
def test_object_patch(operations: list[JsonObject], expected: JsonObject) -> None:
    result = json_object(
        decode_json(workspace.patch_definition('{"name":"old"}', operations, 1024))
    )
    if operations[0]["op"] == "add":
        assert result == {"name": "old", **expected}
    else:
        assert result == expected


def test_nested_array_edits_and_escaped_keys_preserve_source_numbers() -> None:
    source = '{"a/b":{"~k":[1,2,3]},"big":9007199254740993,"float":1.0}'
    changed = workspace.patch_definition(
        source,
        [
            {"op": "add", "path": "/a~1b/~0k/1", "value_json": "4"},
            {"op": "replace", "path": "/a~1b/~0k/0", "value_json": "5"},
            {"op": "remove", "path": "/a~1b/~0k/2"},
            {"op": "add", "path": "/a~1b/~0k/-", "value_json": "6"},
        ],
        1024,
    )
    assert json_object(decode_json(changed))["a/b"] == {"~k": [5, 4, 3, 6]}
    assert '"big":9007199254740993' in changed and '"float":1.0' in changed
    assert source.endswith('"float":1.0}')


@pytest.mark.parametrize(
    "operation",
    [
        {},
        {"op": "move", "path": "/name"},
        {"op": "add", "path": 1, "value_json": "1"},
        {"op": "add", "path": "/name", "value_json": 1},
        {"op": "add", "path": "/name", "value_json": "NaN"},
        {"op": "add", "path": "/name", "value_json": "1", "unknown": 1},
        {"op": "remove", "path": "/name", "value_json": "1"},
        {"op": "remove", "path": ""},
        {"op": "replace", "path": "", "value_json": "[]"},
        {"op": "replace", "path": "name", "value_json": "1"},
        {"op": "replace", "path": "/~2", "value_json": "1"},
        {"op": "replace", "path": "/missing", "value_json": "1"},
        {"op": "replace", "path": "/name/child", "value_json": "1"},
        {"op": "replace", "path": "/items/01", "value_json": "1"},
        {"op": "replace", "path": "/items/-", "value_json": "1"},
        {"op": "replace", "path": "/items/2", "value_json": "1"},
        {"op": "replace", "path": "/items/-1", "value_json": "1"},
        {"op": "replace", "path": "/items/0/no", "value_json": "1"},
        {"op": "replace", "path": "/" * 65, "value_json": "1"},
        {"op": "replace", "path": "/" + "x" * 4096, "value_json": "1"},
    ],
)
def test_invalid_edit_never_returns_partly_changed_source(operation: JsonObject) -> None:
    source = '{"name":"old","items":[1]}'
    with pytest.raises(workspace.WorkspaceError, match="invalid_patch"):
        workspace.patch_definition(
            source,
            [
                {"op": "replace", "path": "/name", "value_json": '"first"'},
                operation,
            ],
            16384,
        )
    assert source == '{"name":"old","items":[1]}'


@pytest.mark.parametrize(
    "source, count, limit",
    [
        ('{"x":1,"x":2}', 1, 1024),
        ("[]", 1, 1024),
        ("{}", 0, 1024),
        ("{}", 129, 16384),
        ('{"x":"long"}', 1, 2),
        ("{", 1, 1024),
        ('{"x":"\ud800"}', 1, 1024),
    ],
)
def test_patch_input_bounds(source: str, count: int, limit: int) -> None:
    edits: list[JsonObject] = [{"op": "add", "path": "/x", "value_json": "1"}] * count
    with pytest.raises(workspace.WorkspaceError, match="invalid_patch"):
        workspace.patch_definition(source, edits, limit)


def test_patch_response_bound_and_nested_array_parent() -> None:
    with pytest.raises(workspace.WorkspaceError, match="response_too_large"):
        workspace.patch_definition("{}", [{"op": "add", "path": "/x", "value_json": '"abcd"'}], 3)
    result = workspace.patch_definition(
        '{"a":[{}]}',
        [
            {"op": "add", "path": "/a/0/key", "value_json": "null"},
        ],
        100,
    )
    assert decode_json(result) == {"a": [{"key": None}]}
