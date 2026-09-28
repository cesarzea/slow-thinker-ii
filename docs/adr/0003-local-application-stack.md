# ADR 0003: Start with a local Python backend and TypeScript browser UI

- Status: Accepted
- Recorded: 2026-09-27
- Decision-maker: César Zea
- Requirements: R17–R22

## Context and problem statement

The first functional cycle must remain small while providing graph visualization immediately. The owner selected Python for the backend and accepted the browser stack recorded in the README.

## Decision drivers

Local single-user operation, graph inspection, typed interfaces, separation of domain representation from visualization, and a path to server deployment.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Python/FastAPI plus React/TypeScript | Agreed stack; clear backend/UI separation | Two language toolchains and contract coordination |
| Terminal-only initial application | Smaller initial UI | Does not meet first-version visualization requirement |
| Multi-user hosted system immediately | Earlier remote access | Adds deployment and access concerns before the execution foundation |

## Decision outcome

Use FastAPI with Python; React, TypeScript and React Flow with Vite for the browser. The backend serves the compiled UI locally. Maintain a versioned domain graph independently of React Flow data and layout state.

Begin with one active workflow and saved history. Component processes, storage technology, browser status transport, and the JSON editing location remain separate decisions.

Subsequent decisions: [ADR 0004](0004-component-packaging.md) selects independent component processes. [Q02](../specification/open-questions.md) selects bundled graph examples for the first UI, with editing tools and manual JSON upload later. Storage and browser status transport remain open.

## Consequences

Public contracts connect frontend and backend. Closing the browser must not own or terminate backend execution. Future server deployment must not require rewriting domain graph definitions.

## Confirmation

Review the C4 container view and module boundaries. QA10–QA13 verify browser reconnection, interrupted-run handling, identity presentation, and readable layout. Architecture checks prohibit UI-library types in core domain contracts.
