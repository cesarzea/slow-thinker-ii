# Glossary

| Term | Meaning |
| --- | --- |
| Component type | A versioned implementation and declared contract, independently supplied. |
| Component instance | A configured use of a type, with its own identity and resource bindings. It is not necessarily a process. |
| Implementation object | An object created by a component host to execute code. Its lifetime can differ from the configured instance, process and persisted resource data. |
| Role | A declared capability category such as agent, resource, control, or collaboration. A type may serve more than one role. |
| Process | A deployment unit that can host one or more instances if its contract permits it. |
| Node | An addressable element in an experiment graph that binds a component operation. |
| Activation | One scheduled graph-node execution. Repeating a node creates another activation. Nested operations have their own call identities and retain the originating activation; they are not extra scheduled graph steps. |
| Call / attempt | One managed invocation. A retry has a distinct attempt identity linked to the logical operation. |
| Graph definition | Versioned domain configuration of an experiment. It is independent of screen layout. |
| Runtime graph revision | The structure effective at an execution point after an authorized mutation. Dynamic mutation is later functionality. |
| Result graph | Graph-shaped content produced or revised by agents; distinct from orchestration structure. |
| Variant | A graph definition derived from another as an experiment candidate. Its lineage does not itself demonstrate improvement. |
| Run | One execution using a frozen definition, input and effective configuration. |
| Work session | A saved grouping of runs used for inspection and aggregate budgets. It does not imply shared agent memory. |
| Agent conversation | Explicitly scoped conversational state, if a component supports it. It is not an MCP connection. |
| Resource binding | An explicit association between a component's resource slot and a configured resource identity. |
| Reservation | Spending capacity committed before a billable attempt; distinct from a final charge. |
| Evidence | Recorded material identified as platform-observed, component-reported, or analyst-inferred. |
| Thinking | Reasoning information a component or provider exposes; availability and completeness are not guaranteed. |
| Evaluation | Assessment of behavior or outcomes according to a versioned policy and selected objectives. |
| Influence | An analytical attribution supported by evidence, potentially involving multiple sources and uncertainty. |
| MCP profile | The exact protocol revision, transports, features, extensions and compatibility behavior supported by an implementation. |

For protocol statelessness and explicitly identified application state, see the [MCP profile](../contracts/mcp-profile.md).
