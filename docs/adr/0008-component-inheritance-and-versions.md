# ADR 0008: Support optional implementation inheritance with bounded versions

- Status: Proposed; recovered by the [scope review of 2026-10-06](../specification/scope-review-2026-10-06.md) and scheduled for S22
- Recorded: 2026-09-27
- Decision-maker: Cesar Zea
- Requirements: R02–R03, R16, R24, R27
- Open questions: Q13, Q17, Q20

## Context and problem statement

The owner proposes deriving component A from an implementation of component B, either fixing B's version or accepting compatible updates within a major version. This goes beyond configuring several instances of one type. Experiment history must identify the actual implementation used even when the declaration permits several versions.

## Decision drivers

Reusable implementations, optional inheritance, independent component versions, explicit compatibility, reproducible dependency selection and small functional cycles.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Independent implementations and instance configuration only | Smallest packaging model | Does not provide the requested implementation inheritance |
| Optional inheritance with version constraints and an exact dependency lock | Reuses implementation while preserving resolved provenance | Requires an extension API, resolution rules and compatibility checks |
| Resolve the newest allowed base whenever a run starts | Immediate uptake of updates | Identical graph declarations may execute different implementations without a reviewed dependency update |

## Decision outcome

The owner confirmed basic single inheritance for the first functional cycle and specified inheritance through code. Keep component types independently versioned. Multiple instances of the same type remain ordinary configuration; a derived implementation is a distinct type with its own version. This ADR remains Proposed while its detailed extension and packaging contract is reviewed.

Use [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) for stable component releases. Compatible additions increment the minor version; compatible fixes increment the patch version; changes that break the declared public contract require a major version. Released artifacts are immutable. The compatibility promise must include the documented extension API used by descendants, as well as external operations and schemas.

| Declared dependency of A | Permitted base releases | Excluded releases |
| --- | --- | --- |
| Exactly B `1.1.0` | `1.1.0` | Every other release |
| B `>=1.1.0,<2.0.0` | Stable `1.1.0`, `1.1.1`, `1.2.0`, and later compatible 1.x releases | Releases below `1.1.0`, 2.x and, by default, prereleases |

These expressions illustrate policy; the proposed Python profile uses standard package dependency syntax, with the resolved mapping recorded in trusted registration metadata. That profile remains under review in Q20. SemVer defines version meaning and ordering, not a universal dependency-range grammar. For initial 0.x and prerelease artifacts, recommend exact pins until their compatibility policy is explicit.

The major versions of A and B do not need to match. An A release depending on B 1.x continues to use B 1.x when B 2.0 appears. A new release of A may explicitly adopt B 2.x after adaptation and verification; A needs its own major increment only if its public contract breaks. Existing published A artifacts are never rewritten.

### Dependency resolution and experiment provenance

Recommend resolving permitted ranges during installation or an explicit dependency update. Persist the exact base versions, artifact digests and transitive dependency closure in an immutable resolution record. Each run retains that resolution alongside its graph and component configuration. Starting or repeating a run must not silently refresh dependencies.

An allowed update can select a newer B without editing A's declared range. It creates a new resolution record and must pass compatibility checks. A published component artifact that embeds its base needs a new component release to change that embedded code; a range never permits modifying an existing release in place.

The resolver rejects unavailable releases, incompatible constraints and inheritance cycles. Compatible parent updates must not grant additional graph permissions or change platform limits. The [installation proposal](../archive/previous-implementation/contracts/component-installation.md#proposed-environment-and-installation-policy) recommends isolated, immutable resolutions with exact hashed wheel locks; compatible updates create new environments without changing old runs. A temporary synthetic-package probe supports this packaging mechanism, not platform-loader conformance. Approval and complete installation metadata remain Q17/Q20.

### Implementation boundary and first-cycle scope

Start with single implementation inheritance and documented extension points. Composition can combine additional capabilities; multiple inheritance and conflict precedence require a separate decision. Standalone component implementations remain valid.

Implementation inheritance is resolved within a component's package/environment and must use a compatible language/runtime. It does not create another graph participant, shared agent state or a direct call to a running base component. Managed calls made by inherited code still pass through the orchestrator. MCP remains the public communication boundary for the resulting component.

Q20 must close the extension points, override rules, resolver/update policy and lock format. The [registration proposal](../archive/previous-implementation/contracts/component-installation.md) separates public component descriptors from installed Python classes, package requirements and resolved base metadata. The examples are review fixtures, not installed components.

### Proposed Python code model

Provide the reference `LLMCall` implementation through a versioned Python package with public exports. A separately packaged implementation derives from it using ordinary [Python class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance). The [Python interface](../archive/previous-implementation/contracts/python-component-api.md) proposes the public JSON values and the `build_messages`, `parse_response` and `validate_result` hooks. The [GroundedReview specimen](../archive/previous-implementation/contracts/examples/grounded-review.md) overrides result validation to check citation identifiers against the activation's input. Package names, types and hook signatures remain proposed.

The base implementation coordinates input preparation, one logical model invocation through a platform-configured familiar client, and response conversion. A descendant can reuse base behavior with `super()` or replace documented extension methods while preserving its declared contracts. Prompts and output schemas remain configurable for cases that need no new implementation. Common schema checks remain outside replaceable hooks and are independently checked at the platform boundary.

Declare the Python base dependency in the derived package's `pyproject.toml`, following [standard packaging metadata](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#dependencies-optional-dependencies). For example, the dependency entry can be `slow-thinker-llm-call==1.1.0` for a fixed stable release, or `slow-thinker-llm-call>=1.1.0,<2.0.0` for compatible updates. These package names and stable versions are illustrative; no such release is claimed. Dependency tooling resolves the installed code; the platform records that resolution and verifies the mapping to component type/version metadata. Do not maintain a second independent dependency resolver in graph JSON.

The derived process imports its base implementation locally. Register the resulting concrete type and its effective operations with the platform through the trusted installation contract. The descriptor and MCP surface expose the completed component; a descriptor alone does not implement code inheritance. Resolve conflicting dependency versions in separate compatible environments, with the exact installation procedure still Q17.

Inheritance hooks are extension mechanisms, not enforcement boundaries. The orchestrator applies permissions, deadlines and accounting to managed calls regardless of which inherited method issued them. Exact subclass hooks and replacement rules must not restrict the platform's ability to host standalone or more complex component implementations.

## Consequences

Authors gain reusable implementations and a controlled path for compatible updates. Maintainers must preserve extension contracts, validate dependency closures and retain exact artifacts or report their unavailability. An exact dependency record supports configuration reproducibility; it cannot guarantee identical LLM outputs or unchanged external services.

Version numbers express a compatibility promise that requires verification. Contract and extension tests must accompany releases; successful checks cannot prove that every possible descendant is compatible. Output-quality changes may matter experimentally even when the API remains compatible.

## Confirmation

Review Q20 before accepting this ADR or changing manifest schemas. Later verify exact pinning, same-major updates, rejection of 2.x for a 1.x constraint, independent A/B major versions, unavailable bases, cycles, transitive conflicts, immutable locks and retained historical resolutions. Verify inherited calls use the same permissions, accounting and tracing controls. No inheritance resolver or compatibility tests are implemented by this document.
