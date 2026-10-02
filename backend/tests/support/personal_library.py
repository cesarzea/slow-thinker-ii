"""Shared real library composition for authoring and browser acceptance fixtures."""

from slow_thinker_ii.adapters.catalog import BundledDefinitionStore, GraphDefinitionValidator
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteDefinitionRepository
from slow_thinker_ii.application import library

from .sequence_plans import EXAMPLES, SCHEMAS


def personal_library(
    database: SqliteDatabase, descriptors: tuple[str, ...] = ()
) -> library.ExperimentLibrary:
    return library.ExperimentLibrary(
        BundledDefinitionStore(EXAMPLES),
        SqliteDefinitionRepository(database),
        GraphDefinitionValidator(SCHEMAS, EXAMPLES, descriptors),
        b"p" * 32,
    )
