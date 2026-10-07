"""Branches: the naming rule, what a new branch starts from, and the parent of a new version."""

import re

from slow_thinker_ii.contracts import JsonObject

from ._change_records import BranchSummary
from ._errors import BranchNotFound, ChangeNotFound, GraphNotFound, InvalidBranch, VersionNotFound
from ._ports import GraphStore

MAIN = "main"
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}")  # ASCII, so case folding is SQLite's


def checked_name(name: str) -> str:
    if _NAME.fullmatch(name) is None:
        raise InvalidBranch(
            "A branch name has 1 to 40 letters, digits, spaces, dots, underscores or hyphens "
            "and starts with a letter or a digit."
        )
    return name


def existing_branch(store: GraphStore, graph_id: str, name: str) -> BranchSummary:
    """The branch named exactly `name`; raises `GraphNotFound` or `BranchNotFound`."""
    branches = store.branches(graph_id)
    if not branches:
        raise GraphNotFound(graph_id)
    found = next((branch for branch in branches if branch.name == name), None)
    if found is None:
        raise BranchNotFound(graph_id, name)
    return found


def start_document(
    store: GraphStore, graph_id: str, from_version: int | None, from_change: int | None
) -> JsonObject:
    """The document of the one version or change a new branch starts from."""
    if from_version is not None and from_change is None:
        version = store.version(graph_id, from_version)
        if version is None:
            raise VersionNotFound(graph_id, from_version)
        return version.document
    if from_change is not None and from_version is None:
        change = store.change(graph_id, from_change)
        if change is None:
            raise ChangeNotFound(graph_id, from_change)
        return change.document
    raise InvalidBranch("A branch starts from either a version or a change.")


def parent_of(branch: BranchSummary) -> int | None:
    """The branch's head version, or before its first version the version it started from."""
    return branch.from_version if branch.head_version is None else branch.head_version
