# Verification record

**Updated: 2026-10-02. S04–S06 passed the complete shared local verification runner and actual two-provider resource execution.** Dated sections retain earlier evidence.

## Provider, resource and workspace delivery — 2026-10-02

The owner activated the [S04–S06 delivery block](specification/s04-s06-delivery.md)
with DeepSeek Flash, a deterministic calculator and private/shared key/value memory.
After reviewed corrections, the complete configured `make verify` finished with
exit 0. The [sanitized summary](evidence/s04-s06-verification-20261002.json)
retains counts, coverage numerators, mutation results and the retained log digest.

| Mandatory check | Result |
| --- | --- |
| Source limits, Ruff, strict Pyright/Mypy, Vulture and Import Linter | Passed; 36 import contracts kept, no broken contracts |
| TypeScript, ESLint, Prettier, dependency-cruiser and Knip | Passed; no type/boundary/unused-code gate relaxed |
| Python/component/example/tooling tests | 2,204 passed in 258.29 seconds |
| Frontend component/API tests | 340 passed across 50 files |
| Browser journeys through production HTTP/SQLite | 20 passed in 1.4 minutes |
| Python independent coverage | 97.57% lines (10,649/10,914); 92.62% branches (2,599/2,806) |
| Frontend independent coverage | 99.37% lines; 93.63% branches; 99.12% functions; 98.64% statements |
| Pinned local CodeQL, Python and JavaScript/TypeScript | No errors or warnings; 97 reviewed Python notes, no JavaScript/TypeScript findings |
| Production build | Passed |
| Accounting mutation baseline | 141 killed, one timeout, 58 survivors; command completed |

Provider tests use ordinary OpenAI/LangChain clients and real loopback mediation,
authority, hosts and price policies with simulated native transport. They cover
provider selection, reasoning options/rejection, cache usage, UTC pricing windows,
reviewed calendar exclusions, exact rounding, immutable source snapshots, refresh
failure and historical compatibility. Required tests make no paid requests.

Resource tests build and install external packages offline, launch real subprocess
MCP hosts and exercise calculator bounds, private namespaces, shared persistent
state, run-local reset, version/CAS/ABA behavior and managed ordinary/routed workers.
Permission, cancellation, budget and nested failure paths retain their evidence.
Workspace tests cover source-preserving patches, strict discovery/HTTP boundaries,
transactional limit commands, replay/conflicts and SQLite v7 migration. Existing
history remains readable. Browser journeys configure components/graphs, save and
execute exact revisions, retain historical canvases, recover uncertain settings
and disconnections, and verify narrow-viewport behavior using deterministic workers.

Whole-system review/testing corrected UTF-8 patch handling, hidden execution
feedback, run-panel remounting and form overflow. Actual installed startup also
exposed an unnecessary outgoing MCP binding on resource-only hosts before any paid
call; public preparation regressions and both subsequent real runs pass.
Three earlier full-runner attempts stopped at formatting, unsupported Node 23 and
CodeQL respectively. The fourth passed under the existing Node 24 environment. Final configuration
audit then found an accidental additional-importer exemption on the derived example.
It was removed; a real negative probe demonstrated acceptance before correction
and rejection afterward. All 14 boundary probes and a fifth complete runner passed
on the corrected configuration.
The [C06 evaluation](continuous-improvement/cycles/006-provider-resource-workspace/report.md)
classifies production, fixture, environment and command defects separately.

Vulture's unchanged 60% scan uses two exact inherited HTMLParser callback references
for framework-dispatch false positives; strict override signatures and actual
parser tests establish their use. No file exclusion or broad name pattern was added.
CodeQL notes comprise protocol/completion declarations, deliberate dual imports
and exhaustive calculator pattern matching; each match has an explicit rejecting
default. No finding was suppressed. Mutation survivors retain the pre-existing
baseline meaning and are not claimed as killed.

The [live validation](progress/s04-s06-live-validation.md) separately records two
actual OpenAI/DeepSeek executions with installed external workers, calculator,
shared durable memory and exact proposal provenance. Their native usage reconciles
to USD 0.000520600 together, with no unresolved charge and unchanged prior results.
Total preceding/current authorized demonstrations remain USD 0.002651950 of USD 3.
Manual live-session UI inspection awaits credential authorization; the original
operator key was preserved. Automated browser acceptance and actual production
execution are complete. Owner review and hosted verification remain separate.

## Personal experiment live execution — 2026-10-02

At the owner's request, the browser created and saved a personal conditional
proposer/reviewer graph and executed an offline Git workshop task with real
OpenAI responses. The run completed with three rounds, six paid model calls,
25 mediated calls and confirmed cleanup. Recorded cost was USD 0.001177650;
the existing USD 3 run/session/month caps remained enforced.

Independent recording checks confirmed the exact saved definition, unchanged
feedback and previous-proposal inputs, source activation bindings, final schedule,
provider request IDs and usage-based cost reconciliation. The reviewer also
produced an apparently unnecessary second rejection, retained as model-quality
evidence. The [live validation report](progress/sprint-03-live-validation.md) and
[sanitized summary](evidence/s03-live-execution-20261002.json) distinguish these
observations from the earlier simulated tests. One run does not establish general
reviewer reliability or a comparative improvement. No product source was changed.

## Personal experiment delivery — 2026-10-02

The [S03 delivery specification](specification/personal-experiments-sprint.md)
and [status report](progress/sprint-03-status-report.md) identify the delivered
personal JSON authoring scope. After reviewed corrections, the complete configured
`make verify` runner finished with exit 0 at the observed 00:08:38 UTC checkpoint.

| Mandatory check                                                              | Recorded result                                                                     |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Physical source limits, Ruff, strict Pyright/Mypy, Vulture and Import Linter | Passed; 27 import contracts and real deliberate boundary violations remain enforced |
| TypeScript, ESLint, Prettier, dependency-cruiser and Knip                    | Passed; no boundary or unused-code exemptions added                                 |
| Python/component/tooling tests                                               | 1,724 passed in 247.79 seconds                                                      |
| Frontend component/API tests                                                 | 259 passed across 39 files                                                          |
| Browser journeys through real HTTP/SQLite                                    | 15 passed in 56.9 seconds                                                           |
| Python coverage                                                              | 97.21% lines; 91.61% branches; 96.11% combined                                      |
| Frontend coverage                                                            | 98.66% statements; 93.48% branches; 99.15% functions; 99.27% lines                  |
| Pinned local CodeQL, Python and JavaScript/TypeScript                        | No errors or warnings; 90 Python notes and no JavaScript notes                      |
| Frontend production build                                                    | Passed                                                                              |
| Accounting mutation execution and independent coverage gates                 | Completed successfully; surviving baseline mutants are not claimed as killed        |

Library/SQLite tests establish canonical numeric fidelity, atomic concurrent replay
and conflicts, exact identities, known parent lineage and fixed signed listing windows.
HTTP/client tests cover operator authorization, viewer write absence, bounded
requests/responses, safe complete diagnostics and uncertain insertion outcomes.
Real v5-to-v6 migrations preserve prior tables, verified backups and rollback behavior.

Production preparation executes a saved personal graph's real program/policy with
the actual Sequence process and LLMCall, using explicitly simulated runtime ports
and transport. Recorded native SDK instructions, input, model alias and output-token
settings establish the admitted configuration and mediated charge. A later revision
leaves the earlier snapshot, result and call evidence unchanged. This is independent
of browser fixtures and does not claim synthetic manifest packages launch inference.

Browser journeys establish raw import/edit/save/reload, exact two-revision selection,
manual new-ID variant execution, dirty/pending/stale/uncertain-state recovery and
retained inspection. Historical checks require a rendered proposer canvas and
recorded activation. The isolated GUI demonstration saved `s03-demo · v1`, completed
a simulated execution and retained its graph/result after changed instructions were
saved as `v2`. Fixture accounting is simulated; no provider traffic or charge occurred.

Whole-system review corrected raw authoring fidelity and post-save editor state.
Testing corrected boolean schema handling, the shared public import policy, test
exports/collection, a CodeQL fixture expression and browser visibility/evidence
assumptions. The [C05 evaluation](continuous-improvement/cycles/005-personal-experiments/report.md)
classifies these failures; five earlier runner attempts stopped before complete
acceptance. The successful sixth attempt retains the original gates and environment.

Ten new Python CodeQL notes are deliberate typing.Protocol method ellipses; the
previous 80 reviewed notes remain. No suppression or severity policy was changed.
Hosted verification and owner review/merge authorization remain separate publication
requirements. These results establish local delivery, not a stable product release.

The existing local application was then restarted with its unchanged execution
configuration. Its database migrated from v5 to v6 with verified backups and passed
integrity checks. All three completed runs, 33 calls, prior event/result content and
spending records were retained; restart recovery appended two cleanup events without
replacing historical evidence. The authenticated library responds successfully and
the existing monthly cap remains USD 3. No new model execution was initiated.

## Browser geometry readiness follow-up — 2026-10-01

Commit `a72e2a6339bb8deab7bf12afab5f60960bc9644e` passed the corrected polling
journey remotely. [CI run 36887588522](https://github.com/cesarzea/slow-thinker-ii/actions/runs/36887588522)
instead failed the narrow-viewport geometry case with a null card bounding box;
the other nine journeys passed. Shared CodeQL, 1,421 Python tests, 154 frontend
tests and the build passed before that failure.

Review identified readiness gaps in the geometry helper: an empty collection
satisfied `every`, and hidden initialization was not rejected. Graph definition
arrival and reorganization remount the canvas. The corrected helper samples the
canvas and exactly two visible, positive-size cards in one DOM evaluation, refusing
incomplete samples. Separation is checked with condition polling over complete
samples. The original containment, strict non-overlap, delayed-definition,
reciprocal-route, configuration, marker and narrow-overflow conditions are retained.
Only the journey and its contract changed; retries, delays, timeouts and product
behavior remain unchanged.

After coordinator review, the narrow representative passed and both geometry cases
passed ten repetitions each: 20 cases in 18.4 seconds. The full unchanged local
`make verify` then passed, including CodeQL, 1,421 Python tests, 154 frontend tests,
all ten browser journeys, build, static, mutation and independent coverage checks.
Coverage and the retained mutation baseline are unchanged from the preceding
checkpoint; CodeQL has no errors or warnings, 80 reviewed Python notes and no
JavaScript/TypeScript findings. All calls used offline fixtures.

Remote verification of this geometry correction is pending at document preparation.
The preceding failed run remains evidence of an escaped test defect, not a full
remote pass. Branch protection and owner sign-off remain unchanged.

## Browser polling regression and publication follow-up — 2026-10-01

The published commit `d4581837016f33011c85c9cf08df312f2807ab48` passed local
verification, but [GitHub CI run 36881892848](https://github.com/cesarzea/slow-thinker-ii/actions/runs/36881892848)
failed the saved-run polling journey; the other nine browser cases passed. Both
native CodeQL jobs and the title check passed. The failing assertion compared
the node's complete inline style after layout reset.

Temporary instrumentation showed that four passing local repetitions had not
moved the node: its card was below the viewport when raw mouse input was sent.
Adding a visibility assertion after reset reproduced the CI failure in four
repetitions. Transient visibility styles could satisfy the earlier comparison
without proving movement. Instrumentation was removed before correction.

The corrected journey scrolls the card into view, requires an actual change in
its computed transform, verifies node and camera transforms across a successful
execution poll, and requires layout reset to restore the initial node transform.
Only the browser test and its module contract changed; no product defect was
established, and no retries, fixed delays, timeouts or gates were relaxed.

The representative corrected case passed, then ten focused repetitions passed
in 32.7 seconds. The unchanged full `make verify` runner subsequently passed:
1,421 Python tests, 154 frontend tests, all ten browser journeys, static checks,
production build, accounting mutations and independent coverage checks. Python
combined coverage remains 95.86%; frontend statement/branch/function/line coverage
remains 98.34%/92.89%/99.12%/99.23%. CodeQL retains the reviewed 80 Python notes,
with no errors or warnings, and no JavaScript/TypeScript findings. The configured
mutation baseline remains 141 killed, one timeout and 58 survivors.

These checks used offline provider fixtures and made no paid model call. The
earlier passing journey counts remain historical results; they did not establish
the intended drag behavior. Remote validation of this correction is pending at
document preparation. Main-branch protection remains unchanged; no merge or owner
sign-off is claimed.

## Shared CodeQL verification and commit readiness — 2026-10-01

Integrated the [CodeQL package](../tooling/quality/codeql/specification.md) into
`make verify` before functional tests. Local execution and both CI workflows read
the same bundle policy: CLI 2.27.1, Python queries 1.8.11 and JavaScript queries
2.4.6. CI passes the SHA-pinned action's public CLI path to the shared runner;
the independent native CodeQL matrix is retained. Remote execution of these
workflow changes has not been performed.

The public-contract tests cover current Git source, privacy exclusions, tooling,
SARIF validation, findings and extraction completeness: 155 passed, with 99.50%
line and 98.61% branch coverage of the new package. A real negative `make verify`
probe using the [documented subprocess assertion](https://codeql.github.com/codeql-query-help/python/py-side-effect-in-assert/)
failed on `py/side-effect-in-assert`; its temporary source was removed. An earlier
probe stopped at document formatting, and the initial 2048 MB JavaScript analysis
failed with an exhausted Java heap. Formatting was corrected and RAM raised to
4096 MB, retaining two threads, complete suites and all rejection criteria. The
affected resource test passed after the adjustment.

The final uninterrupted `make verify` passed all configured commands: source-size,
lint, format, types, imports, module boundaries, dead code, CodeQL, 1,421 Python
tests, 154 frontend tests, production build, ten browser journeys, accounting
mutations and the independent coverage gate. Python combined coverage is 95.86%;
line coverage is 7,828/8,071 and branch coverage is 1,776/1,948, each above 90%.
Frontend statement/branch/function/line coverage remains
98.34%/92.89%/99.12%/99.23%. The mutation command completed with the existing
baseline: 141 killed, one timeout and 58 survivors; this is not a claim that every
mutant was killed.

Both CodeQL analyses completed with zero errors and warnings. Python retains 80
reviewed notes: 66 `Protocol` declaration bodies, ten awaited completion/exception
statements and four dual import forms. JavaScript/TypeScript has no findings.
The working-tree snapshot differs from the earlier index checkpoint; earlier
counts remain historical evidence. No rule, source finding or note was suppressed.
Reports and logs are retained in ignored local storage; snapshots/databases were
removed. No paid provider call was made. Local commit readiness is established;
remote CI success and release approval remain separate.

## Commit preparation and local security analysis — 2026-10-01

Reviewed the pending agent-canvas, English-interface and documentation changes.
Excluded IDE files, credentials, local execution data and the additional host lock
from the index. Corrected outdated current-status wording without deleting earlier
verification checkpoints. Recorded process CSV bytes are preserved by Git attributes;
all 31 current provenance hashes match the staged files.

The shared local quality runner completed through a stopped/resumed sequence.
Its first run passed static checks and stopped because the restricted environment
prevented the dead-code tool from opening a loopback port. Resuming that runner
with loopback permission and the Makefile environment passed dead-code checks,
1,266 Python tests, 154 frontend tests, the production build, ten browser journeys,
accounting mutations and the independent coverage gate. Combined Python coverage
was 95.66%; frontend statement/branch/function/line coverage was
98.34%/92.89%/99.12%/99.23%. No paid model call was made.

Installed the official CodeQL 2.27.1 macOS bundle in ignored local storage and
verified its published SHA-256. An initial extraction failed because the tool cache
inherited the application's ES-module package setting; an isolated CommonJS package
boundary in that cache resolved it without modifying CodeQL or application sources.
The `security-and-quality` suites analyzed an index snapshot containing first-party
source only: 499 Python files and 128 JavaScript/TypeScript files, plus four workflow
files. Both analyses completed without execution errors; no finding was suppressed.

JavaScript/TypeScript reported no findings. Python reported nine errors for cleanup
operations inside assertions, one warning for unnecessary local-variable deletion
and 82 notes. All findings were in files unchanged by the prepared delivery.
They are retained findings, not a passing security result. A concrete cleanup patch
for the nine assertions and one warning is prepared for owner review; it has not
been applied. The remaining notes and shared-entry-point parity also require review
before claiming complete M05 publication readiness. No commit or push was performed
at that checkpoint.

## Approved CodeQL cleanup — 2026-10-01

The owner approved the concrete ten-file cleanup patch. Nine test cleanup calls
now execute before their assertions, so optimized Python cannot remove process or
coordinator cleanup. The default LLMCall validation hook explicitly returns `None`
instead of deleting unused local parameters; its public behavior is unchanged.

All 705 integration and LLMCall tests passed, as did five installed-coordinator
checks using the existing seven-component immutable bundle and simulated provider
traffic. The installed checks cover four completed graph profiles and cancellation;
they do not claim a new component installation. Source-size rules, Ruff checks,
formatting, Pyright and mypy passed. No provider credential or paid call was needed.

The complete Python `security-and-quality` suite was rerun against the corrected
index snapshot. It reports zero errors, zero warnings and 82 retained notes:
67 `Protocol` declarations, 11 awaited-task statements whose completion or raised
exception is observed, and four imports using both module and symbol forms.
Those notes were reviewed; no rule, result or source location was suppressed.
The earlier JavaScript/TypeScript analysis remains applicable because its source
is unchanged. Frontend, browser, coverage and mutation evidence remains at the
preceding full-run checkpoint; those unaffected checks were not repeated here.

Local CodeQL analysis is now recorded, but it remains a separate invocation rather
than part of the shared verification entry point. That M05 integration obligation
remains open before publication; this record does not claim complete local/CI parity,
remote CI success or release approval.

## Engineering process improvement documentation — 2026-09-30

Integrated the [formal English process record](continuous-improvement/README.md)
into project documentation, retaining M01–M05, C01–C03, approval history and
measurement limitations. Former external document locations now redirect to it;
original source wording is preserved in a local archive.

Checked relative links, English labels and document formatting. Compared all five
CSV datasets and three structured result/observation records with their preserved
sources: only labels changed; numeric values, timestamps, identifiers and row order
were retained. C01/C02 accounting totals reconcile. The provenance manifest retains
historical checksum claims separately from verified migration hashes.

This verification covers documentation integrity. Product tests were not repeated
and it does not extend the delivery or productivity claims of the recorded cycles.

## Agent input/output correction — 2026-09-30

Agent cards now show their input/output connectors and an incoming arrow at the
declared entry step. Exterior arrows remain horizontal after expansion and
dragging. Invisible boundary anchors add no visible platform nodes. Saved
controller configuration takes precedence; unsupported or invalid entry metadata
does not create an invented entry.

All 154 frontend unit tests passed. Coverage: 98.34% statements, 92.89% branches,
99.12% functions and 99.23% lines. Frontend typing, ESLint, formatting, dependency
boundaries, dead-code checks and the production build passed. The dead-code check
initially lacked loopback permission while loading the browser configuration; it
passed when rerun with that permission. No source exception was added.

All ten browser journeys passed before a node-handling correction. The new drag
journey exposed React Flow initialization warnings despite passing its assertions.
Controlled nodes now consume dimension/position changes and retain measurements.
The connector/drag and polling journeys passed again with no initialization
warning or ResizeObserver notification; the connector regression now explicitly
rejects the initialization warning. The two geometry/narrow-viewport journeys
also passed again after that correction. Live visual inspection confirmed the
single-agent and bounded-review entry/exit routes without a paid model call.

Backend/Python checks and accounting mutations were not repeated for this frontend
correction. No commit, push, remote CI or local CodeQL run was performed.

## Agent canvas and English presentation — 2026-09-30

The canvas now displays agent-step cards and declared routes. Configuration and
system markers are optional; resources and exact activation/call evidence remain
below the canvas. Product-authored UI, accessible labels and client errors are
English. User-authored content and historical evidence retain their original text.
Saved-run model configuration takes precedence over illustrative definitions.

Verification passed with 1,266 Python tests, 139 frontend tests and nine browser
journeys. Python coverage: 96.86% lines, 90.58% branches. Frontend coverage: 98.27%
statements, 92.65% branches, 99.09% functions and 99.20% lines. Static typing,
formatting, lint, 26 Python import contracts, frontend module boundaries, dead-code
checks, source-size rules and the production build passed. Accounting mutation
results retain the reviewed baseline: 141 killed, one timeout and 58 survivors.
No gate or coverage threshold was weakened.

The local verification command stopped first on translated-fixture formatting,
then on an unused private-helper export. Both were corrected. Remaining commands
from the same verification runner were resumed without repeating completed Python
checks. The first browser continuation omitted Makefile's browser-cache environment
and could not launch Chromium; rerunning with the repository cache launched all
journeys. Eight passed; one test incorrectly expected only the two model resources.
The router is also a resource. Its corrected journey now asserts all three resource
identities; both journeys in that file passed on the focused rerun. This is combined
local gate evidence, not a claim of one uninterrupted `make verify` success.

Browser checks cover all five bundled graphs, single-agent presentation, expanded
configuration, system markers, reciprocal routes, narrow viewports, position and
viewport retention during real polling, reviewer feedback and exact keyboard
inspection. A separate live-browser review read an existing saved execution and
confirmed its actual model/effort metadata. No paid provider call was made.

No commit, push or remote CI run was performed for this delivery. CodeQL was not
run locally; its publication prerequisite remains outstanding. Marker hover/click
inspection is intentionally future work, as agreed in the
[approved sprint](specification/agent-canvas-sprint.md).

## First-cycle delivery

Five bundled graphs execute locally, including bounded proposer–reviewer feedback.
Redirector runs a packaged synchronous Python selector; RoutedCall composes an
ordinary worker and redirector through authenticated MCP. BoundedFlow retains
separate activation identities and declared routes, including terminal acceptance
and exhaustion. The UI shows exact definitions, optional internals, distinct
relationship layers, live execution and linked evidence.

The installed acceptance suite passed all 19 checks against seven independently
prepared, hash-pinned production environments. A separate installed selector check
also passed: a nonterminating selector that ignores termination reaches its deadline,
is forcibly reaped and leaves confirmed ownership records and safe diagnostics.
Accepted feedback takes four activations; exhaustion stops at six without scheduling
a seventh. Settled charges and outstanding obligations remain inspectable.

`make verify` passed with 1,266 Python/tooling/component tests, 119 frontend tests
and seven browser journeys. Python line coverage is 96.86% and independent branch
coverage is 90.58%; frontend coverage is 98.28% statements, 92.51% branches,
99.05% functions and 98.87% lines. All 26 Python import contracts and the configured
size, typing, lint, format, dependency, dead-code and build checks pass. The 200
accounting mutations retain the reviewed baseline: 141 killed, one timeout and
58 survivors. An earlier full run correctly rejected 89.19% Python branch coverage;
18 additional composition/validation acceptance tests covered 25 missing branches.
No threshold or source exclusion was weakened to close that gap. Dependencies and
generated environments are excluded from source analysis, including nested virtual
environments; first-party source remains subject to every gate.

The follow-up CodeQL review moved resource cleanup outside test assertions and
made the new protocol methods explicitly abstract. Targeted tests, both installed
bounded paths and the complete local gate pass after those corrections. Remote
CodeQL reports no new alerts on the corrected source; no alert was suppressed.

The gateway tests exercise permission-filtered MCP discovery, ordinary OpenAI and
LangChain model invocation, a LangGraph node using a StructuredTool, preserved
parent/activation identity, rejected authority, optional redacted reports, deadlines
and no automatic retries. SQLite v5 tests cover migration, exact public budgets,
pricing quarantine, durable process ownership and verified restart cleanup.

Two live OpenAI runs used the reviewed low-cost GPT-6 Luna profile. The first was
accepted immediately. The second began with a deliberately incomplete supplied
candidate: the reviewer returned seven findings, all seven were preserved verbatim
in the next proposal's input, and the revised proposal was accepted. Both runs
confirmed cleanup and no outstanding cost. Their settled costs were USD 0.000165500
and USD 0.000353700; including prior live usage, the retained total is USD 0.000953700
against the owner's USD 3 allowance. These are usage-derived ledger amounts at the
retained tariff, not a provider invoice. Credentials and detailed live evidence
remain local and untracked.

The first cycle supports trusted local components and the reviewed OpenAI provider
adapter. It does not claim arbitrary provider conformance, hostile-code sandboxing,
remote OAuth, graph editing, arbitrary dynamic/parallel scheduling, automatic
collaboration analysis or optimization. Optional reasoning is component-reported
evidence; unavailable reasoning is not reconstructed. The frontend production
build has a non-blocking large-chunk warning; no bundle performance target is claimed.

## Historical implementation checkpoints

The following paragraphs describe earlier checkpoints. Their then-pending work and
old counts are historical, not the current delivery status.

`make verify` runs the configured Python/TypeScript type, lint, dependency, dead-code, size, coverage, build and browser checks. SQLite integration cases exercise competing reservations, all three budget scopes, restart persistence, duplicate/conflicting settlements and excess charges. Four browser journeys render the four bundled graphs and exercise saved sessions, Start, final results, reload/history recovery Stop, and linked event/call/activation/payload inspection through the actual backend with simulated operations.

Earlier complete local run: `make verify` exited successfully with 1008 Python/tooling/component tests, 64 frontend tests and four browser journeys. Python line coverage is 97.70% and branch coverage 91.62%; frontend coverage is 98.33% statements, 94.53% branches, 100% functions and 99.45% lines. All 23 Python import contracts passed. The browser tests select available ports independently of development servers. The graph, completed execution screen and call/activation inspectors were visually inspected. These results cover the implemented code, not the outstanding first-cycle capabilities.

The tariff importer downloads Vercel's public catalogue on missing/overdue startup and every 24 hours while the backend runs. It validates the initial OpenAI Standard text profile, stores immutable revisions and retains valid prices after failures. Tests cover cadence, restarts, invalid categories/capacities/bands, download failures, duplicate refresh requests and unchanged historic revisions. The real public endpoint was successfully imported on 2026-09-28 without credentials or model inference.

Budget mutation testing regenerates its test mapping before each full run. The reviewed 200 mutations yielded 141 killed, one timeout, and 58 survivors: 56 change exception diagnostics and two preserve behavior. No mutation lacked tests. This is not a claim of a 100% mutation score or provider invoice verification.

The host SDK and sequence controller are separate Python packages. Real subprocess tests verify MCP discovery, effective schemas, sequential calls, fresh invocation contexts, cancellation, startup deadlines, forced termination, rejection of malformed/oversized messages and verified process exit. The backend owns the launched process handle and rejects reuse after shutdown. Schema snapshots are copied before serving; JSON validation uses an explicit local reference registry. The automated MCP cases use editable development installations. A required invocation metadata field does not yet establish platform authorization.

`make components` builds identified sources into wheels, resolves a production-only hashed lock, fetches its artifacts and installs a fresh environment offline. Publication follows package inventory and class inspection; reuse verifies retained artifacts, lock, runtime inventory and installed files. Installation tests use locally built fixture wheels without network access, including real subclass checks, compatible base updates, rejected major updates, false ancestry, changed code/metadata and preservation of previous resolutions. A separate local check prepared the actual sequence/host packages with 30 production distributions, executed a successful MCP scheduling call, verified clean process exit and confirmed the environment inventory remained unchanged. This is local installation evidence, not release provenance or OS isolation.

`LLMCall` now runs as a separate MCP process and makes one standard OpenAI SDK request per invocation, using a fresh component object and client. Tests cover text/JSON outputs, internal schema references, input/output validation, retained invalid text, refusal/truncation/provider errors, disabled SDK retries, deadline propagation and cleanup. A real loopback HTTP test verifies requests and per-call bearer tokens across the process boundary. The independent `GroundedReview` package inherits the public implementation and rejects citations absent from the supplied sources. Production preparation now covers both packages as well as the controller and model resource; the installed checks below supplement the development-installation suite. The native gateway tests below establish managed mediation to a simulated model resource; the independent upstream resource is exercised below against local HTTP fixtures; live account access remains pending.

The transient call-authority registry now applies the frozen permission map, filters operation discovery, generates per-call identities and grants, rejects busy ancestors and enforces run/parent deadlines plus call/depth bounds. Tests cover receiver-specific permissions, token reuse and cross-registry rejection, concurrent admission for the final call slot, failed completion, parent/child revocation and Stop including already-revoked work still requiring cancellation. Execution occupancy is retained until the call actually finishes. The authority rules are now used by transactional admission; the native HTTP model route and independent provider resource are exercised below; generic outgoing MCP routing and production route composition remain pending.

`RunAdmission` coordinates authority with SQLite: T2 stores the exact request, call context and pricing basis together with reservations in all three scopes; T3 commits a single dispatch authorization and its ledger transition. Stop closes durable admission, releases only never-authorized reservations and preserves uncertain spending. Tests cover failed evidence/dispatch writes, Stop racing dispatch, parent-call prerequisites, budget rejection stopping the run, payload bounds, runtime/deadline checks and recovery without replay. Existing ledger settlement accepts late usage after Stop. Versioned migration retains and validates a prior-schema backup, rolls back injected failure and rejects a concurrent write during backup preparation. These are storage/application-service tests; backend startup now performs this recovery under exclusive store ownership.

T4 now stores native response/usage receipts, settles known charges and commits eligible call results in one transaction. Tests cover identical and conflicting deliveries, missing usage retaining its reservation, late settlement after Stop/recovery, expired deadlines, charge overruns, active children preventing parent publication and an injected write failure rolling back response and money together. Late receipts preserve terminal dispositions and the original result reference. Schema v3 adds receipts; migration refuses unfinished v2 runs until explicit recovery closes them. These receipts come from trusted application callbacks; complete production graph execution and operator inspection routes are not yet wired; the independent provider transport is exercised below.

`ManagedCalls` now connects T2/T3/T4 to operation preparation and async delivery. Tests exercise nested calls without holding database transactions, pre-dispatch rejection/expiry, transport failure, Stop before and after dispatch, deadline expiry, bounded cleanup of cancellation-resistant work and durable dispatch failure. Real MCP subprocess tests retain native responses/errors, settle fixture usage and preserve both response and reservation if pricing reconciliation fails. `ProcessOperation` binds ready connections and propagates the original deadline and refuses transmission after it expires. Task ownership ends only when work finishes; the managed runtime below now owns process startup/teardown.

`ManagedRun` and `ProcessFleet` now own all required readiness checks, nested-capable managed calls, finalization and process teardown. Real two-process tests cover successful work, failed second-host startup, call deadlines, Stop before/during readiness, Stop during work, invalid operation bindings and restart refusal. T5 records final output only without prior Stop, expired run deadline or outstanding calls. Tests cover completion racing Stop, retained first cause, wrong runtime, invalid output, unsent/uncertain obligations and rolled-back final writes. Cleanup observations remain separate from the terminal outcome; injected cleanup failure remains visible after successful work, and failed final recording propagates after resource cleanup without claiming success. Programs in these lifecycle tests are fixtures; the sequence checks below now cover bundled definitions. The native mediation tests below cover a simulated model resource; the independent provider resource is now exercised below; live account access remains pending.

The local POSIX backend now holds a nonblocking kernel lease for the canonical store path before initialization/recovery and throughout its HTTP lifespan. Tests reject a competing backend and a symlink alias, verify lease release after abrupt owner-process exit, and recover retained call records through actual app startup without replay. The lease file is not a PID-based ownership claim and is never unlinked during release. This proves exclusive backend/store ownership and accounting recovery; it does not yet reconcile OS processes orphaned by an earlier backend crash.

`SequenceCompiler` now validates the canonical graph schema, matches supplied instance type/version contracts, checks configured operations/roles/resource permissions, validates known input values and rejects missing or forward references. Strict JSON parsing rejects duplicate keys and nonfinite numbers; JSON Pointer resolution preserves nulls, escapes and array bounds. Plans retain frozen graph/input JSON, the requested limits profile and variant lineage. `SequenceProgram` asks the managed controller for every step and completion, verifies its decisions, binds only declared inputs and stores all node results. Tests execute all four bundled JSON graphs using the actual MCP sequence process and simulated agent operations, including reuse of the proposer with separate inputs. Invalid controller decisions or unavailable outputs prevent downstream calls. Each scheduled node and its nested calls now retain the originating node ID alongside activation/call IDs; existing saved contexts default to no node identity. These checks do not establish resolved installation artifacts, approved provider/limit profiles or live LLM execution.

`NativeModelGateway` now authenticates invocation credentials, resolves model aliases from the caller's frozen bindings and sends requests through ordinary managed child calls. A real OpenAI client crosses the loopback HTTP route, and an independent LLMCall process completes through that route with one simulated model charge. Tests preserve native success fields, provider statuses/bodies/request references, bounded Retry-After metadata and parent/node identities. Invalid scope, duplicate credentials, browser-origin requests, unsupported options and exhausted budgets prevent model invocation. Injected dispatch-recording failure prevents transmission; late results after Stop are charged but not published. The OpenAI request/pricing profile records conservative reservations against immutable tariffs, settles disjoint usage categories and retains uncertain obligations for absent or inconsistent evidence. These tests do not exercise an upstream provider or a paid request.

`components/openai-model` now hosts `complete` in an independent MCP process. The admitted model alias, real model and token limits are fixed at startup; request conformance tests compare the actual upstream body with the application's priced request. The resource uses one bounded native HTTP attempt without redirects, inherited proxies or automatic retries. It retains parsed native success/error evidence, request references and Retry-After data, redacts reflected credentials and reports unknown transport/capture outcomes without claiming zero cost. Managed secrets are passed explicitly to the selected child outside bootstrap JSON and consumed from its environment before serving; names cannot override process/import configuration and values are omitted from representations. Tests exercise invalid profiles, readiness mismatch, capture limits, timeout/cancellation and stream cleanup. A real LLMCall process and real model-resource process complete through the platform gateway to a local simulated HTTP provider; known cost is settled once. Provider failure retains the obligation, and Stop during an actual upstream request reaps both processes while retaining uncertain cost. These initial tests use development installations and synthetic credentials. The installed checks below add isolated production environments; no live account request was made.

`make components` now prepares all four targets independently, retaining exact production locks and an explicit bundle of resolution IDs. GroundedReview's installed class ancestry and declared base dependency are inspected in its own environment; its package has a managed executable entry point. `InstalledProcess` checks the admitted type and retains the resolution snapshot, verifies it before launching the registered interpreter/module, and verifies installed contents after cleanup. Offline tests reject changed files, changed records and a mismatched type; they control the transport boundary rather than claiming to exercise the installed MCP host. Additional repeatable checks in `backend/tests/installed/check_bundle.py` ran against the four actual prepared environments: the controller scheduled work, LLMCall and GroundedReview each completed through the gateway and independent OpenAI resource to a local provider fixture, exactly one charge settled in each run, all processes exited cleanly and the environments remained unchanged. The three package checks require an explicitly selected bundle and make no paid request. They are separate from the default test count and complemented by the complete graph checks below.

`InstalledGraphCompiler` now validates descriptors and obtains effective contracts from the registered classes in their verified isolated interpreters, without provider clients, credentials or invocation grants. It retains installation/configuration/schema snapshots and checks resource operation requirements. `InstalledGraphEnvironment` validates trusted bindings and billing, materializes private bootstrap directories, rejects changed installation records and starts the compiled participants through the managed process fleet. Default tests cover malformed descriptions, deadlines, configuration/permission mismatches, unsupported MCP aliases, missing or duplicate pricing, immutable bootstrap content and changed installations before launch. The model descriptor now preserves native request/response/error envelopes.

Seven additional installed checks passed against a freshly prepared bundle: three package checks and four complete bundled graphs in `backend/tests/installed/check_graphs.py`. Each graph used actual isolated controller, agent and model-resource processes through the native gateway and a local simulated HTTP provider. Checks verified the managed call count, one settlement per model request in all three budget scopes, no outstanding obligations and clean process exit. Trusted provider/limit bindings were supplied by the test harness; this does not establish production operator admission or UI execution.

`SqliteOperatorStore` now persists saved sessions, immutable execution configurations, Start/Stop receipts and withdrawal tombstones. T1 rechecks the selected configuration, saved session, UTC admission time and single-run/cleanup gate, then atomically creates the run, snapshot, scopes, receipt and event. Concurrency tests admit at most one run; repeated/conflicting and rejected intentions never become new work. Stop preserves the first cause, and withdrawal serializes against late Start requests. Injected write failures roll back session, Start, Stop and withdrawal effects. Configuration changes retain obligations, reject insufficient caps and leave admitted run limits frozen. Migration tests preserve legacy runs and accounting with a verified backup.

The four installed graph checks were rerun through the new session/command admission path and passed, preserving the expected provider calls, settled costs and clean process exit. Their trusted configuration and runtime owner are composed by the test harness.

`ExecutionCoordinator` now owns pending command tasks independently of cancelled HTTP waiters, resolves durable receipts before preparation, checks prepared runtime identities and launches each newly accepted run once. Separate bounded groups of pending Start/control commands retain Stop capacity during preparation. Preparation and shutdown are time-bounded; cancelled tasks remain tracked until they finish. Tests exercise duplicate/conflicting commands, lost waiters, removed-installation replay, withdrawal during preparation, shutdown during T1, unresponsive preparation, expired admitted deadlines, recording failures and actual MCP process cleanup. Runtime model routing now accepts the native-service interface supplied by the coordinator and rejects stale or foreign grants.

Five additional checks in `backend/tests/installed/check_coordinator.py` passed: all four installed example graphs completed through production resource preparation, the coordinator and native gateway with their expected costs; a fifth run was stopped during its simulated upstream request, all runtime owners finished, and outstanding cost remained reserved. Production provider credentials and paid calls were not used. The existing installed package and graph checks remain separate from the default suite.

`InstalledWorkflowPreparer` now validates explicit installation/provider selections, resolves registered host adapters, compiles effective contracts and freezes installation/tariff evidence without storing credentials. Tests cover stale/mismatched prices, renewed validation of unchanged tariffs, admission-time expiry, renamed resources, invalid settings, bounded snapshots and cancellation retaining metadata-task ownership.

`create_app` now accepts trusted `ExecutionSetup` and composes the coordinator, preparation, native gateway and authenticated operator routes under its database lease. HTTP tests exercise session creation, Start/Stop/withdrawal, receipt replay, cancelled waiters, origin/host/credential rejection, strict bounded JSON, safe diagnostics and distinct model authority. State/history reads use consistent transactions, exact money, backend continuity, complete ETags and signed bounded cursors; tests verify shared-balance changes without run events and that inspection leaves cleanup flags unchanged. Startup/shutdown tests verify activation, failed-startup lease release and retained ownership on incomplete shutdown.

Five additional `backend/tests/installed/check_operator.py` checks passed through the actual application over loopback HTTP: all four installed graphs completed, and Stop interrupted a fifth request while preserving outstanding cost. These checks use production application composition, preparation, independent components and synthetic credentials; all provider calls go to a local fixture. The five checks were rerun with trace inspection enabled: they verified parent/child identities, node correlation, one charged attempt per model request, retained arguments/responses without the synthetic credential, and outstanding cost after Stop.

`configured_app` now loads an explicit bounded JSON startup configuration, with paths relative to its file and environment references for credentials. Invalid configuration prevents startup. The supplied template requires real prepared resolution identities and a reviewed expiry before execution. Browser controls retain unresolved command identities across reloads without persisting credentials or prompts. Tests cover lost replies, explicit same-command retry, withdrawal, unavailable local storage, stale reads, pagination, result errors and operator disconnection. The result route only exposes a recorded successful final output. Browser tests use simulated operations; the separate installed checks above cover independent component execution.

The inspector now exposes bounded event pages, causal call/attempt metadata, receipt pages and run-scoped retained payloads through authenticated HTTP reads. Twenty-five new backend cases cover fixed event boundaries while evidence arrives, foreign/invalid cursors, run isolation, authority, late responses, explicit unavailable usage, present JSON null, uncertain costs and oversized representations. Browser and frontend cases follow event-to-call and parent links, view arguments/responses/usage, page/refresh evidence, escape captured text and discard late reads after closing. These reads do not mutate execution or accounting.

Activation inspection now follows each stored root invocation, pages its related calls and links its actual arguments and eligible output. Thirteen new backend cases cover repeated use of one participant, binding references, absent legacy input, failed output eligibility, ambiguous roots/sources, pagination and cross-run isolation. The browser journey follows a call to its activation and published output. The five installed application checks passed again, verifying distinct activation identities and comparing every effective bound argument with its saved input or earlier response via the recorded JSON Pointer.

Per-attempt billing now selects the UTC month inside the reservation transaction and preserves that period during late settlement. Nineteen new integration cases cover month/year boundaries, leap February, shared totals, frozen and reduced caps, zero budgets, regressed/invalid clocks, rollback and inspection. Reservation events retain the UTC interval, admission time and policy revisions. Settlement overrun checks use the attempt’s original scopes.

Graph detail/input-schema routes, generic outgoing MCP mediation and full trace/diagnostic recording remain implementation work. CI workflow files are included for repository publication; remote execution and protections require separate verification. No paid model call was made.

## Completed checks

| Check                         | Method                                                                                                                                                                       | Result                                                                                                                                                                                                                                                               |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reference requirements        | Compare the seven TypeScript rule descriptions with the local reference README, excluding table padding and status labels.                                                   | 7/7 descriptions identical                                                                                                                                                                                                                                           |
| Architecture coverage         | Check numbered sections in the architecture overview and their linked content.                                                                                               | All 12 arc42 sections present                                                                                                                                                                                                                                        |
| Decision records              | Check status, context, drivers, options, outcome, consequences and confirmation.                                                                                             | 11 ADRs: 5 Accepted, 6 Proposed                                                                                                                                                                                                                                      |
| Contract schemas              | `jsonschema` 4.26.0, `Draft202012Validator.check_schema`; resolve package URNs through a local registry.                                                                     | 6 root schemas and 12 embedded operation/configuration schemas valid                                                                                                                                                                                                 |
| Review fixtures               | Validate manifests, bundled graphs and event; resolve graph bindings against illustrative outputs and separate run input, including effective instance input/output schemas. | 4 manifests, 4 graphs and 1 event accepted; eleven node input/output shapes checked                                                                                                                                                                                  |
| LLMCall fixtures              | Validate text/JSON configurations, derived-instance restrictions, success/error envelopes and the invalid-response examples.                                                 | 2 configurations, 1 derived instance and 4 result fixtures consistent; structured input accepted                                                                                                                                                                     |
| Python registration           | Check descriptor identities, base metadata and package requirement declarations; compare the package metadata excerpt.                                                       | 2 registration fixtures consistent; 6 sample versions have the documented exact-pin and bounded-range membership                                                                                                                                                     |
| Code specimens                | Parse fenced Python declarations/examples with `ast.parse` and the package excerpt with `tomllib`.                                                                           | 4 Python blocks and 1 TOML block syntactically valid; this check does not import SDKs, type-check or execute components                                                                                                                                              |
| Invalid variants              | Schema validation and temporary semantic checks against deliberately altered review fixtures.                                                                                | All 40 invalid cases rejected by the review harness                                                                                                                                                                                                                  |
| Diagrams                      | Parse Mermaid blocks with Mermaid 12.0.0.                                                                                                                                    | 2 C4 flowcharts, 1 runtime sequence diagram and 2 visual-model schematics accepted                                                                                                                                                                                   |
| Internal references           | Resolve relative Markdown links and heading fragments.                                                                                                                       | 43 Markdown documents; no broken local references                                                                                                                                                                                                                    |
| Accounting examples           | Exact decimal arithmetic and timestamp parsing of the proposed AP cases.                                                                                                     | 9 arithmetic/date checks passed; no concurrent admission, provider billing or database recovery executed                                                                                                                                                             |
| Provider reservation proposal | Decimal arithmetic from documented tariff/capacity values; compare category/output extremes against the proposed bound.                                                      | 3 example reserves and 36 endpoint comparisons consistent; settlement/release example checked. Does not establish provider billing compliance or an implemented admission guard.                                                                                     |
| README preservation           | Check current status, original-version attribution, dynamic-graph principle, mandatory engineering timing, and removal of the first-milestone section.                       | Preserved                                                                                                                                                                                                                                                            |
| SDK feasibility               | Temporary MCP subprocess/loopback probes, model HTTP mocks and exact dependency resolution.                                                                                  | Positive-path MCP transport/schema/metadata and client-shape checks passed; incompatible LangChain MCP adapter rejected. See the scoped [matrix](contracts/sdk-compatibility.md) and [captured evidence](evidence/sdk-review-20260928.json).                         |
| Packaging feasibility         | uv 0.12.17; offline synthetic wheel resolution/installation and subclass imports in separate Python environments.                                                            | Exact and old resolutions used B 1.1.0; explicit compatible update selected B 1.2.0 and excluded B 2.0.0. Conflicting constraints and an altered valid wheel were rejected. [Captured evidence](evidence/packaging-review-20260928.json); no platform loader tested. |

## Invalid cases exercised

Unsupported schema version; unknown core field; unavailable component version; missing resource slot; incompatible resource role; missing nested-call permission; unknown permitted operation; incorrect controller role; duplicate sequence node; missing sequence node; forward output reference; missing input pointer; invalid pointer escaping; literal binding without a value; incorrect resolved input type; invalid component configuration; missing billing declaration; component evidence masquerading as observed; unknown evidence class; parallel scheduling through the sequence profile.

LLMCall and registration cases add: JSON mode without a schema; text mode with a JSON schema; non-object activation input; unknown configuration field; reserved endpoint parameter; remote schema reference; invalid nested schema; a derived configuration changing its required output contract; malformed JSON; schema-invalid output; malformed issue pointer; wrong output mode; missing error issues; fenced JSON; trailing JSON value; duplicate key; non-finite constant; numeric overflow; malformed Python import path; registration/descriptor identity mismatch.

## Verification boundaries

Schema checks used standard JSON Schema validation. Cross-reference, ordering and strict JSON examples used a temporary review harness based on the documented semantic checklist, with illustrative outputs; no agent or provider was executed. Version membership checks used Python packaging requirement parsing, not an implemented dependency resolver. Syntax checks do not establish SDK behavior, static typing or subclass compatibility. Diagram parsing verifies syntax, not final UI rendering or usability. Internal link checks do not claim every external website was availability-tested.

Validation tools were installed only in temporary directories, not as project dependencies. The permanent verification command and CI configuration remain Q14 and must be established before application code. When that gate is implemented, retain these fixtures and negative cases as inputs to reproducible checks.

## Follow-up review: 2026-09-28

Reviewed the initial hosting proposal against the owner's requirement to add tools, memory and other resources soon. The component and installation contracts now distinguish process lifetime, resource sharing and durable data retention, and limit `generate` and the one-call algorithm to LLMCall. Requirements and Q05/Q17 record the starting-point qualification; Q22 tracks the first concrete extensions and QA22 defines their later acceptance scenario.

Reran the existing documentation harness after these prose changes: the schema/fixture checks, 40 invalid cases, README preservation and internal references passed. This confirms documentation consistency, not resource lifecycle behavior; no tool or memory implementation was added or executed.

Further work made host readiness/teardown, invocation authority and terminal-state races concrete proposals, with QA23–QA24 and CP01–CP07 acceptance cases. Reviewed these against the existing run, component and accounting contracts; no lifecycle or authorization implementation was tested. The question register retains their approval and wire-level gaps.

Rechecked official MCP revision and Python SDK release/mode documentation, and recorded a candidate in the [MCP profile](contracts/mcp-profile.md#sdk-candidate-and-conformance-work). After the owner selected inexpensive OpenAI access, reviewed official model and pricing documentation and recorded the [initial OpenAI profile](contracts/openai-initial-profile.md). At that documentary stage no SDK was installed and no provider/account request was made. The USD 0.0006 example is arithmetic using the stated ordinary input/output rates, not an observed charge or verified reservation bound.

The owner subsequently closed Q12: run, saved work-session and monthly budgets apply only to Slow Thinker II. Updated R23, the accounting contract, ADR 0006, QA17, K11 and the system-context view to remove the proposed original-executor integration. The existing documentation checks and all three Mermaid diagrams passed again. This verifies documentation consistency and diagram syntax; accounting isolation remains an implementation acceptance criterion.

Added the proposed accounting policy with AP01–AP10 and ADR 0011 with transaction boundaries T1–T5, crash recovery and stale-backup handling. Reviewed SQLite's official storage, transaction, durability and backup documentation; runtime settings remain untested. The documentation harness and three diagram parses passed; nine arithmetic/date checks read values directly from the worked examples. They do not test admission races, idempotent settlement or recovery. The owner selected local SQLite and the backend storage boundary; the detailed settings/recovery profile remains proposed. Currency/calendar and manual tariffs are still awaiting answers.

Added the observation proposal and QA26: core event families, payload provenance/capture statuses, optional internal reports, late-response handling and recording failures. Reviewed it against execution, accounting, visual and security contracts, separating one terminal call outcome from later receipt/settlement evidence. The document/link checks passed with 40 Markdown documents and 215 local references, and all three diagrams parsed after the SQLite selection. Per-event payload schemas and trace completeness remain unverified; no event producer or inspector was implemented.

Expanded the visual proposal with Structure/Execution schematics, stable participant/activation/call identities, selection and inspection rules, reflow and authoritative HTTP polling. The schematics were compared with the four bundled definitions and Mermaid parsing was expanded to cover all five diagrams. QA27 specifies UI journeys; syntax checks do not prove rendering, accessibility, latency or interaction behavior.

Prepared a source-layout and dependency-boundary proposal under Q14, preserving the public package names in the registration examples. QA28 specifies deliberate violations for directory placement and cross-module imports. These checks are obligations for implementation setup, not installed tooling; no backend/frontend/component source directories were created. The documentation harness was rerun for the updated links and unchanged contract fixtures.

Installed candidate SDKs only in a temporary environment and ran independent-process stdio, bounded loopback HTTP and model HTTP-mock probes. The SDK review records the actual discovery request needed in pinned mode, default capability declarations, successful metadata/client-shape checks, and the exact dependency conflict between MCP 2.2.0 and langchain-mcp-adapters 0.3.2. The incompatible adapter was removed and `pip check` passed after restoring MCP 2.2.0. No provider key or paid model call was used. Probe sources remained temporary; captured outputs, script digests and installed versions are retained as review evidence, not a permanent test suite or production lock.

A cross-contract review resolved the difference between configured instance, reused host process and temporary LLMCall implementation object. The constructor-bound client is now explicitly fresh per invocation, with bounded cleanup; future stateful resources retain their separate lifecycle. Aligned activation terminology and separated business-call bounds from protocol-traffic limits. QA24 now covers those distinctions. Clarified that specification decisions/acceptance criteria precede product tests, and corrected the arbitrary-control reference to deferred Q16. These are design corrections; no real component host was implemented or tested.

Reviewed current OpenAI request, error, cache and token-counting documentation. Expanded the initial provider proposal with an explicit request subset, native response preservation, LLMCall response checks, HTTP error categories and disjoint cache accounting. Identified a model-fixture limitation: text/usage alone loses native response semantics; Q13 now requires the proposed result revision. The short-context input bound remains unresolved because the documented counting endpoint accepts Responses input. These are documentary findings and acceptance cases; no further SDK or paid provider execution was performed.

Added the proposed operator API with durable command receipts, simultaneous-Start deduplication, explicit withdrawal of an unconfirmed intent and read-only recovery. Aligned T1, the visual interaction and QA27. Corrected projection freshness: run-event sequence alone cannot represent changes to shared budget fields. The proposal adds complete-view cache tokens and bounded snapshot paging; machine-readable wire schemas and executable browser/backend evidence remain open. JSON command/receipt examples were syntax-checked against their referenced graph identity, not against an implemented API schema.

Reviewed uv's official locking, workspace and installer documentation and exercised a temporary offline packaging probe. The installed uv candidate warns that pylock support is experimental, so the first installation proposal uses exact hashed requirements and wheels. An initial corruption sample was rejected as an invalid ZIP; the final integrity case instead changed valid wheel content and verified an explicit hash mismatch. Three isolated environments demonstrated retained and updated base versions with ordinary code inheritance; the original lock stayed unchanged. Sources/wheels/environments stayed temporary, and only results, sanitized command output, locks and hashes are retained as evidence. No application package or dependency setup was created.

Rechecked official model capacity, context-window semantics and pricing. Proposed an initial reservation using published capacity and maximum applicable Standard rates across both context bands, avoiding an unproven exact Chat Completions input counter. Checked three table amounts, 36 category/output endpoint comparisons and the settlement/release example with exact decimal arithmetic. The bound is conditional on the recorded provider specifications, not an invoice guarantee or live-provider verification. Its budget-utilization tradeoff has been submitted to the owner; currency/calendar and tariff policy remain separate decisions.

The owner selected automatic daily Vercel tariff imports on 2026-09-28, replacing the earlier manual-maintenance proposal and closing Q03. Aligned the accounting and OpenAI profiles with daily refresh, validated local revisions and unchanged running/historical execution prices. This records the approved behavior; no importer, scheduler or application runtime has been implemented.

## Historical outstanding items at the specification stage

The following paragraphs retain the pre-implementation checkpoint. Their claims
about missing first-cycle implementation and verification are historical, not the
current delivery status. The [first-cycle delivery](#first-cycle-delivery) and
subsequent dated sections record the implemented contracts and their evidence.
Standalone Python export remains future work.

The [question register](specification/open-questions.md) remains authoritative. Complete platform SDK conformance, authorization, real component package launch, persistence, concurrent budget accounting, cancellation races, production schemas and visual acceptance targets remain unverified. The limited SDK probes do not close those obligations.

The inheritance proposal includes a trusted Python registration schema, base metadata, a derived code specimen and a tested synthetic packaging mechanism. Platform resolution records, actual component installation/ancestry validation, host compatibility and descendant contract checks remain unimplemented and unverified under Q20. The probe's Python 3.13.0 runtime is not a selected production patch release.

The future Python export proposal is documentation only. Direct standalone execution, removal of platform logging/intermediation/supervision, preservation of functional graph logic and measured optimization are acceptance goals under Q21, not verified capabilities or benchmark results. Full equivalence with platform supervisory behavior is deliberately not an export goal.

The consolidated first-cycle baseline is approved; remaining implementation work is tracked separately from the historical design review.
