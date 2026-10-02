"""Unsaved variants and unusual identities preserve exact backend JSON values."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import BundledDefinitionStore, GraphDefinitionValidator
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteDefinitionRepository
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import decode_json, json_object
from support.personal_experiments.definitions import PARENT, numeric_source, source


def test_draft_preserves_all_values_except_identity_and_lineage(
    experiments: library.ExperimentLibrary, database: SqliteDatabase
) -> None:
    original = numeric_source()
    parent = experiments.save(original).reference
    target = library.GraphReference("numeric-variant", "draft β / new")
    draft = experiments.draft(parent, target)
    value = json_object(decode_json(draft))
    expected = json_object(decode_json(original))
    expected.update(
        graph_id=target.graph_id,
        revision=target.revision,
        derived_from={"graph_id": parent.graph_id, "revision": parent.revision},
    )
    assert value == expected and '"temperature":1.0' in draft and "9007199254740993" in draft
    assert SqliteDefinitionRepository(database).read(target) is None
    assert experiments.definition(parent.graph_id, parent.revision) == original
    assert experiments.save(draft).created


@pytest.mark.parametrize(
    "revision", ["α / revision with spaces", "emoji 🧭", "x" * 257, "line\nbreak"]
)
def test_schema_valid_revisions_survive_save_detail_and_draft(
    experiments: library.ExperimentLibrary, revision: str
) -> None:
    reference = experiments.save(source(revision)).reference
    assert reference.revision == revision
    assert (
        json_object(decode_json(experiments.detail(reference.graph_id, revision)))["revision"]
        == revision
    )
    copied = json_object(
        decode_json(experiments.draft(reference, library.GraphReference("new-variant", revision)))
    )
    assert copied["derived_from"] == {"graph_id": reference.graph_id, "revision": revision}


def test_unknown_source_and_self_derivation_errors(experiments: library.ExperimentLibrary) -> None:
    unknown = library.GraphReference("single-agent", "absent")
    for operation in (
        lambda: experiments.definition(unknown.graph_id, unknown.revision),
        lambda: experiments.detail(unknown.graph_id, unknown.revision),
        lambda: experiments.draft(unknown, PARENT),
    ):
        with pytest.raises(library.DefinitionError) as error:
            operation()
        assert error.value.code == "definition_not_found"
    with pytest.raises(library.DefinitionError) as error:
        experiments.draft(PARENT, PARENT)
    assert error.value.code == "invalid_definition"


def test_draft_does_not_reserve_an_occupied_target(experiments: library.ExperimentLibrary) -> None:
    existing = source("occupied", "Keep the existing target.")
    experiments.save(existing)
    draft = experiments.draft(PARENT, library.GraphReference("single-agent", "occupied"))
    assert experiments.definition("single-agent", "occupied") == existing
    with pytest.raises(library.DefinitionError) as error:
        experiments.save(draft)
    assert error.value.code == "definition_conflict"


def test_public_constructors_do_not_access_storage(tmp_path: Path) -> None:
    missing = tmp_path / "uncreated"
    repository = SqliteDefinitionRepository(SqliteDatabase(missing / "state.sqlite"))
    validator = GraphDefinitionValidator(missing / "schemas", missing / "descriptors")
    library.ExperimentLibrary(BundledDefinitionStore(missing), repository, validator, b"k" * 32)
    assert not missing.exists()
    with pytest.raises(library.DefinitionError) as error:
        validator.validate('{"duplicate":1,"duplicate":2}')
    assert error.value.code == "invalid_json" and not missing.exists()
    with pytest.raises(ValueError):
        library.ExperimentLibrary(BundledDefinitionStore(missing), repository, validator, b"short")
