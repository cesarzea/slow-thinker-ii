# ADR 0004: Package components independently and run them as local processes

- Status: Accepted
- Recorded: 2026-09-27
- Decision-maker: César Zea
- Requirements: R02–R03, R05–R06, R08, R10
- Decision: Q01 closed by owner approval on 2026-09-27
- Remaining details: Q04, Q05, Q06, Q17

## Context and problem statement

Users must be able to add component implementations without editing the core. Exact package, launch, and runtime contracts have not been approved.

## Decision drivers

Independent code and definitions, language flexibility, compatible lifecycle management, explicit versioning, and a small initial deployment.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Manifest plus local MCP process | Language-independent boundary and separate lifecycle | Startup, identity and transport management |
| Python object loaded into the backend | Simple initial calls and debugging | Shared failure domain and language coupling |
| Container per component immediately | Stronger isolation possibilities | More packaging and orchestration work |

## Decision outcome

Use independent local component processes from the first functional cycle, with separately packaged code and definitions. The owner explicitly selected this option on 2026-09-27. Python examples may be supplied first, but the protocol contract must not require Python. Exact manifest fields, launch details and transports remain subject to their own contract decisions.

Component processes must be able to call LLMs, other agents, tools and resources through the orchestrator using familiar client interfaces. This requirement applies to outgoing calls from components as well as calls from external clients. Supported OpenAI and LangChain invocation signatures, including their use inside LangGraph nodes, must remain familiar; client configuration or adapters route them through the platform's controls. The supported method and parameter matrix remains Q04.

Separate component type, configured instance, process, node and activation identities. A process must not automatically imply a shared conversation or one instance per call. Unsupported instance/concurrency modes are rejected explicitly.

## Consequences

Need a local registry, package path resolution, a launch handshake, scoped credentials, and process teardown policy. A local process is not a security sandbox. Launch commands belong to a trusted installation profile, not arbitrary graph input.

The candidate manifest in the [component contract](../contracts/components.md) describes capabilities; executable launch details remain deliberately outside its current schema until approved. Compatibility adapters and MCP routing must share authorization, deadlines, accounting and trace correlation, including nested calls while a component is serving an activation.

## Confirmation

During implementation, validate a separately supplied component in an independent process without changing core code. Verify process exit, nested calls through familiar client interfaces, instance isolation, unsupported profiles, and version mismatches. Confirm a concrete MCP SDK supports the selected protocol profile before implementation. Decision acceptance does not claim these checks have passed.
