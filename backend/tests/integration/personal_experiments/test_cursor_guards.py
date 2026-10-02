"""Authenticated cursor content must still obey its scope, type and window constraints."""

from base64 import urlsafe_b64encode
from hashlib import sha256
from hmac import new

import pytest
from slow_thinker_ii.adapters.catalog import BundledDefinitionStore, GraphDefinitionValidator
from slow_thinker_ii.adapters.sqlite import SqliteDatabase
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from support.sequence_plans import EXAMPLES, SCHEMAS

KEY = b"test-cursor-signing-key-at-least-32-bytes"


def signed(value: JsonValue) -> str:
    body = encode_json(value).encode()
    return urlsafe_b64encode(body).decode() + "." + new(KEY, body, sha256).hexdigest()


@pytest.mark.parametrize(
    "field,replacement",
    [
        ("extra", 1),
        ("scope", "other-window"),
        ("limit", True),
        ("limit", 49),
        ("bundle", -1),
        ("bundle", 6),
        ("bundle", False),
        ("after", -1),
        ("after", False),
        ("through", None),
        ("through", False),
        ("through", 2**63),
        ("after", 2),
    ],
)
def test_authenticated_but_invalid_cursor_fields_are_rejected(
    database: SqliteDatabase, field: str, replacement: JsonValue
) -> None:
    value: JsonObject = {
        "scope": "definitions-v1",
        "limit": 50,
        "bundle": 0,
        "after": 0,
        "through": 1,
    }
    value[field] = replacement
    experiments = custom_library(database)
    with pytest.raises(library.DefinitionError) as error:
        experiments.page(50, signed(value))
    assert error.value.code == "invalid_cursor"


def test_authenticated_cursor_cannot_skip_personal_rows_before_bundles(
    database: SqliteDatabase,
) -> None:
    value: JsonObject = {
        "scope": "definitions-v1",
        "limit": 50,
        "bundle": 0,
        "after": 1,
        "through": 1,
    }
    with pytest.raises(library.DefinitionError) as error:
        custom_library(database).page(50, signed(value))
    assert error.value.code == "invalid_cursor"


def test_authenticated_cursor_requires_object_content(database: SqliteDatabase) -> None:
    with pytest.raises(library.DefinitionError) as error:
        custom_library(database).page(50, signed([]))
    assert error.value.code == "invalid_cursor"


def custom_library(database: SqliteDatabase) -> library.ExperimentLibrary:
    from slow_thinker_ii.adapters.sqlite import SqliteDefinitionRepository

    return library.ExperimentLibrary(
        BundledDefinitionStore(EXAMPLES),
        SqliteDefinitionRepository(database),
        GraphDefinitionValidator(SCHEMAS, EXAMPLES),
        KEY,
    )
