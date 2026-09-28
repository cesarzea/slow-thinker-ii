# Call authority and causal context

**Status: Proposed local profile, 2026-09-28.** R05–R08, R11–R15; Q04, Q06, Q08, Q10, Q17. This specifies authorization semantics; transport-level credential delivery still needs an SDK conformance check.

## Platform-owned invocation context

For each invocation the platform creates an opaque, short-lived grant mapped to the run, graph revision, caller instance, originating activation when applicable, current call, allowed targets/operations and effective deadline. The target's context is distinct from its caller's context. It can authorize that target's own permitted subcalls; it cannot impersonate the caller or another participant.

The host receives the grant over its trusted launch/invocation channel and configures fresh standard clients for the platform endpoint. Model-client authentication carries scoped platform authority, not a provider API key. Native MCP clients use their supported authenticated transport. Component code keeps familiar invocation signatures; graph data and tool arguments never serve as proof of identity.

The local stdio implementation carries the invocation token in `_meta["slow-thinker-ii/invocation-grant"]`. The platform connection also sends `_meta["slow-thinker-ii/deadline-monotonic"]`, a finite absolute monotonic deadline shared by processes on the same host. The host rejects expired deadlines and clamps the fresh OpenAI client's timeout to the remaining duration. This clock representation is limited to local processes; it is not a cross-host timestamp. The HTTP SDK client sends the invocation token as its bearer credential to the configured loopback endpoint. The transient `access` module implements the token registry, filtered aliases, receiver-specific permissions, revocation, call/depth limits and deadline checks. It retains only credential digests and separates revoked authority from still-executing calls. The application admission service coordinates its decisions with durable request/dispatch records and budget reservations. Wiring the outward HTTP/MCP routes remains pending. This proposal intentionally defines no new required model-call argument and assumes no SDK feature solely from its name. Host startup has discovery/readiness authority only, not a reusable run-wide credential for business calls.

The [temporary SDK probes](sdk-compatibility.md) confirmed supplied request metadata over stdio and loopback HTTP, plus configured bearer headers on HTTP. Those transport carriers are viable candidates. The probe's fixed synthetic credential and revocation flag are not an implementation of platform grants, graph permissions or authenticated causal identity.

## Admission path

1. Authenticate the grant and resolve its server-side context; reject expired, revoked or unknown authority.
2. Verify that run and parent-call admission remain open and their deadlines have not expired.
3. Resolve the target instance/operation in that run's frozen registry and check the graph's permission rule. Resource binding alone does not grant access.
4. Validate arguments against the effective target schema and supported call profile; check reentrancy, depth and call-count limits.
5. Assign authoritative child-call and attempt identifiers. Reserve any billable maximum atomically across all applicable scopes before dispatch.
6. Dispatch through MCP using a context for the target operation; record the relationship and boundary outcome. Release the admission lock before waiting.

Scheduler calls to listed nodes and the selected controller use platform authority derived from the admitted graph. Component-originated calls use the explicit permission map. A provider resource may carry out only the external request admitted for its attempt; receipt of one request does not authorize a separate billable retry.

## Discovery and routing

Return only operations permitted to the authenticated context. Invocation repeats authorization even if the caller already discovered a tool. Cache discovery by run revision, instance/configuration identity and authority scope; invalidate it on revocation or restart.

For the initial proxy, propose generated tool aliases such as `op_0001`, with an immutable per-run mapping to `(instance_id, operation_id)`. Expose readable participant/operation labels separately. Avoid parsing user identifiers from concatenated tool names; aliases grant no authority and are not stable across runs. A model alias similarly resolves only to the permitted bound model resource.

When one component calls another, the receiver uses its own graph-granted permissions for any nested work. Access to the receiver does not grant the caller direct access to all of the receiver's resources. Every nested call still belongs to the same run, deadline tree and spending scopes.

## Revocation and late evidence

Close invocation authority when its operation finishes, is cancelled or expires. Close all run work authority when the run stops. Subsequent use must fail before dispatch, including requests from a process reused for a later activation. Reconstructing old context from a trace must not restore authority.

Late provider usage follows a separate trusted settlement path tied to an existing attempt; it can settle costs but cannot invoke operations, replace terminal outcomes or advance the graph. A run can finish before this evidence becomes available. The concrete reconciliation transport remains Q08/Q09.

Use fresh per-invocation clients or equivalent isolated adapter state. A shared mutable client whose authentication is changed for successive calls is not an acceptable correlation mechanism. Future concurrent invocations require isolated contexts even if they share a host.

## Evidence and secrets

Persist call identities, permissions applied, target, decision and causal links. Do not persist bearer grants, provider credentials or complete authentication headers in graphs, prompts, errors or ordinary traces. User-supplied correlation labels may be retained as data but cannot override platform identities.

Local trusted components remain the first deployment assumption. Possession of an invocation grant is not OS process isolation; containment of malicious code is outside this profile. This contract limits managed routes and does not claim control over undeclared direct network access by arbitrary local code.

## Acceptance examples

| Case | Expected managed behavior |
| --- | --- |
| Proposer calls its bound model with a valid context. | Admit one child attempt; preserve proposer and originating activation in evidence. |
| Proposer names the reviewer as caller in request data. | Retain authenticated proposer identity; data cannot change authority. |
| A bound memory lacks a permission grant. | Discovery omits it and direct invocation fails before dispatch. |
| A reused proposer process sends its previous invocation grant. | Reject it; the current invocation's client has a different context. |
| A parent completes while a child is still active. | Apply the lifecycle violation policy; no successful downstream binding. |
| Usage arrives after cancellation. | Settle the original attempt once; no new graph work. |

These are proposed acceptance cases for QA03, QA07, QA14 and QA24. No credential mechanism or interoperability claim is verified by this document.
