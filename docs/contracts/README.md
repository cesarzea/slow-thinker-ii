# Contracts

These contracts define the boundaries of the new core. Each has an identifier and a
version. A change that alters the meaning or validity of existing data or messages
creates a new version; existing saved graphs and recorded runs keep the version they
were written with. JSON Schemas use draft 2020-12 and reject unknown fields.

| Contract                                         | Defines                                                              |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| [Graph document](graph-document.md)              | What a user builds and saves; validation and diagnostics            |
| [Component declaration](component-declaration.md) | Placement, ports, state, service uses, configuration and its screens |
| [Execution](execution.md)                        | Runs, messages, activations, limits and termination                  |
| [Component protocol](component-protocol.md)      | How the platform launches and calls component hosts                  |
| [LLM service](llm-service.md)                    | Model catalog, parameter schemas, calls and provider adapters        |
| [Accounting](accounting.md)                      | Money, budgets, tariffs, reservations and settlement                 |
| [Recording](recording.md)                        | The event log of every run                                           |
| [Operator API](operator-api.md)                  | The HTTP interface used by the browser                               |

[Examples](examples/) contain the three validated journey graphs, the four step 1
component declarations and an LLM catalog. They are checked against the schemas in
[schemas](schemas/) by the test suite.

The contracts of the previous implementation are
[archived](../archive/previous-implementation/contracts/README.md).
