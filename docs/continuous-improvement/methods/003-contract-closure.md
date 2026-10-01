# M03 — Contract closure before delegation

| Document control    | Value                                                        |
| ------------------- | ------------------------------------------------------------ |
| Method ID           | M03                                                          |
| Status at recording | Approved for C03; application pending                        |
| Approval recorded   | 2026-09-29                                                   |
| Owner               | Cesar Zea                                                    |
| Extends             | [M02](002-phased-sprint.md), retaining its phases and checks |
| Decision            | [P05](../improvement-register.md)                            |

This method does not retrospectively change C02. Its planned application is
recorded in the [C03 plan](../cycles/003-contract-closure/plan.md).

## Preparing assignments

1. Classify each assignment's decisions. Reference established decisions through
   the exact interface, schema, descriptor or document. The coordinator resolves
   outstanding shared decisions before delegating affected work. Internal choices
   remain explicitly at the implementer's discretion.
2. Check each new or changed interaction from both producer and consumer:
   inputs, outputs, required and absent fields, success, errors, responsibilities,
   and installation or configuration when they affect the contract. Update the
   existing single source of truth, avoiding duplicate specifications.
3. Walk through a complete case and relevant failures before development begins.
   At each step, explain who calls, what is sent, what is received and how execution
   continues. If this requires inventing a shared decision, close the affected
   contract first.
4. Provide responsibilities, concrete contracts, necessary references, implementer
   autonomy and acceptance criteria. Check that dependencies are also specified
   sufficiently to complete the assignment.

This check belongs to sprint preparation and is limited to new or changed
interactions. Uncertainties discovered during implementation are reported;
they are not concealed to make the process appear free of clarification requests.

## Evaluation

Classify clarification requests as omitted decisions, ambiguous documentation,
information that was difficult to locate, or unforeseen issues. Record what was
missing, how it was resolved and associated rework when observable.
Progress reports and deliveries do not count as clarification requests.

Compare preparation, clarification, review and correction costs alongside verified
delivery. Distinguish measurements from estimates, elapsed time from cumulative
parallel activity, following the [measurement definitions](../measurement.md).
Fewer messages alone do not demonstrate an improvement.
