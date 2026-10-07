# ADR-0014: Component-owned dialogs and configurable composition

> **Superseded on 2026-10-04** by [ADR 0016](0016-graph-document-model.md) and [ADR 0020](0020-declared-component-configuration.md). The record below is retained unchanged.


**Status:** Accepted for the owner-authorized S06 correction, implementation pending.
**Date:** 2026-10-03. **Decision owner:** Cesar Zea.

## Context

The existing workspace exposes complete editable forms in a narrow inspector and
platform-owned compatibility profiles. Composition is demonstrated by fixed
RoutedCall/ContextualCall implementations, while an ordinary agent cannot acquire
a Redirector through the product. The owner requires independently configurable
components, component-owned dialog definitions and complete ordinary bundled forms.

## Decision

Use versioned declarative component-owned presentation, read-only inspector
summaries, isolated concept dialogs and a generic managed before/after composition
protocol. Discover metadata generically. Preserve historical descriptors and
legacy compositions. See the [dialog](../archive/previous-implementation/contracts/component-dialogs.md) and
[composition](../archive/previous-implementation/contracts/configurable-composition.md) contracts.

## Options considered

| Option | Assessment |
| --- | --- |
| Add more fixed combined agent types | Small initial change, but each combination needs a new implementation and special UI knowledge. Rejected. |
| Execute arbitrary plugin UI code | Flexible controls, but adds a new frontend execution/distribution/security model beyond this local sprint. Deferred. |
| Declarative dialogs and managed composition protocol | Reuses current field controls, host SDK and mediation; requires bounded metadata, structural planning and stronger cross-component acceptance. Selected. |

## Consequences and actions

Component authors own configuration meaning, attachment behavior and summaries.
The platform owns accessible rendering, exact drafts, validation and supervision.
Generic fallback preserves external configuration. Runtime before/after stages
cover the current correction without an internal graph engine. Arbitrary internal
graphs, concurrent emissions and additional UI control protocols remain future
versions, not implied capabilities. Full preparation, parallel implementation,
combined review and complete verification are defined by
[S06-COMPOSITION](../archive/previous-implementation/specification/s06-composition-and-dialogs.md).
