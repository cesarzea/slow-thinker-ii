# Component registration and installation

**Status: Approved first-cycle contract.** R02, R06, R08, R27; Q04, Q05, Q06, Q17, Q20. Code inheritance, separate local processes and these records form the approved first-cycle installation profile.

## Separate declarations

| Artifact | Responsibility |
| --- | --- |
| Component descriptor | Public type/version, operations, configuration schema and execution capabilities. |
| Python package metadata | Code distribution, public exports and dependency constraints. |
| Trusted registration | Maps a component type to its installed distribution, public class and environment profile. |
| Resolved environment lock | Exact transitive package versions and artifact identities; retained with the run. |
| Graph | Configured component instances, resource bindings, operation use and permissions. |

The graph never supplies import strings, install commands or executable launch arguments. The trusted catalog owns those mappings. Components remain independent packages; importing their code is performed by their host process, not the application backend.

## Registration proposal

The [registration schema](schemas/python-registration.schema.json) and examples for [LLMCall](examples/llm-call.registration.json) and [GroundedReview](examples/grounded-review.registration.json) define the initial Python record:

- `type_id`, `type_version`: must match the referenced descriptor.
- `descriptor`: a manifest filename within the trusted catalog.
- `distribution`: installed Python package name and exact distribution version.
- `entry_point`: public `module:Class` export in that package.
- `environment_profile`: trusted environment and launch configuration; currently an illustrative reference.
- `base`: optional immediate implementation-base identity, declared package requirement and exact resolved package/class. This is evidence of code inheritance, not a replacement for it.

Component versions and Python distribution versions are separately identified: the illustrative component version is `0.1.0-example`, while the Python development release uses `0.1.0.dev1`. The registry verifies their mapping and never assumes the strings must be identical. Stable base range examples remain in [ADR 0008](../../../adr/0008-component-inheritance-and-versions.md).

Resolve dependencies through standard Python package tooling and validate constraints before launch. The registration's `base` must agree with actual package metadata and installed class ancestry. It is not a second source of dependency resolution. Recursive base metadata must be acyclic; incompatible dependency closures require separate environments or an explicit installation error. A registry record alone does not prove code compatibility.

## Load and execute

1. Select the exact descriptor and trusted registration for each configured type/version.
2. Select its already installed, approved environment resolution and verify artifact identities, metadata, base relationships and supported SDK/profile versions. Run admission does not solve dependency ranges or install missing packages.
3. Validate instance configuration and bind effective input/output schemas and permitted resources.
4. Launch the independent component host in the selected environment; it imports the registered public class and prepares its hosting contract. The LLMCall profile validates configuration/schemas at readiness and constructs a fresh implementation object with a platform-configured familiar client per invocation. Other component types have their own dependencies and object lifetimes. The backend does not import arbitrary component packages.
5. Verify readiness and MCP discovery against the effective instance operations before accepting invocations. Transport details remain ADR 0007; readiness deadlines, credentials and correlation remain Q06/Q17.
6. Route the requested, authorized operation to the concrete implementation, propagate cancellation as supported, and record calls/results/usage through the platform. `generate` is LLMCall's operation, not a mandatory operation for tools, memory or controllers. Unhandled operation failures do not advance the sequence.

The owner considers one host per configured component instance per run a possible starting point, with tools, memory and other resources needed soon afterward (2026-09-28). The working proposal reuses that host across the instance's sequential activations, creates fresh invocation-local clients and LLMCall objects, and closes run-owned hosts when execution ends. A base class does not add another host. This is an initial deployment profile, not a universal lifecycle rule; exact teardown, concurrency and reset guarantees remain Q05/Q17.

Process lifetime, component state and durable resource data are separate concerns. Closing a host releases execution resources; it does not authorize deleting a persistent memory store or stopping an external service. Future shared services and persistent resource bindings require explicit ownership, access, retention and reset policies. The first profile does not yet implement them. See [resource and memory binding](components.md#resource-and-memory-binding).

The [lifecycle proposal](component-lifecycle.md) specifies readiness, host states, nested-call handling and bounded cleanup. The [call-authority proposal](call-authority.md) specifies fresh invocation context and revocation while preserving familiar client signatures. Their acceptance and concrete SDK/launch mapping remain Q05/Q06/Q17.

## Proposed environment and installation policy

Recommend `uv` as the initial Python resolver/installer, with one exact dependency closure per environment. The tested candidate is `uv 0.12.17`; installation tooling and Python interpreter versions must be pinned in the setup profile. Propose CPython 3.13 as the first compatibility target, selecting a maintained exact patch before implementation setup. The temporary Python 3.13.0 probe does not select that old patch for the application.

Use independently locked projects/environments for the backend and component distributions. Two components needing different versions of one base must not be forced into a common environment. A repository may contain several projects; it does not require one uv workspace spanning every independently versioned component. uv workspaces share a lock and resolve their members together. [Workspace behavior](https://docs.astral.sh/uv/concepts/projects/workspaces/).

Development projects may use committed `uv.lock` files. Managed component installations use a generated, complete `requirements.txt` lock with exact versions and SHA-256 wheel hashes, selected for the target interpreter/platform. These are different artifacts: the development lock includes its declared development groups, while the installation lock contains only the component, host and production dependencies. Neither is maintained manually as a second independent dependency declaration; retain the source metadata and explicit resolution inputs that generated it.

The installation lock must include the host's required SDKs as well as the component's dependencies. An incompatible component/host closure fails installation; do not downgrade the selected MCP profile to satisfy it. The existing [SDK compatibility finding](sdk-compatibility.md) remains applicable. Dev-only packages and editable source checkouts are excluded from managed experiment environments.

uv documents hash-pinned requirements and exact environment synchronization. The proposed installation uses `uv pip sync` with an explicit target interpreter, hash checking, binary-only artifacts and offline access to a prepared local wheel directory. [Locking environments](https://docs.astral.sh/uv/pip/compile/), [installer options](https://docs.astral.sh/uv/reference/cli/). Disable inherited uv configuration and automatic interpreter downloads; package-index access belongs to explicit preparation, never graph startup.

Standardized [pylock.toml](https://packaging.python.org/en/latest/specifications/pylock-toml/) remains a possible later artifact format. The installed uv candidate reports its support as experimental, so it is not required by this first proposal. Exact hashed requirements were exercised successfully in the [offline probe](../evidence/packaging-review-20260928.json).

### Preparation and publication

1. Build first-party components into wheels from identified source and controlled build dependencies. Record the source revision/digest, wheel digest and build tooling. Never publish changed wheel bytes under an existing released identity.
2. Resolve the component, host and approved SDK constraints for one target platform/interpreter. Retain exact transitive versions, selected wheel identities/hashes, extras/markers and the resolver version. No range or implicit latest version remains in the installation lock.
3. Fetch/build required artifacts during this explicit preparation step, verify their origins and hashes, and retain them outside the source tree in a managed artifact store. A local wheel cache is not a public release, signature or security audit. Apply the mandatory supply-chain gates separately.
4. Create a fresh, unregistered environment at its final path; install from the complete lock using only those verified wheels. Disable editable installs, implicit source builds, package-index fallback and development groups. An unavailable compatible wheel fails preparation rather than starting a build during execution.
5. Verify package metadata/dependencies and run the component's contract/extension checks in that environment. Verify entry points and class ancestry in an isolated subprocess, with no provider credentials or business-call authority. Record outcomes; installing packages alone cannot establish behavioral compatibility.
6. Publish the catalog's immutable resolution reference only after verification succeeds. Do not relocate a virtual environment as a substitute for publishing its reference. A failed preparation leaves previous registrations/resolutions usable and cannot modify an active environment.

The resolution record includes its identity, installation lock digest, component/host artifact identities, exact Python build, OS/architecture/ABI, approved SDK profile and verification evidence. Installed distribution metadata is checked against it before launch. File hashes and environment policy support reproducibility; trusted local code remains an assumption, not a claim of tamper-proof OS isolation.

Instances using the same exact resolution may share the installed environment, but each still has its own host process and invocation context. Runtime writes use separate run/instance directories or declared resource storage, never package files. Interpreter/package sharing does not grant shared memory, credentials or graph state.

### Launch without installation side effects

The backend launches the resolved environment's absolute Python executable with an argument vector for the installed host entry point; no shell evaluation or graph-supplied executable path. Use an isolated Python import context and a minimal, explicit environment allowlist so user-site packages or inherited import paths cannot silently supply a different base. Host stdout is reserved for MCP transport; bounded diagnostics use stderr and the recording rules.

Do not invoke an auto-syncing package runner when launching an experiment. uv may lock or synchronize environments as part of `uv run`; a successful package lookup is not permission to update a run's code. [Automatic synchronization](https://docs.astral.sh/uv/concepts/projects/sync/). Missing or inconsistent installed environments fail admission and require explicit preparation. Exact bootstrap arguments and credential delivery remain Q06/Q17.

### Updates, repetition and removal

An explicit update re-resolves allowed dependency ranges into a new environment/resolution, preserving the old one. Exact B `1.1.0` pins stay fixed; a B `>=1.1.0,<2.0.0` range may select `1.2.0`, never `2.0.0`. The update must pass the same checks and cannot mutate an already admitted run. Graph/component versions and environment-resolution versions remain separate recorded identities.

Repeating a historical experiment selects its original resolution by default. If required artifacts or a supported interpreter are unavailable, report that limitation; selecting a new resolution is an explicit changed experiment. Package records cannot guarantee identical model responses or external services.

Automatic removal of historical artifacts is outside the first profile. Never remove an environment used by a live host. Any later cleanup must preserve run metadata and declare when it makes exact reinstantiation unavailable. Removing code artifacts cannot erase trace/accounting data or persistent resource contents.

## Verification boundaries

Review checks validate schema structure, descriptor/type mappings and declared version constraints. The offline packaging probe additionally exercised ordinary subclass imports in separately installed synthetic packages, exact pins, a compatible update, unchanged old locks, a rejected major-version conflict and rejection of a valid ZIP wheel whose bytes failed the recorded hash. The probe used local wheels and no provider calls; it did not execute a platform host or real component.

Repository tests now cover registration/ancestry validation, immutable resolutions, rejected updates, integrity, readiness and mediated inherited calls. Seven actual component environments were prepared and exercised separately from synthetic installation fixtures. Exact evidence and limitations are recorded in the [verification record](../verification.md).
