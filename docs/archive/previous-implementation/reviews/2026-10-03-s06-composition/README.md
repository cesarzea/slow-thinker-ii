# S06 configurable composition — delivery review

| Document control | Value |
| --- | --- |
| Owner / date | Cesar Zea / 2026-10-03 |
| Scope | [S06-COMPOSITION / 1](../../specification/s06-composition-and-dialogs.md), C01–C14 |
| Status | Installed manual workflows verified; unchanged whole verification pending |
| Acceptance | Owner usability acceptance is separate from local verification |

## Actual workflow evidence

The ordinary interface created a two-agent experiment, attached a Redirector to
the Reviewer, resolved accept/revise destinations, saved an immutable revision and
executed the feedback loop. Both agents remain LLMCall in the graph. No special
Reviewer implementation or platform form was added.

The subsequent revision attaches an independently packaged response-marker to
the Proposer. Its package declares Prefix configuration, summary and attachment
semantics. The platform renders those declarations generically; the recorded result
contains `Recorded externally: ` from the configured component.

| Case | Recorded execution | Calls / processes | Accounting |
| --- | --- | --- | --- |
| Ordinary Proposer + Redirector | `765817c3124e428993ea51587ba85d3c`; one activation | 6 / 5, all reaped | USD 0.0000027 illustrative; zero pending |
| Ordinary Reviewer + Redirector | `26cb9f9c87bb456ea55e239f4ccb9607`; next → revise → next → accept | 17 / 7, all reaped | USD 0.0000108 illustrative; zero pending |
| External marker + Reviewer loop | `f5917c2601fa4c4f83f200c51fa8ce61`; same four activations | 21 / 9, all reaped | USD 0.0000108 illustrative; zero pending |

The [sanitized runtime evidence](../../evidence/s06-composition-local-runs-20261003.json)
retains call ancestry, targets, ports, usage settlement, owned-process cleanup,
definition hashes and recorded marker outputs. HTTP, SQLite, installed processes
and mediated MCP are real. Model responses and usage are a deterministic local
upstream. **No new paid-provider calls or answer-quality validation are claimed.**

## Actual interface captures

- [Read-only composed-agent inspector](composed-agent-summary.png): configuration
  summaries and Configure/Replace/Remove actions, with agent-focused flow.
- [Component-declared concept dialog](external-component-dialog.png): visible Prefix
  label, small inline expand control and separate Apply/Cancel actions.
- [Attachment preview](external-attachment-preview.png): explicit integration,
  routing effects and functional permission approval.
- [Completed Reviewer loop](reviewer-run.png) and
  [completed external-component loop](external-component-run.png): actual result,
  settled cost, activation counts and retained execution history.
- [Earlier hidden-label capture](external-component-dialog-before-label-fix.png):
  preserved failed visual checkpoint, not the final dialog.

These are screenshots of the application, not generated design references. The
read-only inspector was scrolled to its Components section for the first capture.
The desktop viewport is 1,422 × 800 CSS pixels. Captures establish these observed
states; they do not replace accessibility, narrow-layout or lifecycle tests.

## Acceptance-to-evidence map

| Criteria | Implementation boundary / evidence |
| --- | --- |
| C01–C04 | Generic composition planner and independently packaged ComposedCall; explicit routes, bounded conversion, current-worker restoration and consecutive nested lifecycle cases. |
| C05 | Component/resource connection forms, explicit grants, actual consumer labels and retained private/shared resource checks. |
| C06–C08 | Component-owned summaries/concept dialogs, complete bundled field controls, inline Prompt expansion, local Apply/Cancel buffers and untouched required-schema default regression. |
| C09–C11 | Package-owned presentation/attachment metadata, selected immutable installation, external marker configuration/execution and hidden functional worker identities. |
| C12 | Retained navigation/history tests, exact-source numeric cases and restored original unsaved draft with matching byte count/hash. |
| C13 | Three installed manual workflows above; earlier failures retained and classified in C11. |
| C14 | Unchanged complete local runner remains pending; scoped tests do not close it. |

Individual receipts are maintained with the
[workspace application](../../../../../backend/src/slow_thinker_ii/application/workspace/specification.md),
[shared API](../../../../../frontend/src/api/specification.md),
[shared UI](../../../../../frontend/src/ui/specification.md),
[product workspace](../../../../../frontend/src/features/workspace/specification.md) and
[composer](../../../../../components/composed-call/source-review.md).

## Preserved state and boundaries

The owner's original unsaved draft was restored in a separate tab. Its 1,746 bytes
and SHA-256 match the backup; its existing missing-permission issue was preserved.
No revision was saved for that draft. Original paid setup and historical runs were
not rewritten. An environment interruption closed the original tab; its survival
is not claimed.

Legacy wrappers without reversible journals remain Configure-only, with a reason.
Finite sequence and bounded conditional profiles remain supported. Account/credit
figures are previews; evaluation, real accounts, internal graph editing and new
execution profiles are outside this delivery. No commit, push or publication was
performed. The [status report](../../progress/sprint-06-status-report.md) and
[C11 record](../../../../continuous-improvement/cycles/011-s06-composition-and-dialogs/report.md)
separate observed verification, owner acceptance and process conclusions.
