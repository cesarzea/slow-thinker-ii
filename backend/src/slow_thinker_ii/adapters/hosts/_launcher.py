"""Launch every package host of a run at once, recording readiness, or fail the start."""

import asyncio
from pathlib import Path

from slow_thinker_ii.application import HostLauncher, RunHosts, StartupFailed
from slow_thinker_ii.contracts import encode_json
from slow_thinker_ii.engine import RunLog
from slow_thinker_ii.graphs import RunPlan

from ._host import Host
from ._process import HostProcess, Launch
from ._protocol import bootstrap_document
from ._readiness import NotReady
from ._records import (
    Part,
    component_of,
    host_name,
    not_installed,
    plan_parts,
    record_failure,
    record_ready,
)
from ._resolution import Target, resolve
from ._run_hosts import HostKey, LocalRunHosts
from ._settings import HostSettings, LaunchTarget


class HostFailure(Exception):
    """A host that did not start; the message is the run's English detail."""


class LocalHostLauncher(HostLauncher):
    """Starts one local process per package node and per embedded component."""

    def __init__(self, targets: LaunchTarget, settings: HostSettings) -> None:
        self._targets = targets
        self._settings = settings

    async def launch(self, run_id: str, plan: RunPlan, log: RunLog) -> RunHosts:
        parts = plan_parts(plan)
        found = await resolve(self._targets, [component_of(part) for part in parts])
        targets = {ref: target for ref, target in found.items() if isinstance(target, Target)}
        if len(targets) != len(found):
            raise not_installed(parts, found, log)
        directory = self._settings.workspace / run_id
        started: dict[HostKey, Host] = {}
        try:
            async with asyncio.TaskGroup() as group:
                for part in parts:
                    target = targets[component_of(part)]
                    group.create_task(self._start(part, target, directory, log, started))
        except BaseExceptionGroup as failures:
            await LocalRunHosts(started, directory).close()
            raise _first(failures) from None
        except BaseException:
            await LocalRunHosts(started, directory).close()
            raise
        return LocalRunHosts(started, directory)

    async def _start(
        self,
        part: Part,
        target: Target,
        directory: Path,
        log: RunLog,
        started: dict[HostKey, Host],
    ) -> None:
        node, position, _ = part
        began = asyncio.get_running_loop().time()
        name = host_name(part)
        try:
            host = self._host(part, target, directory)
            started[(node.id, position)] = host
            await host.start()
        except NotReady as error:
            detail = f"{name} could not start: {error.cause}"
            record_failure(log, part, error.code, detail)
            raise HostFailure(detail) from None
        except asyncio.CancelledError:
            record_failure(log, part, "stopped", f"{name} was stopped before it was ready.")
            raise
        record_ready(log, part, round((asyncio.get_running_loop().time() - began) * 1000))

    def _host(self, part: Part, target: Target, directory: Path) -> Host:
        node, position, component = part
        document = bootstrap_document(node, position, component, self._settings)
        bootstrap = directory / f"{node.id}.{position}.json"
        try:
            directory.mkdir(parents=True, exist_ok=True)
            bootstrap.write_text(encode_json(document) + "\n", encoding="utf-8")
        except OSError as error:
            cause = f"its bootstrap document could not be written: {error}."
            raise NotReady("launch_failed", cause) from error
        settings = self._settings
        launch = Launch(
            target.interpreter,
            target.module,
            bootstrap,
            directory,
            settings.max_message_bytes,
            settings.shutdown_seconds,
        )
        return Host(HostProcess(launch), position, settings.startup_seconds)


def _first(failures: BaseExceptionGroup) -> BaseException:
    """`StartupFailed` with the first host's detail; any unexpected error as it is."""
    errors = list(failures.exceptions)
    unexpected = [error for error in errors if not isinstance(error, HostFailure)]
    return unexpected[0] if unexpected else StartupFailed(str(errors[0]))
