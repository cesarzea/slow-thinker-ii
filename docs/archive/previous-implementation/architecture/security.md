# Initial threat model

**Status: Proposed analysis; controls are required but not implemented.** The initial environment is local and single-user, with trusted component code. This document supports the mandatory [OWASP LLM risk mapping](https://genai.owasp.org/llm-top-10/) and [ASVS requirements](https://owasp.org/projects/asvs); it is not a certification or a completed verification assessment.

## Assets and trust boundaries

Assets include provider credentials, private prompts and outputs, reported reasoning/state, graph definitions, execution authority, saved spending balances, and analysis results.

Boundaries exist between browser and backend, component processes and the routing authority, local storage and its readers, and the platform and external providers. Component outputs and fetched material remain data even when they contain instructions. An MCP tool description is not an authorization grant.

## Initial threats and required responses

| Threat | Risk reference | Required design response | Verification |
| --- | --- | --- | --- |
| Instructions embedded in another agent's output seek extra tool access. | LLM01 / LLM06 | Effective permissions come from the run policy and authenticated caller identity. Output text cannot expand them. | QA03; adversarial output fixture |
| Sensitive reasoning or resource contents reach an unintended recipient. | LLM02 | Separate trace access from component-visible context; enforce resource and operation scopes. Define redaction and retention before implementation. | QA05, QA15; access tests |
| A component bypasses accounting to call a provider directly. | LLM06 / LLM10 | Trusted-component contract forbids bypass. Route credentials and spending authorization through managed adapters. Explicitly exclude malicious-code containment from this deployment claim. | Managed-route tests; later isolation review |
| Unbounded loops, retries, payloads, or schema validation exhaust resources. | LLM10 | Deadlines, spend reservations and bounded control policies; choose input/schema/payload limits. | QA06–QA09; malformed input fixtures |
| Dependency or workflow changes compromise the build. | LLM03 | Apply the README supply-chain requirements from initial setup. | Dependency checks, CodeQL, pinned actions, Scorecard |
| Agent output is executed as code or interpreted as privileged configuration. | LLM05 | Validate typed boundaries; do not evaluate input-binding strings as code. | Contract validation and injection tests |
| Fabricated explanations contaminate later influence analysis. | LLM09 | Label observed, reported and inferred evidence; preserve evaluator versions and uncertainty. | QA05, QA18 |

## Local endpoint controls

If the proposed loopback HTTP MCP endpoint is adopted, require authentication and origin validation, bind locally, and issue scoped component credentials. Caller-supplied instance identifiers are not proof of identity. The [call-authority proposal](../contracts/call-authority.md) defines per-invocation scope, causal context, isolated clients and revocation. Concrete credential delivery, SDK support, browser access and launch protocol remain blocking decisions.

The [operator API](../contracts/operator-api.md) is a separate authority surface. Component grants cannot start runs, change budgets or read operator traces. Browser command identities and payload references are not credentials. Durable duplicate suppression does not replace authentication, origin/CSRF controls or per-object access checks.

## Recording and secrets

Recording all managed interactions does not authorize copying authentication secrets into payloads or traces. Secret references and redaction markers must preserve the ability to understand what was omitted. The [observation proposal](../contracts/observation.md) defines explicit capture statuses, provenance for reported internals and visible recording failures. Retention/deletion, encryption at rest and provider-specific reasoning mappings still require approval; no completeness or secure-erasure claim follows from saving an event envelope.

## Release and deployment assurance

Threat modeling begins with this design. ASVS applicability and requirement identifiers must be tracked during implementation, with Level 2 verification before the first server deployment. Signed artifacts, provenance and software bills of materials apply to the first release. Criteria that need executable evidence cannot be marked verified while the application is absent.
