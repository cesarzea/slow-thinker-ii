"""Production workspace HTTP and SQLite composition, without model execution."""

from dataclasses import dataclass, replace
from pathlib import Path

import httpx
from fastapi import FastAPI
from slow_thinker_ii.adapters.http import OperatorAccess, OperatorBoundary, workspace_router
from slow_thinker_ii.adapters.sqlite import SqliteConfigurationCommands, SqliteModelTariffReader
from slow_thinker_ii.adapters.workspace import WorkspaceCatalog
from slow_thinker_ii.application import ExecutionConfiguration, LimitsProfile, workspace
from slow_thinker_ii.contracts import encode_json

from .operator_commands import OperatorCase, operator_case
from .operator_http import ORIGIN, TOKEN
from .sequence_plans import EXAMPLES, SCHEMAS
from .workspace_data import workspace_descriptors, workspace_resources


def workspace_service(case: OperatorCase, maximum: LimitsProfile) -> workspace.WorkspaceService:
    catalog = WorkspaceCatalog(
        SCHEMAS,
        EXAMPLES,
        workspace_descriptors(),
        case.store.profile,
        maximum,
        SqliteModelTariffReader(case.database),
        case.wall,
    )
    commands = SqliteConfigurationCommands(case.database, case.wall)
    return workspace.WorkspaceService(catalog, commands, maximum)


@dataclass(frozen=True)
class WorkspaceHttp:
    base: OperatorCase
    profile: ExecutionConfiguration
    service: workspace.WorkspaceService
    client: httpx.AsyncClient


def workspace_http(directory: Path, limit: int = 1_048_576) -> WorkspaceHttp:
    case = operator_case(directory)
    profile = replace(
        case.profile, revision="workspace-1", resources_json=encode_json(workspace_resources())
    )
    case.store.configure(profile)
    service = workspace_service(case, profile.limits)
    app = FastAPI()
    app.add_middleware(
        OperatorBoundary, access=OperatorAccess(TOKEN, (ORIGIN,), ("127.0.0.1:8000",))
    )
    app.include_router(workspace_router(service, limit))
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=ORIGIN,
        headers={"authorization": "Bearer " + TOKEN, "origin": ORIGIN},
    )
    return WorkspaceHttp(case, profile, service, client)
