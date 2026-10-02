"""Independent real SQLite stores and reusable description-only preparation installations."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import GraphDefinitionValidator, TypeInstallation
from slow_thinker_ii.adapters.sqlite import SqliteDatabase
from slow_thinker_ii.application import library
from support.installed_graphs import types
from support.personal_library import personal_library
from support.preparation import PreparationCase
from support.sequence_plans import EXAMPLES, SCHEMAS


@pytest.fixture
def database(tmp_path: Path) -> SqliteDatabase:
    value = SqliteDatabase(tmp_path / "library.sqlite")
    value.initialize()
    return value


@pytest.fixture
def experiments(database: SqliteDatabase) -> library.ExperimentLibrary:
    return personal_library(database)


@pytest.fixture
def validator() -> GraphDefinitionValidator:
    return GraphDefinitionValidator(SCHEMAS, EXAMPLES)


@pytest.fixture(scope="module")
def installed_types(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, tuple[TypeInstallation, ...]]:
    directory = tmp_path_factory.mktemp("personal-description-installations")
    return directory, types(directory)


@pytest.fixture
def preparation(
    tmp_path: Path, installed_types: tuple[Path, tuple[TypeInstallation, ...]]
) -> PreparationCase:
    directory, selected = installed_types
    return PreparationCase(tmp_path, directory, selected)
