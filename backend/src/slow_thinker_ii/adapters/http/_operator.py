"""Compose the authenticated operator command and read routes."""

from fastapi import APIRouter

from slow_thinker_ii.application import ExecutionCoordinator, OperatorQueries, OperatorSessions

from ._operator_auth import OperatorAccess
from ._operator_commands import OperatorCommands
from ._operator_reads import OperatorReads


def operator_router(
    coordinator: ExecutionCoordinator,
    sessions: OperatorSessions,
    queries: OperatorQueries,
    access: OperatorAccess,
    max_body_bytes: int = 1_048_576,
) -> APIRouter:
    if type(max_body_bytes) is not int or max_body_bytes < 1:
        raise ValueError("A positive operator transport bound is required")
    commands = OperatorCommands(coordinator, access, max_body_bytes)
    reads = OperatorReads(queries, sessions, access, max_body_bytes)
    router = APIRouter(prefix="/api/v1")
    router.add_api_route("/sessions", commands.session, methods=["POST"])
    router.add_api_route("/runs", commands.start, methods=["POST"])
    router.add_api_route("/runs/{run_id}/stop", commands.stop, methods=["POST"])
    router.add_api_route("/commands/{command_id}/withdraw", commands.withdraw, methods=["POST"])
    router.add_api_route("/commands/{command_id}", reads.command, methods=["GET"])
    router.add_api_route("/workspace", reads.workspace, methods=["GET"])
    router.add_api_route("/runs/{run_id}", reads.run, methods=["GET"])
    router.add_api_route("/runs/{run_id}/result", reads.result, methods=["GET"])
    router.add_api_route("/runs/{run_id}/definition", reads.definition, methods=["GET"])
    router.add_api_route("/runs/{run_id}/events", reads.events, methods=["GET"])
    router.add_api_route("/runs/{run_id}/calls/{call_id}", reads.call, methods=["GET"])
    router.add_api_route("/runs/{run_id}/payloads/{payload_id}", reads.payload, methods=["GET"])
    router.add_api_route(
        "/runs/{run_id}/activations/{activation_id}", reads.activation, methods=["GET"]
    )
    router.add_api_route("/sessions/{session_id}/runs", reads.session_runs, methods=["GET"])
    return router
