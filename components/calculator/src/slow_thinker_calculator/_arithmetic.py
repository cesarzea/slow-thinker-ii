"""Evaluate only reviewed AST arithmetic with exact, bounded Decimal operations."""

import ast
import re
from decimal import Decimal

from ._config import Settings

_LITERAL = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")


def bounded(value: Decimal, limits: Settings) -> Decimal:
    if not value.is_finite() or abs(value.adjusted()) > limits.max_result_bytes:
        raise ValueError("Calculator result exceeds its bound")
    if len(format(value, "f").encode("utf-8")) > limits.max_result_bytes:
        raise ValueError("Calculator result exceeds its bound")
    return value


def literal(node: ast.Constant, source: str, limits: Settings) -> Decimal:
    text = ast.get_source_segment(source, node)
    if type(node.value) not in (int, float) or text is None or not _LITERAL.fullmatch(text):
        raise ValueError("Only decimal numeric literals are supported")
    value = Decimal(text)
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int) or abs(exponent) > limits.max_exponent:
        raise ValueError("Numeric literal exponent exceeds its bound")
    return bounded(value, limits)


def power(left: Decimal, right: Decimal, limits: Settings) -> Decimal:
    if right != right.to_integral_value() or abs(right) > limits.max_exponent:
        raise ValueError("Power requires a bounded integer exponent")
    return left ** int(right)


def binary(operator: ast.operator, left: Decimal, right: Decimal, limits: Settings) -> Decimal:
    match operator:
        case ast.Add():
            return left + right
        case ast.Sub():
            return left - right
        case ast.Mult():
            return left * right
        case ast.Div():
            return left / right
        case ast.FloorDiv():
            return left // right
        case ast.Mod():
            return left % right
        case ast.Pow():
            return power(left, right, limits)
        case _:
            raise ValueError("Unsupported calculator operator")


def evaluate(node: ast.AST, source: str, limits: Settings) -> Decimal:
    match node:
        case ast.Constant():
            return literal(node, source, limits)
        case ast.UnaryOp(op=ast.UAdd(), operand=positive_operand):
            return evaluate(positive_operand, source, limits)
        case ast.UnaryOp(op=ast.USub(), operand=negative_operand):
            return bounded(-evaluate(negative_operand, source, limits), limits)
        case ast.BinOp(left=left, op=operator, right=right):
            return bounded(
                binary(
                    operator,
                    evaluate(left, source, limits),
                    evaluate(right, source, limits),
                    limits,
                ),
                limits,
            )
        case _:
            raise ValueError("Unsupported calculator expression")
