"""Values exchanged with the LLM ports and the settings of the use cases."""

from dataclasses import dataclass
from datetime import datetime

from slow_thinker_ii.accounting import Tariff, Usage
from slow_thinker_ii.catalog import LlmModelSettings
from slow_thinker_ii.contracts import JsonObject


@dataclass(frozen=True)
class LlmModel:
    """A configured model: its catalog settings and its reviewed tariff."""

    settings: LlmModelSettings
    tariff: Tariff


@dataclass(frozen=True)
class ProviderReply:
    status: int  # 200 success, 502 provider_error, 504 provider_timeout
    body: JsonObject  # Chat Completions response or {"error": {...}}, redacted
    usage: Usage | None  # normalized; None when unknown
    started_at: datetime  # aware UTC
    ended_at: datetime


@dataclass(frozen=True)
class GatewayReply:
    """What `/v1/chat/completions` answers: the status and the JSON body, unchanged."""

    status: int
    body: JsonObject


@dataclass(frozen=True)
class BudgetLimits:
    """The day and month budgets of the server configuration, in quanta of 10⁻⁹ USD."""

    daily_nanos: int
    monthly_nanos: int


@dataclass(frozen=True)
class RunSettings:
    max_active_runs: int = 4
    max_activation_seconds: int = 300
