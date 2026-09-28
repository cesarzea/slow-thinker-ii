"""A local native HTTP provider records exactly what the isolated resource sends."""

import asyncio

from fastapi import FastAPI, Request, Response
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from .native_model import response
from .openai_calls import completion


class Upstream:
    def __init__(self, status: int = 200, *, blocked: bool = False) -> None:
        self.status = status
        self.content = "success"
        self.requests: list[JsonObject] = []
        self.credentials: list[str | None] = []
        self.entered, self.release = asyncio.Event(), asyncio.Event()
        if not blocked:
            self.release.set()
        self.app = FastAPI()
        self.app.add_api_route("/v1/chat/completions", self.complete, methods=["POST"])

    async def complete(self, request: Request) -> Response:
        self.requests.append(json_object(decode_json((await request.body()).decode())))
        self.credentials.append(request.headers.get("authorization"))
        self.entered.set()
        await self.release.wait()
        body: JsonObject = (
            response()
            if self.status == 200
            else {"error": {"message": "fixture failure", "code": "rate_limit"}}
        )
        if self.status == 200:
            body["choices"] = completion(self.content)["choices"]
        return Response(
            encode_json(body),
            status_code=self.status,
            media_type="application/json",
            headers={"x-request-id": "req_upstream"},
        )
