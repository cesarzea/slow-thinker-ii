"""Resolve a native model alias only in its authenticated caller's frozen resource bindings."""

from slow_thinker_ii.access import AccessDenied, CallAuthority
from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from ._gateway_records import RejectionRecorder
from ._native_records import GatewayError, InvocationRouter, ModelBinding, NativeReply
from ._native_reply import native_reply


class NativeModelGateway:
    def __init__(
        self,
        authority: CallAuthority,
        calls: InvocationRouter,
        bindings: tuple[ModelBinding, ...],
        recorder: RejectionRecorder | None = None,
    ) -> None:
        self._authority, self._calls = authority, calls
        self._recorder = recorder
        self._bindings = {(item.caller, item.model_alias): item.target for item in bindings}
        if len(self._bindings) != len(bindings) or any(
            not item.caller or not item.model_alias for item in bindings
        ):
            raise ValueError("Model bindings need unique nonempty caller/alias pairs")

    def deadline(self, grant: str) -> float:
        return self._authority.context(grant).deadline

    async def complete(self, grant: str, request_json: str) -> NativeReply:
        context = self._authority.context(grant)
        request = json_object(decode_json(request_json))
        model = request.get("model")
        if not isinstance(model, str):
            self._reject(grant, "model", "model_alias_required")
            raise GatewayError("model_alias_required", 400)
        target = self._bindings.get((context.target.instance, model))
        if target is None:
            self._reject(grant, model, "model_binding_denied")
            raise AccessDenied("model_binding_denied")
        aliases = self._authority.discover(grant)
        alias = next((item.alias for item in aliases if item.address == target), None)
        if alias is None:
            self._reject(grant, model, "model_operation_denied")
            raise AccessDenied("model_operation_denied")
        try:
            result = await self._calls.invoke(grant, alias, encode_json({"request": request}))
        except AccessDenied as error:
            self._reject(grant, model, error.code)
            raise
        try:
            return native_reply(result)
        except GatewayError:
            raise
        except ValueError as error:
            raise GatewayError("invalid_model_response") from error

    def _reject(self, grant: str, operation: str, reason: str) -> None:
        if self._recorder is not None:
            self._recorder.reject(grant, operation, reason)
