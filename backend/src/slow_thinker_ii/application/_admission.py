"""Admission of a model call: request shape, the caller's selected entry and its parameters."""

from collections.abc import Iterable
from dataclasses import dataclass

from slow_thinker_ii.accounting import input_bound, reservation_bound
from slow_thinker_ii.catalog import LlmEntry, llm_entry
from slow_thinker_ii.contracts import JsonObject

from ._active import ActiveCall
from ._call_record import CallRecord, error_body
from ._requests import ChatRequest, parse_request
from ._values import GatewayReply, LlmModel


@dataclass(frozen=True)
class Admitted:
    model: LlmModel
    request: JsonObject  # dispatched: validated, with schema defaults
    bound: int  # reservation in quanta


class CallAdmission:
    def __init__(self, models: Iterable[LlmModel]) -> None:
        self._models = {model.settings.id: model for model in models}
        self._entries = {key: llm_entry(item.settings) for key, item in self._models.items()}
        names = (_property_names(entry) for entry in self._entries.values())
        self._names = frozenset(name for found in names for name in found)

    def admit(self, call: ActiveCall, body: str, record: CallRecord) -> Admitted | GatewayReply:
        """Checks in order: request shape and fields (400), selected entry (403), parameters."""
        request = parse_request(body, self._names)
        if isinstance(request, str):
            record.request = body
            return rejected(400, "invalid_request", request)
        record.request, record.llm = request.document, request.model
        model = self._models.get(request.model)
        if model is None or request.model not in call.component.llm_entries:
            message = (
                f"The model “{request.model}” is not selected in this component's configuration."
            )
            return rejected(403, "model_not_allowed", message)
        entry = self._entries[request.model]
        parameters = entry.with_defaults(request.parameters)
        problems = entry.parameter_problems(parameters)
        if problems:
            return rejected(400, "invalid_request", f"Invalid parameters: {' '.join(problems)}")
        record.provider_model = model.settings.model
        record.request = request.dispatched(parameters)
        return Admitted(model, record.request, _bound(model, request, parameters))


def rejected(status: int, code: str, message: str) -> GatewayReply:
    return GatewayReply(status, error_body(status, code, message))


def _property_names(entry: LlmEntry) -> frozenset[str]:
    """Parameter names of an entry's schema; together they are the accepted parameter fields."""
    properties = entry.parameters.get("properties")
    return frozenset(properties) if isinstance(properties, dict) else frozenset()


def _bound(model: LlmModel, request: ChatRequest, parameters: JsonObject) -> int:
    """Input bound × highest input rate plus `max_completion_tokens` × highest output rate."""
    output = parameters.get("max_completion_tokens")
    tokens = input_bound(request.input_bytes(), len(request.messages))
    return reservation_bound(model.tariff, tokens, output if isinstance(output, int) else 0)
