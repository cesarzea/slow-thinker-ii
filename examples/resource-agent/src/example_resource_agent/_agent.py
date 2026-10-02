"""An authored agent consumes explicit context through the public LLMCall API."""

from slow_thinker_llm_call import JsonObject, LLMCall, Message


class ResourceAgent(LLMCall):
    def build_messages(self, arguments: JsonObject) -> list[Message]:
        messages = super().build_messages(arguments)
        guidance = Message(
            "system",
            "Use any explicitly supplied memory or calculation context as evidence. "
            "Do not invent remembered facts or claim tool calls that were not supplied.",
        )
        return [messages[0], guidance, *messages[1:]]
