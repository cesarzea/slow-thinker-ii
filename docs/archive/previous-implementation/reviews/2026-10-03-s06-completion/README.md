# S06 whole-interface review

Owner: Cesar Zea. Review date: 2026-10-03. Scope:
[S06-UI-COMPLETE](../../specification/s06-ui-completion.md).
Status: locally verified; owner usability acceptance pending.

## Evidence boundary

The captures below show the actual application. They are not generated design
images. The isolated demonstration uses production HTTP/SQLite services and
installed component processes through MCP. Its deterministic local model produces
illustrative answers and accounting; it makes no paid provider calls. The banner
states that distinction. User accounts and credits remain labeled previews.

The original owner draft remains separate and unchanged. A named demonstration
experiment is created through the ordinary template and settings forms; existing
immutable templates are retained.

## Product observations

| Area                   | Reviewed behavior                                                                                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Collection             | Readable rows, search, template/import/variant actions, truthful counts and state; details are progressive.                                               |
| Design                 | Agent-focused canvas, entry/final/feedback routes, toolbar actions, adjacent selection; no appended technical panels.                                     |
| Configuration          | Independently collapsible Prompt/Model/Response/Components/Connected resources/Advanced groups; child configuration and prompt expansion.                 |
| Composition            | Reviewer contains an LLMCall worker and a Redirector; output names and installed selector are editable in its inspector.                                  |
| Resources and settings | Actual consumers, internal/shared placement, typed configuration, experiment/global scope and scoped budget/deadline units.                               |
| Versions               | Saved immutable identity, note and lineage; comparison retains the actual source values. First-save automatic refresh received a regression correction.   |
| Runs                   | Saved session/task, admitted graph, readable accepted result, nearby evidence and explicit raw details. Actual local run completed with four activations. |
| Narrow layout          | Measured 390 CSS pixels with no document horizontal overflow; selected inspector provides Back to graph.                                                  |

Actual runtime evidence records 17 mediated calls, including two nested worker
and two Redirector calls. All seven owned processes were reaped and all four
synthetic usage receipts settled. The first fixture run's unresolved usage remains
preserved and visible: [sanitized record](../../evidence/s06-ui-completion-local-run-20261003.json).

## Captures

- [Experiment collection](experiments.png)
- [Composed reviewer and internal Redirector](composed-agent.png)
- [Selected inspector at 390 CSS pixels](narrow-inspector.png)
- [Experiment resources and actual consumers](resources.png)
- [Saved version and lineage](versions.png)
- [Completed local-model collaboration](completed-run.png)
- [Redirector response beside the complete graph](redirector-evidence.png)

The desktop viewport measured 1422 by 800 CSS pixels; the narrow viewport measured
390 CSS pixels wide, with no document horizontal overflow in either observation.
Browser zoom can change screenshot pixel dimensions. Automated journeys separately exercise keyboard,
selection, recovery and narrow layout. The
[formal verification record](../../evidence/s06-ui-completion-verification-20261003.json)
identifies the passing unchanged runner result; screenshots do not replace tests.
