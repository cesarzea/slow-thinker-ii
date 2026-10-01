"""Simulate CodeQL command responses while retaining real Git inventory."""

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

from .reports import JsonObject, report

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class SimulatedCodeQL:
    def __init__(self, real_run: CommandRunner) -> None:
        self.real_run = real_run
        self.documents = {
            "python": report("python", ("source.py",)),
            "javascript": report("javascript", ("frontend/main.ts",)),
        }
        self.version = json.dumps({"version": "2.27.1"})
        self.commands: list[tuple[str, ...]] = []
        self.snapshots: list[dict[str, str]] = []
        self.databases: dict[str, str] = {}
        self.failed_stage: str | None = None
        self.exception: Exception | None = None
        self.inventory: str | None = None
        self.raw_report: str | None = None
        self.write_report = True

    def run(self, arguments: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.commands.append(arguments)
        stage = arguments[1] if arguments[0] == "git" or arguments[1] == "version" else arguments[2]
        if stage == self.failed_stage:
            if self.exception is not None:
                raise self.exception
            return subprocess.CompletedProcess(arguments, 7, "deliberate command failure\n")
        if arguments[0] == "git":
            if self.inventory is not None:
                return subprocess.CompletedProcess(arguments, 0, self.inventory)
            return self.real_run(arguments, **kwargs)
        if arguments[1] == "version":
            return subprocess.CompletedProcess(arguments, 0, self.version)
        if stage == "create":
            self.capture_snapshot(arguments)
        elif stage == "analyze":
            self.save_report(arguments)
        return subprocess.CompletedProcess(arguments, 0, "simulated CodeQL completed\n")

    def capture_snapshot(self, arguments: tuple[str, ...]) -> None:
        language = next(
            value.removeprefix("--language=")
            for value in arguments
            if value.startswith("--language=")
        )
        source = Path(
            next(
                value.removeprefix("--source-root=")
                for value in arguments
                if value.startswith("--source-root=")
            )
        )
        self.databases[arguments[3]] = language
        self.snapshots.append(
            {
                path.relative_to(source).as_posix(): path.read_text()
                for path in source.rglob("*")
                if path.is_file()
            }
        )

    def save_report(self, arguments: tuple[str, ...]) -> None:
        if not self.write_report:
            return
        destination = Path(
            next(
                value.removeprefix("--output=")
                for value in arguments
                if value.startswith("--output=")
            )
        )
        language = self.databases[arguments[3]]
        destination.write_text(
            self.raw_report if self.raw_report is not None else json.dumps(self.documents[language])
        )

    def python_report(self) -> JsonObject:
        return self.documents["python"]
