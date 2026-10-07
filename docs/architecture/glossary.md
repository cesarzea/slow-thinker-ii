# Glossary

| Term                   | Meaning                                                                                       |
| ---------------------- | --------------------------------------------------------------------------------------------- |
| Activation             | One execution of a node for one delivered message                                             |
| Component              | A packaged or platform implementation with a declaration, identified by `type@version`        |
| Component declaration  | The package's description of placements, ports, state, uses, configuration and screens        |
| Connection             | A link from an output port to an input port; the only path a message can take                 |
| Delivery               | One message on its way to one input port, waiting in the run's queue or being processed       |
| Embedded component     | A component placed inside a node at a position, such as a Router at the node's output         |
| Event log              | The append-only record of a run                                                               |
| Grant                  | A short-lived credential identifying one activation's call, used for calls back to the platform |
| Graph                  | A document of nodes, connections, limits and layout, saved as immutable versions              |
| Host                   | The process running one packaged component for one node or embedded component during a run    |
| LLM catalog            | The models the platform offers, each with its parameter schema                                |
| Message                | A JSON value emitted on a port and delivered through connections                              |
| Node                   | An instance of a component in a graph, with its own configuration                             |
| Observed evidence      | What the platform recorded while mediating                                                    |
| Port                   | A named input or output of a node                                                             |
| Reported evidence      | What a component chose to report about its internal work                                      |
| Run                    | One execution of one graph version with one input                                             |
| Service                | A capability provided by the platform, such as the LLM service                                |
