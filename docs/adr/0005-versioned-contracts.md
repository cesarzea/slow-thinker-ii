# ADR 0005: Separate versioned component, graph and run contracts

- Status: Accepted on 2026-10-07 with S06, as amended by [ADR 0016](0016-graph-document-model.md) and [ADR 0020](0020-declared-component-configuration.md)
- Recorded: 2026-09-27
- Decision-maker: Cesar Zea
- Requirements: R02–R04, R09–R10, R16–R19, R24
- Open questions: Q05, Q11, Q13

## Context and problem statement

The same agent can participate in multiple nodes and activations. Future controllers may express dynamic graphs. A UI serialization or fixed sequence object cannot become the universal domain model.

## Decision drivers

Stable identities, explicit compatibility, reusable components, extensible control policy, inspectable lineage, and machine-checkable examples.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Versioned domain contracts with extension-specific configuration | General core with explicit supported profiles | Requires schema and semantic validation |
| Persist the visualization library's graph | Fast initial editor wiring | Couples execution and saved experiments to UI details |
| Encode every future control mechanism in one core schema | Single apparent contract | Prematurely fixes semantics and grows the core |

## Decision outcome

Recommend separate component manifests, graph definitions, run input, and event envelopes. Use JSON Schema 2020-12 for structural review, with explicit semantic checks. Proposed schema version `0.1-draft` is not a stable API promise.

The graph references configured instances and node operations. A versioned controller configuration owns control-specific data. The initial sequence profile supports finite ordered node lists; other profiles must be rejected until implemented. Later dynamic revisions preserve their lineage and activation references.

## Consequences

Schema-valid does not mean executable or authorized. Type resolution, binding compatibility, permission coverage, ordering, and limit policy require semantic validation. Extension configuration is not permission to ignore unknown core fields.

The review schemas deliberately omit transport secrets, process commands, persistence-engine details and automatic migration rules. These remain visible open decisions.

## Confirmation

Validate the review example and deliberately invalid variants. Demonstrate two instances and three activations conceptually, without conflating the controller or model resource with an agent. Review each future capability against this boundary before accepting the schema.
