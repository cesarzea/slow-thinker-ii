"""A launch binding supplies the admitted run and a durable ownership journal."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from slow_thinker_ii.application import OwnedLaunch, ProcessIdentity, ProcessJournal


@dataclass(frozen=True)
class LaunchOwnership:
    journal: ProcessJournal
    launch: OwnedLaunch

    @property
    def marker(self) -> str:
        return self.launch.marker

    def prepare(self) -> None:
        self.journal.prepare(self.launch)

    def started(self, identity: ProcessIdentity) -> None:
        self.journal.started(identity)

    def stopped(self, reason: str) -> None:
        self.journal.stopped(self.marker, reason)


@dataclass(frozen=True)
class GraphOwnership:
    journal: ProcessJournal
    run_id: str
    runtime_id: str

    def host(self, instance: str, workspace: Path) -> LaunchOwnership:
        return LaunchOwnership(
            self.journal,
            OwnedLaunch(uuid4().hex, self.run_id, self.runtime_id, instance, str(workspace)),
        )
