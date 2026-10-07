# ADR 0020: Component-declared configuration rendered by the platform

- Status: Accepted
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR08, CR09, CR14
- Supersedes: the dialog vocabulary of [ADR 0014](0014-component-owned-dialogs-and-composition.md)

## Context and problem statement

What the interface shows for a component must be defined inside that component's
package, and the platform builds the interface. The previous vocabulary included
LLM-specific controls, which placed model semantics in the platform.

## Decision outcome

Each package declares, in its [component declaration](../contracts/component-declaration.md),
its configuration schema and an interface declaration made of sections and fields.
The platform renders them with a fixed vocabulary of generic controls: text,
multiline, number, choice, list, code, schema and service. The service control
lists the platform's entries for a declared service and renders the selected
entry's parameter schema inline. A node's dialog contains the host component's
sections followed by each embedded component's sections. Components ship no
interface code; undeclared configuration falls back to a form generated from the
configuration schema.

## Consequences

A component that needs a control outside the vocabulary requires a new platform
control version, not component code. Declarations are validated when a component
is installed and when the catalog is served.
