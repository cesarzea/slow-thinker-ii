"""Models, tariffs and budgets of the step 1 server configuration example."""

from slow_thinker_ii.accounting import parse_tariff, parse_usd
from slow_thinker_ii.application import BudgetLimits, LlmModel
from slow_thinker_ii.contracts import json_object

from .examples import configured_models, model_settings, server_configuration


def llm_models() -> tuple[LlmModel, ...]:
    """Each configured model with its catalog settings and its tariff."""
    return tuple(
        LlmModel(model_settings(model), parse_tariff(model["tariff"]))
        for model in configured_models()
    )


def budget_limits() -> BudgetLimits:
    budgets = json_object(server_configuration()["budgets"])
    daily, monthly = budgets["daily_usd"], budgets["monthly_usd"]
    assert isinstance(daily, str) and isinstance(monthly, str)
    return BudgetLimits(parse_usd(daily), parse_usd(monthly))
