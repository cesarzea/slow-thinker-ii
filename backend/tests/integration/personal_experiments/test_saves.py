"""Canonical immutable saves, exact identities and lineage use the public library boundary."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteDefinitionRepository
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.personal_experiments.definitions import PARENT, numeric_source, source, variant


def test_canonical_replay_and_two_revisions_are_independent(
    experiments: library.ExperimentLibrary,
) -> None:
    first, second = source("personal one"), source("personal two", "A later instruction.")
    assert experiments.save(json.dumps(decode_json(first), indent=2)).created
    assert not experiments.save(first).created
    assert experiments.save(second).created
    assert experiments.definition("single-agent", "personal one") == first
    assert experiments.definition("single-agent", "personal two") == second
    assert json_object(decode_json(experiments.detail("single-agent", "personal one")))[
        "definition"
    ] == decode_json(first)
    assert experiments.definition(PARENT.graph_id, PARENT.revision) != first


def test_concurrent_canonical_saves_create_one_row(
    experiments: library.ExperimentLibrary, database: SqliteDatabase
) -> None:
    barrier = Barrier(8)

    def save(_: int) -> library.SaveResult:
        barrier.wait()
        return experiments.save(source("concurrent"))

    with ThreadPoolExecutor(max_workers=8) as workers:
        results = tuple(workers.map(save, range(8)))
    assert sum(result.created for result in results) == 1
    with database.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM personal_definitions").fetchone()[0] == 1


def test_concurrent_different_content_conflicts_atomically(
    experiments: library.ExperimentLibrary,
) -> None:
    barrier = Barrier(2)

    def save(instruction: str) -> str:
        barrier.wait()
        try:
            experiments.save(source("occupied", instruction))
            return "created"
        except library.DefinitionError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = tuple(workers.map(save, ("First instruction.", "Second instruction.")))
    assert sorted(results) == ["created", "definition_conflict"]


def test_bundled_identity_replays_and_rejects_changed_content(
    experiments: library.ExperimentLibrary,
) -> None:
    original = experiments.definition(PARENT.graph_id, PARENT.revision)
    assert not experiments.save(original).created
    changed = variant(PARENT.revision)
    changed.pop("derived_from")
    with pytest.raises(library.DefinitionError) as error:
        experiments.save(encode_json(changed))
    assert error.value.code == "definition_conflict"
    assert experiments.definition(PARENT.graph_id, PARENT.revision) == original


def test_numeric_representation_is_part_of_canonical_identity(
    experiments: library.ExperimentLibrary,
) -> None:
    value = numeric_source()
    assert experiments.save(value).created
    assert not experiments.save(
        experiments.definition("single-agent", "numeric α / version")
    ).created
    with pytest.raises(library.DefinitionError) as error:
        experiments.save(value.replace('"temperature":1.0', '"temperature":1'))
    assert error.value.code == "definition_conflict"


def test_lineage_to_personal_parent_is_retained(experiments: library.ExperimentLibrary) -> None:
    experiments.save(source("parent"))
    draft = experiments.draft(
        library.GraphReference("single-agent", "parent"),
        library.GraphReference("a-variant", "child"),
    )
    assert experiments.save(draft).created
    value = json_object(decode_json(experiments.definition("a-variant", "child")))
    assert value["derived_from"] == {"graph_id": "single-agent", "revision": "parent"}


@pytest.mark.parametrize("self_parent", [False, True])
def test_invalid_lineage_cannot_insert(
    experiments: library.ExperimentLibrary, database: SqliteDatabase, self_parent: bool
) -> None:
    value = variant("child")
    value["derived_from"] = {
        "graph_id": "single-agent",
        "revision": "child" if self_parent else "missing",
    }
    with pytest.raises(library.DefinitionError) as error:
        experiments.save(encode_json(value))
    assert error.value.code == (
        "invalid_definition" if self_parent else "definition_parent_missing"
    )
    with database.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM personal_definitions").fetchone()[0] == 0


def test_repository_parent_check_is_atomic(
    database: SqliteDatabase, experiments: library.ExperimentLibrary
) -> None:
    repository = SqliteDefinitionRepository(database)
    document = experiments.validate(source("child"))
    for parent, code in [
        (library.GraphReference("single-agent", "absent"), "definition_parent_missing"),
        (document.reference, "invalid_definition"),
    ]:
        with pytest.raises(library.DefinitionError) as error:
            repository.insert(replace(document, parent=parent), False)
        assert error.value.code == code
    assert repository.read(document.reference) is None
