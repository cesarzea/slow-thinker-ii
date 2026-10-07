# Context and container views

## System context

```mermaid
flowchart LR
  operator([Operator])
  author([Component author])
  platform[Slow Thinker II platform]
  providers[(Model providers: OpenAI, DeepSeek)]
  packages[[Component packages]]
  operator -- builds, runs and inspects graphs --> platform
  author -- publishes --> packages
  packages -- installed into --> platform
  platform -- HTTPS with server-side credentials --> providers
```

## Containers

```mermaid
flowchart TB
  subgraph browser[Browser]
    ui[Interface: graph list, editor, run and activity views]
  end
  subgraph backend[Backend process]
    api[Operator API /api/v2]
    gateway[LLM gateway /v1 and reports /mcp]
    app[Application: graph library, runs, usage]
    engine[Engine]
    store[(SQLite: graphs, versions, runs, events, ledger)]
    prov[Provider adapters]
  end
  subgraph hosts[Component hosts, one process per node or embedded component]
    llm[LLM Call]
    router[Router]
    memory[Memory]
  end
  ui -- HTTPS JSON, operator token --> api
  api --> app
  app --> engine
  app --> store
  engine -- MCP over stdio: activate, select_output --> llm
  engine -- MCP over stdio: select_output --> router
  engine -- MCP over stdio: recall, remember --> memory
  llm -- Chat Completions, invocation grant --> gateway
  llm -- platform.report --> gateway
  gateway --> prov
  gateway --> store
  prov -- HTTPS --> ext[(Model providers)]
```

The platform is the only participant that holds credentials and the only path
between participants. Trigger and Output nodes run inside the backend.

## Components of the backend

```mermaid
flowchart LR
  http[adapters.http] --> application
  bootstrap --> http
  bootstrap --> sqlite[adapters.sqlite]
  bootstrap --> hostsA[adapters.hosts]
  bootstrap --> providersA[adapters.providers]
  bootstrap --> installations[adapters.installations]
  application --> engine
  application --> graphs
  application --> access
  application --> accounting
  engine --> graphs
  graphs --> catalog
  catalog --> contracts
  access --> contracts
  accounting --> contracts
```

Adapters implement ports defined by `application` and `engine`; arrows show import
direction. The [module boundaries](module-boundaries.md) enforce it.
