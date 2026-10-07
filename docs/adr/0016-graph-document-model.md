# ADR 0016: Graph documents of nodes, ports, connections and embedded components

- Status: Accepted
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR01, CR05, CR09, CR14
- Supersedes: [ADR 0013](0013-workspace-authoring-state.md); the composition part of [ADR 0014](0014-component-owned-dialogs-and-composition.md)
- Amends: [ADR 0005](0005-versioned-contracts.md) for the graph contract

## Context and problem statement

Users think in nodes connected through named outputs and inputs, including loops,
with a Router placed inside an agent to give it several outputs. The previous
graph format expressed topology through controller configuration, permissions,
slots and containment, and edited exact JSON text through server patches.

## Decision outcome

A graph is a typed document, [graph format 1](../contracts/graph-document.md):
nodes with a component reference and configuration, optional embedded components
with a position, connections from an output port to an input port, run limits and
layout. Effective ports come from the component declarations; a node with an
embedded output component exposes that component's outputs. The editor works on
a local copy and saves the whole document; each save creates an immutable version.
Runs record the version they executed. The document contains no permissions,
wrapper nodes or internal identifiers.

## Consequences

Validation is a pure function of the document, the installed component
declarations and the platform's LLM catalog, and is used both when saving and
before a run. Exact-text patching, composition plans and restoration journals are
not needed. Large-integer preservation across the browser is not required by the
S06 components.
