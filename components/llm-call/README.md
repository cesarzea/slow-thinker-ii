# LLM Call

A graph node that sends its prompt as the system message and the received message as
the user message to the LLM selected in its configuration, once per activation, and
emits the reply on `out`: as text, or as JSON validated against a schema. Invalid
replies fail the activation; nothing is retried or repaired.

The model call goes through the platform's Chat Completions endpoint with the
activation's grant; the component holds no provider credentials. Its configuration
dialog is defined by the packaged [declaration](src/slow_thinker_llm_call/component.json).

Run as `python -m slow_thinker_llm_call <bootstrap>`. Subclasses of `LLMCall` can
override `build_messages`, `parse_response` and `validate_result`.

Tests: `uv run --locked pytest components/llm-call/tests`. See
[specification.md](specification.md) for the behaviour and failure codes.
