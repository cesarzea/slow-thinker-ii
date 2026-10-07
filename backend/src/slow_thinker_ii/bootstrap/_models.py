"""Configured models: catalog settings and reviewed tariffs, checked against the providers."""

from collections.abc import Collection, Mapping
from types import MappingProxyType

from slow_thinker_ii.accounting import parse_tariff
from slow_thinker_ii.application import LlmModel
from slow_thinker_ii.catalog import LlmModelSettings

from ._document import ModelDocument, invalid

SIMULATED = "simulated"


def configured_models(
    documents: tuple[ModelDocument, ...], providers: Collection[str]
) -> tuple[LlmModel, ...]:
    """Each model with a configured provider, a unique id, a valid entry and a valid tariff."""
    models: list[LlmModel] = []
    for index, document in enumerate(documents):
        where = f"/llm/models/{index}"
        if any(model.settings.id == document.id for model in models):
            raise invalid(f"{where}/id", f"“{document.id}” is configured more than once")
        if document.provider not in providers:
            raise invalid(
                f"{where}/provider", f"“{document.provider}” is not a configured provider"
            )
        if document.replies is not None and document.provider != SIMULATED:
            raise invalid(f"{where}/replies", "only models of the simulated provider have replies")
        models.append(_model(document, where))
    return tuple(models)


def scripted_replies(documents: tuple[ModelDocument, ...]) -> Mapping[str, tuple[str, ...]]:
    """The replies the simulated provider gives, by model id."""
    return MappingProxyType(
        {document.id: document.replies for document in documents if document.replies is not None}
    )


def _model(document: ModelDocument, where: str) -> LlmModel:
    settings = LlmModelSettings(
        document.id,
        document.label,
        document.provider,
        document.model,
        document.max_output_tokens,
        document.default_output_tokens,
        document.reasoning_efforts,
        document.temperature,
    )
    if document.default_output_tokens > document.max_output_tokens:
        raise invalid(f"{where}/default_output_tokens", "must not exceed max_output_tokens")
    try:
        tariff = parse_tariff(document.tariff)
    except ValueError as error:
        raise invalid(f"{where}/tariff", str(error).rstrip(".")) from None
    return LlmModel(settings, tariff)
