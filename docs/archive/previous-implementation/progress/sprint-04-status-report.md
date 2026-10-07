# Sprint Status Report — S04

| Document control | Value |
| --- | --- |
| Report ID | SPRINT-S04-001 |
| Report version | **0.0.4.1** — V0.0, Sprint 4, Revision 1 |
| Owner | Cesar Zea |
| Reporting date | 2026-10-02, Europe/Lisbon |
| Scope | Provider-neutral model resources and a second provider |
| Delivery status | Locally verified, including actual provider execution |
| Publication status | Delivery preparation; hosted checks and owner review pending |

This is a development checkpoint, not a product release. Package versions remain
Python `0.1.0.dev1` and frontend `0.1.0-dev.1`.

## Delivered outcome

Agents can independently select OpenAI or DeepSeek model profiles through the
same mediated model-resource contract. ModelProvider supplies provider adapters;
LLMCall and familiar OpenAI/LangChain clients retain the platform's authority,
deadlines, evidence and accounting path. Supported reasoning options are explicit;
unsupported requests fail before paid dispatch. Native responses, available
reasoning, usage and provider identities are retained without automatic retries.

DeepSeek's reviewed direct pricing source refreshes independently once per day,
alongside the existing Vercel OpenAI catalogue. Immutable snapshots freeze source
digests, billing identity and rates. Conservative reservations and cache/time-band
reconciliation preserve unresolved exposure when usage or timing is ambiguous.
Old OpenAI installations and historical runs remain compatible.

## Acceptance evidence

The [delivery block](../specification/s04-s06-delivery.md) defines A01–A07 and A22;
the [model contract](../contracts/model-resources.md) defines the public boundaries.
Model, tariff and preparation tests cover native request mapping, ordinary clients,
independent grants, reasoning rejection, exact cache/calendar costs, source failures
and retained snapshots. Both providers completed the
[actual collaboration demonstration](s04-s06-live-validation.md).

The complete shared `make verify` passed: **2,204 Python tests, 340 frontend tests
and 20 browser journeys**, plus static, build, CodeQL, accounting mutation and
independent coverage gates. Python line/branch coverage is **97.57% / 92.62%**;
frontend line/branch coverage is **99.37% / 93.63%**. The
[verification record](../verification.md#provider-resource-and-workspace-delivery--2026-10-02)
records the full results and corrections.

## Boundaries and next checkpoint

Only the reviewed provider profiles and capabilities are supported. Arbitrary
provider compatibility, general reliability and model-quality improvement are not
claimed. Adding an adapter requires its own reviewed billing and request policy.
Hosted checks and explicit owner review remain separate from local acceptance.
The [S05 report](sprint-05-status-report.md) records resource extensibility;
[S06](sprint-06-status-report.md) records the product workspace.
