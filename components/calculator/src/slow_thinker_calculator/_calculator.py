"""Independent deterministic arithmetic; no host or external service is required."""

import ast
from decimal import DecimalException, Inexact, localcontext

from slow_thinker_host import JsonObject

from ._arithmetic import evaluate
from ._config import settings


class Calculator:
    def __init__(
        self,
        *,
        max_expression_bytes: int = 4096,
        max_nodes: int = 128,
        max_exponent: int = 100,
        max_result_bytes: int = 4096,
    ) -> None:
        self._limits = settings(
            {
                "max_expression_bytes": max_expression_bytes,
                "max_nodes": max_nodes,
                "max_exponent": max_exponent,
                "max_result_bytes": max_result_bytes,
            }
        )

    def calculate(self, expression: str) -> JsonObject:
        if type(expression) is not str or not expression.strip():
            raise ValueError("Calculator expression must be nonempty")
        if len(expression.encode("utf-8")) > self._limits.max_expression_bytes:
            raise ValueError("Calculator expression exceeds its bound")
        try:
            tree = ast.parse(expression.strip(), mode="eval")
            if sum(1 for _ in ast.walk(tree)) > self._limits.max_nodes:
                raise ValueError("Calculator expression tree exceeds its bound")
            with localcontext(prec=self._limits.max_result_bytes) as context:
                context.traps[Inexact] = True
                result = evaluate(tree.body, expression.strip(), self._limits)
        except (SyntaxError, DecimalException, RecursionError) as error:
            raise ValueError("Invalid or inexact calculator arithmetic") from error
        text = format(result, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return {"expression": expression, "value": "0" if result == 0 else text}
