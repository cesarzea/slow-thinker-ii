"""The simulated reply to a JSON Schema request is the schema's smallest deterministic instance."""

import pytest
from slow_thinker_ii.adapters.providers import SimulatedProvider
from slow_thinker_ii.contracts import JsonValue, decode_json
from support.examples import FLASH

from .fixtures import chat, model, text_of


async def instance(schema: JsonValue) -> JsonValue:
    response_format: JsonValue = {
        "type": "json_schema",
        "json_schema": {"name": "output", "schema": schema},
    }
    request = chat(FLASH, response_format=response_format)
    return decode_json(text_of(await SimulatedProvider().complete(model(FLASH), request, 30)))


@pytest.mark.parametrize(
    ("schema", "expected"),
    [
        ({"type": "integer", "minimum": 1, "maximum": 10}, 10),
        ({"type": "integer", "minimum": 3}, 3),
        ({"type": "integer"}, 0),
        ({"type": "integer", "maximum": 10.5}, 10),
        ({"type": "integer", "minimum": 1.5}, 2),
        ({"type": "number", "minimum": -1.5, "maximum": 2.5}, 2.5),
        ({"type": "number", "minimum": -1.5}, -1.5),
        ({"type": "number", "maximum": True}, 0),
        ({"type": "string", "maxLength": 3}, "simulated"),
        ({"type": "boolean"}, True),
        ({"type": "array", "minItems": 2}, []),
        ({"type": "null"}, None),
        ({"type": "unknown"}, None),
        ({"enum": ["first", "second"], "type": "string"}, "first"),
        ({"enum": [], "type": "boolean"}, True),
        ({"const": {"fixed": [1]}}, {"fixed": [1]}),
        ({"type": ["null", "string"]}, "simulated"),
        ({"type": ["null"]}, None),
        ({"type": []}, {}),
        ({"minimum": 4}, {}),
        (True, {}),
    ],
)
async def test_each_type_has_its_smallest_value(schema: JsonValue, expected: JsonValue) -> None:
    assert await instance(schema) == expected


async def test_objects_have_only_their_required_properties() -> None:
    schema: JsonValue = {
        "type": "object",
        "required": ["review", "tags", "undeclared", 7],
        "properties": {
            "review": {
                "required": ["score", "accepted"],
                "properties": {
                    "score": {"type": "integer", "maximum": 10},
                    "accepted": {"type": "boolean"},
                    "comment": {"type": "string"},
                },
            },
            "tags": {"type": "array", "items": {"type": "string"}},
            "optional": {"type": "string"},
        },
    }
    assert await instance(schema) == {
        "review": {"score": 10, "accepted": True},
        "tags": [],
        "undeclared": {},
    }


@pytest.mark.parametrize(
    ("schema", "expected"),
    [
        ({"type": "object", "required": "score"}, {}),
        ({"type": "object", "properties": {"score": {"type": "integer"}}}, {}),
        ({"type": "object", "required": ["score"], "properties": ["score"]}, {"score": {}}),
    ],
)
async def test_malformed_object_keywords_give_the_smallest_object(
    schema: JsonValue, expected: JsonValue
) -> None:
    assert await instance(schema) == expected
