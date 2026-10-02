"""Browser journeys exercise production HTTP/storage ownership with a deterministic operation."""

import asyncio
import os
import time
from pathlib import Path
from urllib.parse import urlsplit

from slow_thinker_ii.adapters.catalog import ConditionalCompiler, SequenceCompiler
from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteOperatorQueries,
    SqliteOperatorStore,
    SqliteRunStore,
)
from slow_thinker_ii.application import (
    ConditionalProgram,
    ExecutionConfiguration,
    ExecutionCoordinator,
    LimitsProfile,
    PreparedStart,
    PreparedWorkflow,
    SequenceProgram,
    StartIntent,
    library,
    sequence_access,
)
from slow_thinker_ii.bootstrap import ExecutionServices
from slow_thinker_ii.contracts import decode_json, json_object

from .browser_sequence import BrowserSequenceEnvironment
from .browser_snapshot import browser_snapshot
from .conditional import ConditionalEnvironment
from .personal_library import personal_library
from .sequence_plans import SCHEMAS, resolved

BROWSER_TOKEN = "browser_fixture_operator_token_01234567890123456789"


class BrowserPreparation:
    def __init__(
        self, configuration: ExecutionConfiguration, definitions: library.DefinitionReader
    ) -> None:
        self._configuration = configuration
        self._definitions = definitions

    async def prepare(self, intent: StartIntent, runtime_id: str) -> PreparedWorkflow:
        problem = json_object(decode_json(intent.input_json)).get("problem")
        source = self._definitions.definition(intent.graph_id, intent.graph_revision)
        definition = json_object(decode_json(source))
        components = json_object(definition["components"])
        controller = json_object(definition["controller"])
        if json_object(components[str(controller["component"])])["type_id"] == "bounded-flow":
            plan = ConditionalCompiler(SCHEMAS).compile(
                source, intent.input_json, resolved(definition)
            )
            return PreparedWorkflow(
                self._start(intent, runtime_id),
                sequence_access(plan),
                ConditionalEnvironment(plan, str(problem)),
                ConditionalProgram(plan),
            )
        if problem == "prepare-wait":
            await asyncio.sleep(0.5)
        sequence = SequenceCompiler(SCHEMAS).compile(
            source, intent.input_json, resolved(definition)
        )
        return PreparedWorkflow(
            self._start(intent, runtime_id),
            sequence_access(sequence),
            BrowserSequenceEnvironment(sequence, str(problem)),
            SequenceProgram(sequence),
        )

    def _start(self, intent: StartIntent, runtime_id: str) -> PreparedStart:
        return PreparedStart(
            intent, self._configuration, runtime_id, browser_snapshot(intent, self._definitions)
        )


class BrowserExecution:
    def build(self, database: SqliteDatabase, root: Path) -> ExecutionServices:
        del root
        limits = LimitsProfile(
            "browser", 30, 20, 5, 3, 100, 8, 1_048_576, 1_000_000_000, 5_000_000_000, 10_000_000_000
        )
        configuration = ExecutionConfiguration("browser", limits, "{}")
        commands = SqliteOperatorStore(database, limits.max_payload_bytes)
        coordinator = ExecutionCoordinator(
            commands,
            SqliteRunStore(database, limits.max_payload_bytes),
            BrowserPreparation(configuration, personal_library(database)),
            time.monotonic,
            5,
            3,
            4,
        )
        origins = (
            os.environ["SLOW_THINKER_TEST_API_ORIGIN"],
            os.environ["SLOW_THINKER_TEST_BROWSER_ORIGIN"],
        )
        access = OperatorAccess(
            BROWSER_TOKEN, origins, tuple(urlsplit(origin).netloc for origin in origins)
        )
        return ExecutionServices(
            configuration, coordinator, commands, SqliteOperatorQueries(database, b"k" * 32), access
        )
