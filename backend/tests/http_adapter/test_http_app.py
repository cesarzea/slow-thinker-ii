"""Settings validation, the supplied lifespan and the compiled interface served at the root."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi import FastAPI
from slow_thinker_ii.adapters.http import create_http_app
from support.platform import Platform

from .http_harness import TOKEN, error, http_settings, operator_api, services

TOKEN_RULE = "The operator token must be 32 to 128 visible ASCII characters without spaces."
HOST_RULE = "At least one allowed host is required, each without spaces."
BOUND_RULE = "The request body bound must be a positive number of bytes."


def origin_rule(origin: str) -> str:
    return f"The allowed origin “{origin}” must be exactly scheme://host[:port]."


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("operator_token", "too-short", TOKEN_RULE),
        ("operator_token", "t" * 129, TOKEN_RULE),
        ("operator_token", f"{TOKEN} x", TOKEN_RULE),
        ("operator_token", "é" * 40, TOKEN_RULE),
        ("allowed_hosts", (), HOST_RULE),
        ("allowed_hosts", ("127.0.0.1:8000", ""), HOST_RULE),
        ("allowed_hosts", ("local host",), HOST_RULE),
        ("allowed_origins", ("http://127.0.0.1:5173/",), origin_rule("http://127.0.0.1:5173/")),
        ("allowed_origins", ("ftp://127.0.0.1",), origin_rule("ftp://127.0.0.1")),
        ("allowed_origins", ("http://",), origin_rule("http://")),
        ("allowed_origins", ("127.0.0.1:5173",), origin_rule("127.0.0.1:5173")),
        (
            "allowed_origins",
            ("http://user@127.0.0.1:5173",),
            "The allowed origin “http://user@127.0.0.1:5173” must not contain credentials.",
        ),
        ("max_body_bytes", 0, BOUND_RULE),
        ("max_body_bytes", True, BOUND_RULE),
    ],
)
def test_invalid_settings_are_refused(field: str, value: object, message: str) -> None:
    with pytest.raises(ValueError) as raised:
        replace(http_settings(), **{field: value})
    assert str(raised.value) == message


def test_settings_never_show_the_token() -> None:
    settings = replace(http_settings(), allowed_origins=(), allowed_hosts=("[::1]:8000",))
    assert TOKEN not in repr(settings)
    assert settings.allowed_origins == ()


async def test_the_supplied_lifespan_wraps_the_application() -> None:
    events: list[str] = []

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        events.append("started")
        yield
        events.append("stopped")

    app = create_http_app(services(Platform()), http_settings(), lifespan)
    async with app.router.lifespan_context(app):
        assert events == ["started"]
    assert events == ["started", "stopped"]


async def test_the_compiled_interface_is_served_at_the_root(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<!doctype html><title>Slow Thinker II</title>")
    (tmp_path / "assets" / "app.js").write_text("export {};")
    async with operator_api(settings=http_settings(static=tmp_path)) as api:
        anonymous = {"authorization": ""}
        page = await api.http.get("/", headers=anonymous)
        assert page.status_code == 200 and "<title>Slow Thinker II</title>" in page.text
        assert (await api.http.get("/assets/app.js", headers=anonymous)).status_code == 200
        assert (await api.http.get("/missing.js", headers=anonymous)).status_code == 404
        guarded = await api.http.get("/api/v2/nothing", headers=anonymous)
        assert error(guarded) == (401, "operator_authentication_required")
        assert error(await api.http.get("/api/v2/nothing")) == (404, "not_found")
        assert error(await api.http.post("/api/v2/nothing")) == (404, "not_found")
        assert (await api.http.get("/api/v2/usage")).status_code == 200


def test_a_missing_interface_directory_is_refused(tmp_path: Path) -> None:
    settings = http_settings(static=tmp_path / "dist")
    with pytest.raises(ValueError) as raised:
        create_http_app(services(Platform()), settings)
    assert str(raised.value) == f"The interface directory “{tmp_path / 'dist'}” does not exist."
