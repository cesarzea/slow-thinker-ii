"""Branches of a graph and the changes of their working copies, in operator API shapes."""

from dataclasses import dataclass
from datetime import datetime

from slow_thinker_ii.contracts import JsonObject, json_object

from ._records import rfc3339


@dataclass(frozen=True)
class BranchSummary:
    name: str
    created_at: datetime
    from_version: int | None  # what the branch started from; both None for main
    from_change: int | None
    latest_change: int
    head_version: int | None  # the branch's latest version

    def to_json(self) -> JsonObject:
        return {
            "name": self.name,
            "created_at": rfc3339(self.created_at),
            "from_version": self.from_version,
            "from_change": self.from_change,
            "latest_change": self.latest_change,
            "head_version": self.head_version,
        }


@dataclass(frozen=True)
class ChangeSummary:
    change: int
    branch: str
    at: datetime
    name: str  # of its document
    version: int | None  # the latest version activated from it, or None

    def to_json(self) -> JsonObject:
        return {
            "change": self.change,
            "branch": self.branch,
            "at": rfc3339(self.at),
            "name": self.name,
            "version": self.version,
        }


@dataclass(frozen=True)
class ChangeRecord:
    graph_id: str
    change: int
    branch: str
    at: datetime
    document: JsonObject  # a draft: it may have diagnostics
    version: int | None

    def to_json(self) -> JsonObject:
        return {
            "graph_id": self.graph_id,
            "change": self.change,
            "branch": self.branch,
            "at": rfc3339(self.at),
            "document": json_object(self.document),
            "version": self.version,
        }
