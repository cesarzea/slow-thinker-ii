"""Bounded authenticated personal graph authoring routes."""

from fastapi import APIRouter

from slow_thinker_ii.application import library

from ._definition_routes import DefinitionRoutes


def definition_router(service: library.ExperimentLibrary, max_payload_bytes: int) -> APIRouter:
    if type(max_payload_bytes) is not int or max_payload_bytes < 1:
        raise ValueError("A positive definition transport bound is required")
    routes = DefinitionRoutes(service, max_payload_bytes)
    router = APIRouter(prefix="/api/v1/definitions")
    router.add_api_route("", routes.list, methods=["GET"])
    router.add_api_route("/detail", routes.detail, methods=["GET"])
    router.add_api_route("/source", routes.source, methods=["GET"])
    router.add_api_route("/draft", routes.draft, methods=["POST"])
    router.add_api_route("/validate", routes.validate, methods=["POST"])
    router.add_api_route("", routes.save, methods=["POST"])
    return router
