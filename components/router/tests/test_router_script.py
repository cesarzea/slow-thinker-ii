"""The script is compiled once at startup; unusable scripts stop the host with the line."""

import pytest
from slow_thinker_router import ScriptError, load_route

ROUTE = "def route(received, node_input):\n    return 'yes', received\n"


def test_route_is_taken_from_a_fresh_namespace_with_the_normal_builtins() -> None:
    script = "SEEN = len([1, 2])\n\ndef route(received, node_input):\n    return 'yes', SEEN\n"
    assert load_route(script)("story", None) == ("yes", 2)
    assert load_route(ROUTE)("story", None) == ("yes", "story")


@pytest.mark.parametrize(
    "script",
    [
        "route = lambda received, node_input: ('yes', received)\n",
        "def route(*values):\n    return 'yes', values[0]\n",
        "def route(received, node_input, extra=None):\n    return 'yes', received\n",
        "class Choice:\n    def __call__(self, a, b):\n        return 'yes', a\n\nroute = Choice()",
    ],
)
def test_any_callable_accepting_two_positional_values_is_a_route(script: str) -> None:
    assert load_route(script)(1, 2) == ("yes", 1)


@pytest.mark.parametrize(
    ("script", "message"),
    [
        (
            "def route(received, node_input):\n    return 'yes' received\n",
            "The script has a syntax error at line 2: invalid syntax",
        ),
        ("def choose(received, node_input):\n    pass\n", "does not define a function named route"),
        ("route = 3\n", "does not define a function named route"),
        ("def route(received):\n    pass\n", "must take two positional parameters"),
        ("def route(a, b, c):\n    pass\n", "must take two positional parameters"),
        ("async def route(a, b):\n    pass\n", "must be a regular, synchronous function"),
        ("async def route(a, b):\n    yield 1\n", "must be a regular, synchronous function"),
        (
            "class Choice:\n    async def __call__(self, a, b):\n        pass\n\nroute = Choice()",
            "must be a regular, synchronous function",
        ),
        (
            "LIMIT = 10\nTHRESHOLD = LIMIT / 0\n",
            "The script raised ZeroDivisionError: division by zero at line 2 while loading",
        ),
        ("import missing_module_for_router_tests\n", "ModuleNotFoundError"),
    ],
)
def test_unusable_scripts_fail_with_an_english_message(script: str, message: str) -> None:
    with pytest.raises(ScriptError) as caught:
        load_route(script)
    assert message in str(caught.value)
