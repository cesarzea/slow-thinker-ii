# ADR 0010: Validate LLMCall output without implicit repair calls

- Status: Accepted
- Recorded: 2026-09-27
- Decision-maker: César Zea
- Requirements: R08, R11–R14, R29
- Remaining details: Q04, Q08, Q10, Q13

## Context and problem statement

The reference single-call component must support configurable text and structured JSON output. Invalid output needs an explicit result that preserves evidence without silently adding model calls, cost or a different collaboration process.

## Decision drivers

Visible failure, retained evidence, predictable model-call count, explicit spending and reusable output contracts.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Accept any response as successful text | Smallest implementation | Does not honor a structured output contract |
| Return a structured validation error with the received response | Preserves evidence and the one-call behavior | Caller must handle or explicitly configure recovery |
| Automatically ask an LLM to repair invalid output | May recover some responses | Adds implicit calls, cost and behavior |

## Decision outcome

The owner accepted text or JSON validated against a configured schema. On invalid structured output, return a structured error and retain the original received response. Do not implicitly coerce the response or make a repair call. Any additional call requires explicit configuration and normal accounting/admission.

The [LLMCall contract](../contracts/llm-call.md) proposes concrete configuration fields, result envelopes and validation rules. Acceptance of this policy does not approve every detailed schema, provider mapping or installation mechanism in that proposal.

## Consequences

A failed output validation remains inspectable and may still have incurred provider cost. The sequence executor treats the unhandled result as failure and does not supply it as a successful downstream value. Repair can later be an explicit graph step or configured retry behavior, with its own evidence and spending authorization.

## Confirmation

During implementation, verify text preservation, valid JSON, malformed JSON, schema mismatch, original-response retention and exactly one provider attempt for the default behavior. Verify no downstream activation on unhandled failure and no lost usage charge. Documentation fixtures exercise candidate schemas only; they are not runtime evidence.
