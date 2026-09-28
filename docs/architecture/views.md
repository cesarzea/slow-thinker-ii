# C4 views

**Status: Draft.** These diagrams use [C4 abstractions](https://c4model.com/diagrams) rendered with Mermaid. Each view identifies people, software systems or containers, responsibilities, and relationships. A C4 container is a runnable application or data store, not necessarily a Docker container.

## System context

```mermaid
flowchart LR
  operator["Experiment designer / analyst<br/>Person"]
  author["Component author<br/>Person"]
  platform["Slow Thinker II<br/>Software system<br/>Define, execute, inspect and evaluate collaboration"]
  providers["Model and resource providers<br/>External software systems"]
  clients["Agent tooling<br/>External software systems<br/>MCP / OpenAI-compatible clients"]
  operator -->|"Defines experiments and inspects outcomes"| platform
  author -->|"Supplies component packages and contracts"| platform
  clients -->|"Invokes authorized platform capabilities"| platform
  platform -->|"Sends authorized requests; receives results and usage"| providers
```

Provider APIs are external boundaries. The original Slow Thinker remains independent, with no runtime or accounting integration. Budgets cover only managed Slow Thinker II calls (Q12). The diagram does not assert that external clients support every platform capability.

## Containers: initial local deployment

```mermaid
flowchart TB
  person["Operator<br/>Person"]
  ext["Provider APIs<br/>External software systems"]
  subgraph system["Slow Thinker II — local deployment boundary"]
    web["Browser UI<br/>React / TypeScript / React Flow<br/>Graph views and inspection"]
    api["Application and runtime<br/>Python / FastAPI<br/>Routing, execution, limits, accounting and observation"]
    worker["Independent local component processes<br/>MCP capabilities and familiar clients<br/>Agents and extensions"]
    resource["Provider resource processes<br/>Managed MCP adapters<br/>External requests and usage reporting"]
    data[("Local persistent store<br/>SQLite<br/>Definitions, evidence and accounting")]
    web -->|"Application API: commands and reads; HTTP polling proposed"| api
    api -->|"MCP invocation; stdio proposed"| worker
    worker -->|"MCP or compatible client calls; loopback HTTP proposed"| api
    api -->|"Authorized, budget-reserved MCP calls"| resource
    api -->|"Persist and query through storage adapters"| data
  end
  person -->|"Uses in browser"| web
  resource -->|"Authorized provider requests: HTTPS"| ext
```

## View constraints

- Independent local component processes are required from the first cycle. Exact hosting and transport details remain under review; this view does not define source-module boundaries.
- The runtime serves the compiled browser application; a separate production Node backend is not required.
- Provider resources receive platform-authorized calls and return results and usage. Their external I/O belongs to the managed adapter boundary and must be instrumented for accounting. It does not grant agent processes direct provider access.
- Component-to-platform calls use their own client transport. They must not assume an MCP server can initiate arbitrary reverse requests on the platform's connection.
- Compatible client requests enter the runtime's adapters and shared admission controls before MCP dispatch to a component. Familiar call syntax does not grant direct access to another process or external provider.
- Credentials and trace payloads are outside the diagram; their lifecycle is covered by the [security view](security.md).
- The local boundary is a deployment scope, not a malicious-code sandbox.

## Review questions

Independent-process packaging is accepted in [ADR 0004](../adr/0004-component-packaging.md). Confirm the transport directions and compatibility mappings in [ADR 0007](../adr/0007-mcp-profile.md). SQLite is selected; detailed persistence and the [browser polling proposal](visual-model.md#proposed-live-update-behavior) remain under review in the [open-question register](../specification/open-questions.md). A component-level C4 view will follow when public module boundaries are approved.
