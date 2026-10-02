"""Personal definition reads and immutable writes through the public application library."""

import asyncio

from fastapi import Request, Response

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import decode_json, encode_json

from ._definition_errors import definition_error
from ._definition_input import definition_source, detail_query, draft_body, page_query
from ._definition_replies import definition_reply, definition_text_reply, page_data, reference_data
from ._operator_replies import representation


class DefinitionRoutes:
    def __init__(self, service: library.ExperimentLibrary, limit: int) -> None:
        self._service, self._limit = service, limit

    async def list(self, request: Request) -> Response:
        try:
            limit, cursor = page_query(request)
            page = await asyncio.to_thread(self._service.page, limit, cursor)
            return definition_reply(page_data(page), self._limit)
        except Exception as error:
            return definition_error(error)

    async def detail(self, request: Request) -> Response:
        try:
            reference = detail_query(request)
            content = await asyncio.to_thread(
                self._service.detail, reference.graph_id, reference.revision
            )
            return representation(request, content, self._limit)
        except Exception as error:
            return definition_error(error)

    async def validate(self, request: Request) -> Response:
        try:
            source = await definition_source(request, self._limit)
            document = await asyncio.to_thread(self._service.validate, source)
            value = reference_data(document.reference)
            value["validation_scope"] = "definition"
            return definition_reply(value, self._limit)
        except Exception as error:
            return definition_error(error)

    async def source(self, request: Request) -> Response:
        try:
            reference = detail_query(request)
            content = await asyncio.to_thread(
                self._service.definition, reference.graph_id, reference.revision
            )
            return definition_text_reply(encode_json(decode_json(content)), self._limit)
        except Exception as error:
            return definition_error(error)

    async def draft(self, request: Request) -> Response:
        try:
            source, target = await draft_body(request, self._limit)
            content = await asyncio.to_thread(self._service.draft, source, target)
            return definition_text_reply(content, self._limit)
        except Exception as error:
            return definition_error(error)

    async def save(self, request: Request) -> Response:
        try:
            source = await definition_source(request, self._limit)
            saved = await asyncio.to_thread(self._service.save, source)
            value = reference_data(saved.reference)
            value["created"] = saved.created
            return definition_reply(value, self._limit, 201 if saved.created else 200)
        except Exception as error:
            return definition_error(error)
