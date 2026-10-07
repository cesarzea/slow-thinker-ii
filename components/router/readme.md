# Router

A component that runs the user's Python script to choose an output. The script defines
`route(received, node_input)` and returns an output name declared in the configuration
and the content to send through it. Embedded at a node's output, it replaces the
node's output ports with the configured names; as a node, it routes the message it
receives.

The script is loaded once when the host starts, so syntax errors stop the run before
it begins; each call runs in a worker thread. Its configuration dialog is defined by
the packaged [declaration](src/slow_thinker_router/component.json).

Run as `python -m slow_thinker_router <bootstrap>`. Tests:
`uv run --locked pytest components/router/tests`. See
[specification.md](specification.md) for the behaviour and failure codes.
