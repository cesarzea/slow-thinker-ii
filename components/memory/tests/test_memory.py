"""The Memory adds the node's latest exchanges to each message and keeps each new one."""

from memory_fakes import FakeContext
from slow_thinker_memory import Exchange, Memory, with_history


async def test_the_first_message_passes_unchanged() -> None:
    memory = Memory(2)
    assert await memory.recall("Interview the cat.", FakeContext()) == "Interview the cat."


async def test_recall_adds_the_latest_exchanges_as_a_transcript() -> None:
    memory, context = Memory(2), FakeContext()
    await memory.remember("Interview the cat.", "Why did you fall?", context)
    await memory.remember({"answer": "The wind."}, "Which wind?", context)
    await memory.remember("A draught.", "Thank you.", context)
    recalled = await memory.recall("Bye.", context)
    assert recalled == "\n".join(
        [
            "Conversation so far:",
            'You received: {"answer":"The wind."}',
            "You replied: Which wind?",
            "You received: A draught.",
            "You replied: Thank you.",
            "",
            "New message:",
            "Bye.",
        ]
    )


def test_a_structured_message_becomes_json_text() -> None:
    history = [Exchange("Hi", {"score": 8})]
    assert with_history(history, {"question": 2}) == "\n".join(
        [
            "Conversation so far:",
            "You received: Hi",
            'You replied: {"score":8}',
            "",
            "New message:",
            '{"question":2}',
        ]
    )
    assert with_history([], {"question": 2}) == {"question": 2}
