"""Compose equivalent exact-definition readers without opening the database."""

from pathlib import Path
from secrets import token_bytes

from slow_thinker_ii.adapters.catalog import BundledDefinitionStore, GraphDefinitionValidator
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteDefinitionRepository
from slow_thinker_ii.application import library


def experiment_library(
    database: SqliteDatabase, root: Path, descriptors: tuple[str, ...] = ()
) -> library.ExperimentLibrary:
    examples = root / "docs/contracts/examples"
    return library.ExperimentLibrary(
        BundledDefinitionStore(examples),
        SqliteDefinitionRepository(database),
        GraphDefinitionValidator(root / "docs/contracts/schemas", examples, descriptors),
        token_bytes(32),
    )
