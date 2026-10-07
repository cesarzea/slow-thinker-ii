# Risks and unresolved assumptions

**Status: Initial register.** There is no application implementation yet. Closure actions reference the [open questions](../specification/open-questions.md).

| ID | Risk | Consequence | Response / decision needed |
| --- | --- | --- | --- |
| K01 | Component mediation is mistaken for OS isolation. | A malicious local process could bypass declared interfaces. | State trusted-code scope; choose stronger isolation before untrusted execution. Q01, Q06 |
| K02 | An integration dependency downgrades MCP or cached discovery is mistaken for peer evidence. | Protocol compatibility is claimed but unavailable. | The SDK review found a concrete adapter constraint conflict and local discovery placeholder. Pin compatible versions, require real discovery and complete CP01–CP07. Q04 |
| K03 | A serialized scheduler blocks nested callbacks. | Agent waits for a model call that the platform cannot serve. | Separate admission from active-call waiting; verify QA04 and nested-call scenario. Q05 |
| K04 | Usage arrives after cancellation, restart, or month change. | Under-counting or releasing reserved funds too early. | Review the accounting policy and ADR 0011: immutable admission periods, retained ambiguous obligations and idempotent settlement. Q07–Q09 |
| K05 | A provider cannot bound a charge, or a conservative bound greatly exceeds likely cost. | Unsafe admission or unexpectedly rejected cheap calls. | The initial proposal reserves against published model capacity and maximum applicable rates, subject to explicit provider assumptions. Distinguish reserves from charges, reject unbounded profiles and review any excess. Q04/Q07 |
| K06 | Optional instrumentation is treated as complete internal evidence. | False causal conclusions or claims about unavailable reasoning. | Preserve provenance and missingness; evaluate analyses separately. Q10, Q15 |
| K07 | Generic graphs overload one visual view. | Operators cannot distinguish participants, activations and relationships. | Layered views and projections; select scale and reflow acceptance limits. Q11 |
| K08 | Shared memory defaults leak context across runs. | Experiments become contaminated and permissions are bypassed. | Explicit resource identities/lifetimes; isolate new runs by default. Q05 |
| K09 | Trace payloads grow without retention limits. | Local disk exhaustion or sensitive-data accumulation. | ADR 0011 proposes stopping dispatch on write failure and preserving accounting through retention; payload limits and retention rules remain Q10/Q18. |
| K10 | Variant comparison changes several uncontrolled factors. | Apparent improvement is attributed to the wrong change. | Version task inputs, model settings and evaluators; later define repetitions and comparison rules. Q15 |
| K11 | An II monthly budget is mistaken for a cap on the entire provider account. | Spending by the original executor or other tools is incorrectly assumed to be controlled. | Label budgets as II-only and verify scope with QA17. Q12 is closed; no shared accounting integration. |
| K12 | A broad extension schema accepts a behavior the runtime cannot execute. | Silent fallback changes the experiment. | Validate declared profile and capabilities; reject unsupported configurations before dispatch. Q13 |
| K13 | Standards are named but their checks cannot detect violations. | Professional assurances exceed actual enforcement. | Demonstrate a failing example for each gate; retain implementation evidence. Q14 |
| K14 | An older database backup omits newer provider spending. | Restored balances incorrectly authorize additional calls. | Open restored stores without billable admission until the missing interval is reconciled. ADR 0011, QA25, Q09 |

Estimates for experiment size, payload volume, provider latency, and expected run frequency are not yet known. No horizontal-scaling design or numerical service-level claim has been inferred from the future server goal.
