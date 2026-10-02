"""Settings compare/replay, profile activation and commitments in one transaction."""

import sqlite3
import time
from collections.abc import Callable

from slow_thinker_ii.application import ExecutionConfiguration, LimitsProfile, workspace

from ._database import SqliteDatabase
from ._operator_profiles import activate, current_profile


class SqliteConfigurationCommands:
    def __init__(self, database: SqliteDatabase, wall: Callable[[], float] = time.time) -> None:
        self._database, self._wall = database, wall

    def initialize(self, configured: ExecutionConfiguration) -> None:
        with self._database.transaction() as db:
            current = current_profile(db)
            selected = configured
            if (
                current is not None
                and current.resources_json == configured.resources_json
                and current.limits.revision == configured.limits.revision
            ):
                if not workspace.within_limits(current.limits, configured.limits):
                    raise ValueError("Saved settings exceed the current startup ceilings")
                selected = current
            activate(db, selected, self._wall())

    def change(
        self, command: workspace.LimitsCommand, maximum: LimitsProfile
    ) -> workspace.ConfigurationResult:
        with self._database.transaction() as db:
            row = db.execute(
                "SELECT * FROM configuration_commands WHERE command_id=?", (command.command_id,)
            ).fetchone()
            if row is not None:
                if str(row["request_json"]) != command.to_json():
                    raise workspace.WorkspaceError("configuration_conflict")
                return workspace.ConfigurationResult(
                    command.command_id, str(row["configuration_revision"]), True
                )
            profile = current_profile(db)
            if profile is None:
                raise workspace.WorkspaceError("operator_service_unavailable")
            if profile.revision != command.expected_revision:
                raise workspace.WorkspaceError("configuration_conflict")
            active = db.execute(
                "SELECT 1 FROM managed_runs WHERE state IN ('created','running','stopping') LIMIT 1"
            ).fetchone()
            if active is not None:
                raise workspace.WorkspaceError("configuration_active")
            changed = workspace.apply_limits(profile, command, maximum)
            self._activate(db, changed)
            db.execute(
                "INSERT INTO configuration_commands VALUES(?,?,?)",
                (command.command_id, command.to_json(), changed.revision),
            )
            return workspace.ConfigurationResult(command.command_id, changed.revision, False)

    def _activate(self, db: sqlite3.Connection, profile: ExecutionConfiguration) -> None:
        try:
            activate(db, profile, self._wall())
        except ValueError as error:
            raise workspace.WorkspaceError("budget_below_commitments") from error
