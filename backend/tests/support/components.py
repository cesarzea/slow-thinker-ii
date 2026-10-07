"""Hosts that behave like the step 1 components: LLM Call calls the gateway, Router routes."""

from collections.abc import Callable

from slow_thinker_ii.application import LlmGateway
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object
from slow_thinker_ii.engine import CallContext, CallFailure, Emission
from slow_thinker_ii.graphs import RunPlan

from .hosts import Gate


class ComponentHosts:
    """`engine.Hosts` for one plan, as `adapters.hosts` would serve the real components.

    LLM Call sends its prompt as the system message and the received message as the user
    message through the gateway with the call's grant, and emits the reply on `out` (parsed
    for JSON output). An embedded Router picks the node's first output when the received
    `score` is at least 7, else the second, and sends the node input, like the journeys'
    scripts. `contexts` keeps every call; `gate`, when given, holds `activate` calls.
    """

    def __init__(
        self, plan: RunPlan, gateway: Callable[[], LlmGateway], gate: Gate | None = None
    ) -> None:
        self.contexts: list[CallContext] = []
        self.gate = gate
        self._plan = plan
        self._gateway = gateway

    async def activate(
        self, context: CallContext, message: JsonValue
    ) -> tuple[Emission, ...] | CallFailure:
        self.contexts.append(context)
        if self.gate is not None:
            await self.gate.wait()
        config = self._plan.node(context.node_id).host.config
        reply = await self._gateway().complete(
            context.grant, encode_json(chat_body(config, message))
        )
        if reply.status != 200:
            error = json_object(reply.body["error"])
            return CallFailure("model_call_failed", f"The model call failed: {error['code']}.")
        content = str(_choice(reply.body)["content"])
        output = json_object(config["output_format"])
        return (Emission("out", decode_json(content) if output["type"] == "json" else content),)

    async def select_output(
        self, context: CallContext, received: JsonValue, node_input: JsonValue
    ) -> Emission | CallFailure:
        self.contexts.append(context)
        high, low = self._plan.node(context.node_id).outputs
        score = received.get("score") if isinstance(received, dict) else None
        return Emission(high if isinstance(score, int) and score >= 7 else low, node_input)

    async def recall(self, context: CallContext, message: JsonValue) -> JsonValue | CallFailure:
        """No memory is served here: the message passes unchanged."""
        self.contexts.append(context)
        return message

    async def remember(
        self, context: CallContext, received: JsonValue, replied: JsonValue
    ) -> None | CallFailure:
        self.contexts.append(context)
        return None


def chat_body(config: JsonObject, message: JsonValue) -> JsonObject:
    """The Chat Completions request of an LLM Call configuration for one received message."""
    selection = json_object(config["model"])
    user = message if isinstance(message, str) else encode_json(message)
    body: JsonObject = {
        "model": selection["llm"],
        "messages": [
            {"role": "system", "content": config["prompt"]},
            {"role": "user", "content": user},
        ],
        **json_object(selection["parameters"]),
    }
    output = json_object(config["output_format"])
    if output["type"] == "json":
        schema = {"name": "output", "schema": output["schema"], "strict": True}
        body["response_format"] = {"type": "json_schema", "json_schema": schema}
    return body


def _choice(body: JsonObject) -> JsonObject:
    choices = body["choices"]
    assert isinstance(choices, list)
    return json_object(json_object(choices[0])["message"])
