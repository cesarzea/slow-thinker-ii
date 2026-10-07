"""What the gateway learns about one model call, recorded as its `llm.called` event."""

from dataclasses import dataclass, field
from decimal import Context, Decimal
from fractions import Fraction
from types import MappingProxyType

from slow_thinker_ii.accounting import Rates, Scope, Usage, format_usd
from slow_thinker_ii.contracts import JsonObject, JsonValue

_ERROR_TYPES = MappingProxyType(
    {
        400: "invalid_request_error",
        401: "authentication_error",
        402: "budget_error",
        403: "permission_error",
        502: "provider_error",
        504: "timeout_error",
    }
)


@dataclass
class CallRecord:
    call_id: str
    started: float  # monotonic seconds
    request: JsonValue = None  # the dispatched request, or what was received
    llm: str | None = None
    provider_model: str | None = None
    reserved: int = 0  # quanta
    cost: int = 0
    estimated: bool = False
    usage: Usage | None = None
    rates: Rates | None = None
    scopes: tuple[Scope, ...] = field(default=())

    def data(self, status: int, body: JsonObject, duration_ms: int) -> JsonObject:
        """The `llm.called` data: `response` for status 200, otherwise `error`."""
        outcome = "response" if status == 200 else "error"
        return {
            "call_id": self.call_id,
            "llm": self.llm,
            "provider_model": self.provider_model,
            "request": self.request,
            outcome: body if status == 200 else body.get("error"),
            "usage": None if self.usage is None else usage_document(self.usage),
            "reserved_usd": format_usd(self.reserved),
            "cost_usd": format_usd(self.cost),
            "estimated": self.estimated,
            "rates": None if self.rates is None else rates_document(self.rates),
            "status": status,
            "duration_ms": duration_ms,
        }


def error_body(status: int, code: str, message: str) -> JsonObject:
    """`{"error": {"code", "message", "type"}}`, with an OpenAI-style type for the status."""
    kind = _ERROR_TYPES.get(status, "api_error")
    return {"error": {"code": code, "message": message, "type": kind}}


def usage_document(usage: Usage) -> JsonObject:
    return {
        "input": usage.input,
        "cached_input": usage.cached_input,
        "cache_write": usage.cache_write,
        "output": usage.output,
    }


def rates_document(rates: Rates) -> JsonObject:
    """Applied rates as exact decimal strings in USD per million tokens; unbilled ones omitted."""
    pairs = (
        ("input", rates.input),
        ("cached_input", rates.cached_input),
        ("cache_write", rates.cache_write),
        ("output", rates.output),
    )
    return {name: per_million(rate) for name, rate in pairs if rate is not None}


def per_million(rate: Fraction) -> str:
    """The exact decimal of a reviewed rate, which has at most 27 significant digits."""
    scaled = rate * 1_000_000
    exact = Context(prec=60)
    value = exact.divide(Decimal(scaled.numerator), Decimal(scaled.denominator))
    return format(value.normalize(exact), "f")
