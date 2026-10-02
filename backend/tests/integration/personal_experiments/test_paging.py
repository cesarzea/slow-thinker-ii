"""Signed bounded pages freeze insertion windows across subsequent saves."""

import pytest
from slow_thinker_ii.adapters.catalog import BundledDefinitionStore, GraphDefinitionValidator
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteDefinitionRepository
from slow_thinker_ii.application import library
from support.personal_experiments.definitions import source
from support.sequence_plans import EXAMPLES, SCHEMAS


def all_pages(
    experiments: library.ExperimentLibrary, first: library.LibraryPage, limit: int
) -> tuple[library.LibraryItem, ...]:
    items, cursor = list(first.items), first.next_cursor
    while cursor is not None:
        page = experiments.page(limit, cursor)
        items.extend(page.items)
        cursor = page.next_cursor
    return tuple(items)


def test_bundled_first_pages_exclude_new_personal_saves(
    experiments: library.ExperimentLibrary,
) -> None:
    experiments.save(source("first"))
    experiments.save(source("second"))
    first = experiments.page(2)
    assert len(first.items) == 2 and all(item.origin == "bundled" for item in first.items)
    experiments.save(source("later"))
    items = all_pages(experiments, first, 2)
    assert [item.origin for item in items] == ["bundled"] * 5 + ["personal"] * 2
    assert [item.summary.revision for item in items[-2:]] == ["first", "second"]
    assert experiments.page(100).items[-1].summary.revision == "later"
    assert items[-1].parent == library.GraphReference("single-agent", "example-2")


def test_fixed_empty_personal_window_and_cursor_page_size(
    experiments: library.ExperimentLibrary,
) -> None:
    first = experiments.page(1)
    experiments.save(source("new"))
    assert len(all_pages(experiments, first, 1)) == 5
    with pytest.raises(library.DefinitionError) as error:
        experiments.page(2, first.next_cursor)
    assert error.value.code == "invalid_cursor"


@pytest.mark.parametrize("limit", [0, 101, -1, True])
def test_page_size_is_rejected_instead_of_clamped(
    experiments: library.ExperimentLibrary, limit: int
) -> None:
    with pytest.raises(library.DefinitionError) as error:
        experiments.page(limit)
    assert error.value.code == "invalid_query"


@pytest.mark.parametrize("cursor", ["invalid", "x" * 1025, "é.unsigned"])
def test_malformed_cursor_is_rejected(experiments: library.ExperimentLibrary, cursor: str) -> None:
    with pytest.raises(library.DefinitionError) as error:
        experiments.page(cursor=cursor)
    assert error.value.code == "invalid_cursor"


def test_tampered_and_foreign_process_cursors_are_rejected(
    database: SqliteDatabase, experiments: library.ExperimentLibrary
) -> None:
    cursor = experiments.page(1).next_cursor
    assert cursor is not None
    tampered = cursor[:-1] + ("0" if cursor[-1] != "0" else "1")
    foreign = library.ExperimentLibrary(
        BundledDefinitionStore(EXAMPLES),
        SqliteDefinitionRepository(database),
        GraphDefinitionValidator(SCHEMAS, EXAMPLES),
        b"f" * 32,
    )
    for reader, token in [(experiments, tampered), (foreign, cursor)]:
        with pytest.raises(library.DefinitionError) as error:
            reader.page(1, token)
        assert error.value.code == "invalid_cursor"


def test_repository_zero_limit_fixes_boundary(
    database: SqliteDatabase, experiments: library.ExperimentLibrary
) -> None:
    experiments.save(source("one"))
    repository = SqliteDefinitionRepository(database)
    boundary = repository.page(0, None, 0)
    assert boundary.definitions == () and boundary.has_more and boundary.last == 0
    experiments.save(source("two"))
    fixed = repository.page(0, boundary.through, 100)
    assert len(fixed.definitions) == 1 and not fixed.has_more
