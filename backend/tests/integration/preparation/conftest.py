"""Reuse immutable synthetic installations; each case gets its own configuration and storage."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import TypeInstallation
from support.installed_graphs import types
from support.preparation import PreparationCase


@pytest.fixture(scope="module")
def installed_types(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, tuple[TypeInstallation, ...]]:
    directory = tmp_path_factory.mktemp("preparation-installations")
    return directory, types(directory)


@pytest.fixture
def case(
    tmp_path: Path, installed_types: tuple[Path, tuple[TypeInstallation, ...]]
) -> PreparationCase:
    directory, selected = installed_types
    return PreparationCase(tmp_path, directory, selected)
