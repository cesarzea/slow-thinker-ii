"""Repository bounds and ordinary unparented definitions obey the public application ports."""

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteDefinitionRepository
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import encode_json
from support.personal_experiments.definitions import variant


@pytest.mark.parametrize(
    "after,through,limit",
    [
        (0, None, -1),
        (0, None, 101),
        (0, None, True),
        (False, None, 1),
        (-1, None, 1),
        (2, 1, 1),
        (0, False, 1),
        (0, 2**63, 1),
    ],
)
def test_repository_rejects_invalid_window_or_size(
    database: SqliteDatabase, after: int, through: int | None, limit: int
) -> None:
    with pytest.raises(ValueError, match="Invalid personal definition page"):
        SqliteDefinitionRepository(database).page(after, through, limit)


def test_personal_definition_without_parent_is_valid(
    experiments: library.ExperimentLibrary,
) -> None:
    value = variant("independent")
    value.pop("derived_from")
    validated = experiments.validate(encode_json(value))
    assert validated.parent is None
    assert experiments.save(validated.definition_json).created
    assert experiments.page(100).items[-1].parent is None


def test_validate_checks_personal_parent_without_persisting(
    experiments: library.ExperimentLibrary, database: SqliteDatabase
) -> None:
    value = variant("unsaved")
    value["derived_from"] = {"graph_id": "single-agent", "revision": "absent"}
    with pytest.raises(library.DefinitionError) as error:
        experiments.validate(encode_json(value))
    assert error.value.code == "definition_parent_missing"
    assert SqliteDefinitionRepository(database).page(0, None, 100).definitions == ()
