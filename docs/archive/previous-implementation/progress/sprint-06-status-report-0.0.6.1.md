# Sprint Status Report — S06

| Document control | Value |
| --- | --- |
| Report ID | SPRINT-S06-001 |
| Report version | **0.0.6.1** — V0.0, Sprint 6, Revision 1 |
| Owner | Cesar Zea |
| Reporting date | 2026-10-02, Europe/Lisbon |
| Scope | Product configuration and execution workspace |
| Delivery status | Locally verified; owner interface review pending |
| Publication status | Delivery preparation; hosted checks and owner review pending |

This is a development checkpoint, not a stable product release. The
[central version register](../../../../CHANGELOG.md) distinguishes report and package versions.

## Delivered outcome

The application now provides Experiments, Components, Resources, Runs and Settings
navigation. Discovered schemas drive component forms, with model/reasoning choices,
managed children and resource bindings. Supported graph forms configure nodes,
sequence order, conditional routes, inputs, permissions and activation limits.
Expert JSON editing remains available for unsupported schema constructs.

Forms and JSON use the same source and server validation. Patches preserve unrelated
configuration and exact numbers. Saved revisions and variants remain immutable;
earlier run definitions, results and canvases survive later edits. Runs expose
execution controls, results, costs and optional evidence. Settings apply bounded
deadlines and run/session/month budgets with stale-revision rejection and unchanged
replay after uncertain responses. Credentials remain outside graph definitions.

## Acceptance evidence

The [delivery block](../specification/s04-s06-delivery.md) defines A15–A22;
the [workspace contract](../contracts/product-workspace.md) and
[usage guide](../workspace.md) explain the supported interactions.
Browser journeys exercise actual application HTTP/SQLite authoring, component/model
configuration, exact revision execution, historical canvas retention, settings
recovery, disconnection and narrow-viewport behavior. Their inference workers are
deterministic test fixtures. Separately, the
[live demonstration](s04-s06-live-validation.md) uses actual providers and resources
through the production authoring and execution APIs.

The complete shared runner passed **2,204 Python tests, 340 frontend tests and
20 browser journeys**. Frontend coverage is **99.37% lines, 93.63% branches,
99.12% functions and 98.64% statements**. CodeQL and all other mandatory gates
passed; the [verification record](../verification.md#provider-resource-and-workspace-delivery--2026-10-02)
retains reviewed findings and correction history.

## Limitations and review checkpoint

Forms cover the current supported control profiles; full graphical authoring,
prompt-based creation and evaluation/comparison remain later sprints. SQLite v7
retains prior runs and records settings commands transactionally.
Manual inspection of the existing live operator session remains pending: automatic
approval review rejected temporary credential replacement without explicit owner
authorization. The original credential was retained. This does not invalidate the
completed automated browser journeys or the actual provider/resource executions.
Hosted checks and explicit owner review remain separate publication requirements.
