"""Authenticated bounded workspace discovery and settings/source commands."""

import asyncio

from fastapi import APIRouter, Request, Response

from slow_thinker_ii.application import workspace
from slow_thinker_ii.contracts import decode_json, json_object

from ._definition_input import definition_source, query_fields
from ._definition_replies import definition_reply, definition_text_reply
from ._operator_errors import OperatorError, operator_error

STATUSES = {
    "invalid_patch": 422,
    "invalid_limits": 422,
    "configuration_conflict": 409,
    "configuration_active": 409,
    "budget_below_commitments": 422,
    "response_too_large": 413,
    "operator_service_unavailable": 503,
}


def workspace_router(service: workspace.WorkspaceService, limit: int) -> APIRouter:
    routes = WorkspaceRoutes(service, limit)
    router = APIRouter(prefix="/api/v1")
    router.add_api_route("/configuration/catalog", routes.catalog, methods=["GET"])
    router.add_api_route("/configuration/limits", routes.limits, methods=["POST"])
    router.add_api_route("/definitions/patch", routes.patch, methods=["POST"])
    return router


def failure(error: Exception) -> Response:
    if isinstance(error, workspace.WorkspaceError):
        return operator_error(OperatorError(error.code, STATUSES.get(error.code, 503)))
    return operator_error(error)


class WorkspaceRoutes:
    def __init__(self, service: workspace.WorkspaceService, limit: int) -> None:
        if type(limit) is not int or limit < 1:
            raise ValueError("A positive workspace transport bound is required")
        self._service, self._limit = service, limit

    async def catalog(self, request: Request) -> Response:
        try:
            query_fields(request, set())
            value = await asyncio.to_thread(self._service.catalog)
            return definition_reply(value, self._limit)
        except Exception as error:
            return failure(error)

    async def limits(self, request: Request) -> Response:
        try:
            value = json_object(decode_json(await definition_source(request, self._limit)))
            result = await asyncio.to_thread(self._service.change_limits, value)
            return definition_reply(result, self._limit)
        except (ValueError, RecursionError) as error:
            return failure(
                error
                if isinstance(error, workspace.WorkspaceError)
                else workspace.WorkspaceError("invalid_limits")
            )
        except Exception as error:
            return failure(error)

    async def patch(self, request: Request) -> Response:
        try:
            body = json_object(decode_json(await definition_source(request, self._limit)))
            source, operations = body.get("source"), body.get("operations")
            if (
                set(body) != {"source", "operations"}
                or not isinstance(source, str)
                or not isinstance(operations, list)
            ):
                raise workspace.WorkspaceError("invalid_patch")
            result = await asyncio.to_thread(
                workspace.patch_definition,
                source,
                [json_object(item) for item in operations],
                self._limit,
            )
            return definition_text_reply(result, self._limit)
        except (ValueError, RecursionError) as error:
            return failure(
                error
                if isinstance(error, workspace.WorkspaceError)
                else workspace.WorkspaceError("invalid_patch")
            )
        except Exception as error:
            return failure(error)
