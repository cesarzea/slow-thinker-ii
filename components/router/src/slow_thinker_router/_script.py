"""Load the configured script's `route` function and describe what its code raised."""

import builtins
import inspect
import traceback
from collections.abc import Callable
from typing import cast

from slow_thinker_host import JsonValue

SCRIPT_FILE = "<script>"

type Route = Callable[[JsonValue, JsonValue], object]


class ScriptError(ValueError):
    """The script cannot provide `route`; the message is English and names the line."""


def load_route(script: str) -> Route:
    """Run the script in a fresh namespace with the normal built-ins and return `route`."""
    try:
        code = compile(script, SCRIPT_FILE, "exec")
    except SyntaxError as error:
        message = f"The script has a syntax error at line {error.lineno}: {error.msg}"
        raise ScriptError(message) from error
    namespace: dict[str, object] = {"__builtins__": builtins, "__name__": "router_script"}
    try:
        exec(code, namespace)
    except Exception as error:
        raise ScriptError(f"The script raised {raised(error)} while loading") from error
    return _route(namespace.get("route"))


def raised(error: BaseException) -> str:
    """The exception's type and message, and the script line where it was raised."""
    lines = [
        frame.lineno
        for frame in traceback.extract_tb(error.__traceback__)
        if frame.filename == SCRIPT_FILE
    ]
    text = f"{type(error).__name__}: {error}" if str(error) else type(error).__name__
    return f"{text} at line {lines[-1]}" if lines else text


def _route(value: object) -> Route:
    if not callable(value):
        raise ScriptError("The script does not define a function named route")
    function = cast(Route, value)
    asynchronous = (inspect.iscoroutinefunction, inspect.isasyncgenfunction)
    if any(
        check(candidate)
        for check in asynchronous
        for candidate in (function, type(function).__call__)
    ):
        raise ScriptError("The script's route function must be a regular, synchronous function")
    try:
        inspect.signature(function).bind(None, None)
    except (TypeError, ValueError) as error:
        raise ScriptError(
            "The script's route function must take two positional parameters: "
            "received and node_input"
        ) from error
    return function
