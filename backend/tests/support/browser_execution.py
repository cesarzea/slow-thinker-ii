"""Browser journeys exercise production HTTP/storage ownership with a deterministic operation."""

import asyncio
import os
import time
from pathlib import Path
from urllib.parse import urlsplit

from slow_thinker_ii.access import AccessPolicy
from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteOperatorQueries,
    SqliteOperatorStore,
    SqliteRunStore,
)
from slow_thinker_ii.application import (
    ChargeBasis,
    ChargeEvidence,
    ExecutionConfiguration,
    ExecutionCoordinator,
    LimitsProfile,
    PreparedStart,
    PreparedWorkflow,
    StartIntent,
)
from slow_thinker_ii.bootstrap import ExecutionServices
from slow_thinker_ii.contracts import OperationResult, decode_json, json_object

from .coordinator import TARGET, Environment, Program
from .managed_calls import FixtureOperation

BROWSER_TOKEN = "browser_fixture_operator_token_01234567890123456789"


class BrowserPreparation:
    def __init__(self, configuration: ExecutionConfiguration) -> None:
        self._configuration = configuration

    async def prepare(self, intent: StartIntent, runtime_id: str) -> PreparedWorkflow:
        problem = json_object(decode_json(intent.input_json)).get("problem")
        if problem == "prepare-wait":
            await asyncio.sleep(0.5)
        operation = FixtureOperation(
            ChargeBasis(3000, "fixture", "{}"), ChargeEvidence("{}", 2390, "browser-fixture")
        )
        operation.result = OperationResult(
            '{"nodes":{"draft":{"text":"Resultado de prueba"}}}', False
        )
        if problem == "wait":
            operation.release.clear()
        return PreparedWorkflow(
            PreparedStart(intent, self._configuration, runtime_id, '{"fixture":true}'),
            AccessPolicy((TARGET,), (), (TARGET,)),
            Environment(operation),
            Program(),
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
            BrowserPreparation(configuration),
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
