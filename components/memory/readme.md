# Memory

A component embedded as a node's memory. Before each activation the platform calls its
`recall` with the received message, and the node receives what it returns: the message
with the node's latest exchanges as a transcript. After the activation the platform calls
`remember` with the received message and the node's reply. The exchanges live in this
host's process, so the memory lasts for the run. Its configuration dialog is defined by
the packaged [declaration](src/slow_thinker_memory/component.json).

Run as `python -m slow_thinker_memory <bootstrap>`. Tests:
`uv run --locked pytest components/memory/tests`. See
[specification.md](specification.md) for the behaviour and failure codes.
