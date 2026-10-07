"""Stored graphs and their activated versions, in their operator API shapes."""

from dataclasses import dataclass
from datetime import datetime

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object

from ._change_records import BranchSummary
from ._records import rfc3339


@dataclass(frozen=True)
class GraphSummary:
    id: str
    name: str  # of the latest change
    active_version: int | None  # the highest version; None before the first activation
    latest_change: int
    updated_at: datetime  # of the latest change

    def to_json(self) -> JsonObject:
        return {
            "id": self.id,
            "name": self.name,
            "active_version": self.active_version,
            "latest_change": self.latest_change,
            "updated_at": rfc3339(self.updated_at),
        }


@dataclass(frozen=True)
class VersionSummary:
    version: int
    branch: str
    parent: int | None  # the version this one follows on its lineage
    change: int  # the change it was activated from
    name: str  # of that change
    created_at: datetime

    def to_json(self) -> JsonObject:
        return {
            "version": self.version,
            "branch": self.branch,
            "parent": self.parent,
            "change": self.change,
            "name": self.name,
            "created_at": rfc3339(self.created_at),
        }


@dataclass(frozen=True)
class GraphRecord:
    id: str
    name: str  # of the latest change
    active_version: int | None
    latest_change: int
    branches: tuple[BranchSummary, ...]  # oldest first
    versions: tuple[VersionSummary, ...]  # oldest first

    def to_json(self) -> JsonObject:
        branches: list[JsonValue] = [branch.to_json() for branch in self.branches]
        versions: list[JsonValue] = [version.to_json() for version in self.versions]
        return {
            "id": self.id,
            "name": self.name,
            "active_version": self.active_version,
            "latest_change": self.latest_change,
            "branches": branches,
            "versions": versions,
        }


@dataclass(frozen=True)
class VersionRecord:
    graph_id: str
    version: int
    branch: str
    parent: int | None
    change: int
    created_at: datetime
    document: JsonObject

    def to_json(self) -> JsonObject:
        return {
            "graph_id": self.graph_id,
            "version": self.version,
            "branch": self.branch,
            "parent": self.parent,
            "change": self.change,
            "created_at": rfc3339(self.created_at),
            "document": json_object(self.document),
        }
