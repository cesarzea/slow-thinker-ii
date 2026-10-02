# Personal experiment acceptance support: specification

Supports the [S03 testing assignment](../../../../docs/specification/personal-experiments-sprint.md).
Definition fixtures use public JSON/graph contracts. Preparation uses the production
InstalledWorkflowPreparer and real immutable library, with existing synthetic installation
descriptions that cannot launch inference.

The replacement RunEnvironment runs the real Sequence process and a public OperationPort
wrapping real LLMCall. Its native SDK uses an in-memory HTTP transport that records requests
and calls the public NativeModelGateway. A metered simulated model operation retains ordinary
managed-call authority/accounting. Tests execute the production prepared program and policy;
they do not inspect private program fields or claim executable installed provider packages.

Runtime evidence includes exact changed prompt/input, admitted snapshot, persisted results,
mediated child calls and process cleanup. All secrets, provider responses and transport are
synthetic; no paid provider access is required.
