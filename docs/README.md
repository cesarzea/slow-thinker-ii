# Documentation

**Status, 2026-10-05:** a new execution core is being built under the
[M07 working method](continuous-improvement/methods/007-validated-journeys.md).
Step 1 (build, run and inspect graphs) is implemented, reviewed by the owner and in
acceptance; the [sprint report](specification/step-1/sprint-report.md) summarizes the
review and the [verification record](specification/step-1/verification.md) lists the
evidence. The [roadmap](specification/roadmap.md) plans the next steps. The
[local development guide](development.md) explains how to run it. The previous
implementation's documentation is [archived](archive/previous-implementation/README.md).

## Reading order

1. [Requirements](specification/requirements.md): purpose, stakeholders and the
   CR01–CR18 requirements.
2. [Step 1 journeys](specification/core-step-1-journeys/README.md): the validated
   user journeys that step 1 delivers.
3. [Step 1 delivery](specification/step-1/README.md): acceptance criteria, modules,
   assignments, verification and the sprint report.
4. [Architecture](architecture/README.md): arc42 description with C4 views,
   runtime scenarios, module boundaries, security and quality scenarios.
5. [Decisions](adr/README.md): the MADR log; records 0015–0023 define the core and
   0024–0026 record the step 1 review; 0027 the project's license.
6. [Contracts](contracts/README.md): graph documents, component declarations,
   execution, component protocol, LLM service, accounting, recording and the
   operator API.
7. [Roadmap](specification/roadmap.md): the approved step and later candidates.
8. [Engineering process improvement](continuous-improvement/README.md): working
   methods, cycle evaluations and decisions.

All maintained documentation is in English. Requirements, decisions, contracts and
implementation evidence are kept separate; a decision's acceptance does not imply
that it is implemented or verified.
