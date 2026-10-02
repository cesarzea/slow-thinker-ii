"""Arithmetic remains exact, bounded and free of executable expression forms."""

import pytest
from slow_thinker_calculator import Calculator, CalculatorHost
from slow_thinker_host import Invocation, JsonObject, Operation, json_object


@pytest.mark.parametrize(
    "expression,value",
    [
        ("6 * 12 + 3 * 8", "96"),
        ("0.1+0.2", "0.3"),
        ("-(2+3)/2", "-2.5"),
        ("+3 - 1", "2"),
        ("7//2", "3"),
        ("7%2", "1"),
        ("2**-3", "0.125"),
        ("1e2", "100"),
        (".5*2", "1"),
        ("-0.00", "0"),
        (" 2+2 ", "4"),
        ("9007199254740993+1", "9007199254740994"),
    ],
)
def test_exact_decimal_arithmetic(expression: str, value: str) -> None:
    assert Calculator().calculate(expression) == {"expression": expression, "value": value}


@pytest.mark.parametrize(
    "expression",
    [
        "",
        " ",
        "name",
        "f()",
        "(1).real",
        "[1][0]",
        "True",
        "'1'",
        "1;2",
        "lambda: 1",
        "2<<1",
        "0x10",
        "1_000",
        "1/0",
        "1/3",
        "2**101",
        "2**.5",
        "1e101",
        "1e-101",
        "(" * 300 + "1" + ")" * 300,
    ],
)
def test_invalid_or_excessive_arithmetic_is_rejected(expression: str) -> None:
    with pytest.raises(ValueError):
        Calculator().calculate(expression)


@pytest.mark.parametrize(
    "config,expression",
    [
        ({"max_expression_bytes": 1}, "12"),
        ({"max_nodes": 2}, "1+1"),
        ({"max_result_bytes": 2}, "99+1"),
        ({"max_result_bytes": 2}, ".001"),
        ({"max_exponent": 1}, "2**2"),
        ({"max_result_bytes": 1}, "9*9"),
    ],
)
def test_configured_bounds_apply(config: dict[str, int], expression: str) -> None:
    with pytest.raises(ValueError):
        Calculator(**config).calculate(expression)


@pytest.mark.parametrize(
    "config", [{"max_nodes": True}, {"max_exponent": -1}, {"max_result_bytes": 4097}, {"extra": 1}]
)
def test_description_rejects_invalid_configuration(config: JsonObject) -> None:
    with pytest.raises(ValueError):
        CalculatorHost.describe(config)


async def test_host_validates_schema_and_returns_standard_errors() -> None:
    operations = CalculatorHost.describe({})
    host = CalculatorHost({}, operations)
    assert host.operations() == operations
    assert (await host.invoke("calculate", {"expression": "1+1"}, Invocation("g"))).value[
        "value"
    ] == "2"
    from mcp.shared.exceptions import MCPError

    for name, arguments in [
        ("other", {}),
        ("calculate", {"expression": False}),
        ("calculate", {"expression": "1/0"}),
    ]:
        with pytest.raises(MCPError) as caught:
            await host.invoke(name, json_object(arguments), Invocation("g"))
        assert caught.value.message == "calculator_failed"
    with pytest.raises(ValueError, match="schemas do not match"):
        CalculatorHost({}, (Operation("calculate", {}, {}),))
