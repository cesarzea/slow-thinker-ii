"""Rows of the in-memory graph store: the changes, branches and versions of one graph."""

from dataclasses import dataclass, field
from datetime import datetime

from slow_thinker_ii.application import BranchSummary, ChangeSummary, VersionSummary
from slow_thinker_ii.contracts import JsonObject


@dataclass(frozen=True)
class StoredChange:
    branch: str
    name: str
    at: datetime
    document: JsonObject


@dataclass(frozen=True)
class StoredBranch:
    name: str
    created_at: datetime
    from_version: int | None
    from_change: int | None


@dataclass(frozen=True)
class StoredVersion:
    change: int
    parent: int | None
    at: datetime


@dataclass
class StoredGraph:
    """Change n is `changes[n - 1]` and version n is `versions[n - 1]`, across branches."""

    changes: list[StoredChange]
    branches: list[StoredBranch]
    versions: list[StoredVersion] = field(default_factory=list[StoredVersion])

    def numbers(self, branch: str | None) -> list[int]:
        """Change numbers of one branch, or of every branch, in ascending order."""
        return [n for n, item in enumerate(self.changes, 1) if branch in (None, item.branch)]

    def version_of(self, change: int) -> int | None:
        """The latest version activated from `change`."""
        found = [n for n, item in enumerate(self.versions, 1) if item.change == change]
        return found[-1] if found else None

    def branch_summary(self, branch: StoredBranch) -> BranchSummary:
        heads = [n for n, item in enumerate(self.versions, 1) if self._branch(item) == branch.name]
        head = heads[-1] if heads else None
        latest = self.numbers(branch.name)[-1]
        start = (branch.from_version, branch.from_change)
        return BranchSummary(branch.name, branch.created_at, *start, latest, head)

    def change_summary(self, change: int) -> ChangeSummary:
        item = self.changes[change - 1]
        return ChangeSummary(change, item.branch, item.at, item.name, self.version_of(change))

    def version_summary(self, version: int) -> VersionSummary:
        item = self.versions[version - 1]
        source = self.changes[item.change - 1]
        branch, name = source.branch, source.name
        return VersionSummary(version, branch, item.parent, item.change, name, item.at)

    def _branch(self, version: StoredVersion) -> str:
        return self.changes[version.change - 1].branch
